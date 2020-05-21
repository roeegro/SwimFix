import json
import shutil
import os


# We assume the openpose training and cooc-annotator repositories
# are located at the same level with the client, server, utils dirs
openpose_train_path = "../openpose_train/"
annotator_path = "../coco-annotator/"
coco_skeleton = [[16, 14], [14, 12], [17, 15], [15, 13], [12, 13], [6, 12], [7, 13], [6, 7], [6, 8], [7, 9], [8, 10], [9, 11], [2, 3], [1, 2], [1, 3], [2, 4], [3, 5], [4, 6], [5, 7]]

'''
Iterate over all the key value pairs in dictionary and call the given
callback function() on each pair. Items for which callback() returns True,
add them to the new dictionary. In the end return the new dictionary.
'''


def filter_dict(dictObj, callback):
    new_dict = dict()
    # Iterate over all the items in dictionary
    for (key, value) in dictObj.items():
        # Check if item satisfies the given condition then add to new dict
        if callback((key, value)):
            new_dict[key] = value
    return new_dict


def json_field_len(json_path, field_name):
    with open(json_path, 'r+') as f:
        parsed = json.load(f)
        field = parsed[field_name]
        print(len(field))


def diff(first, second):
        second = set(second)
        return [item for item in first if item not in second]


def filter_json(json_path, filters, out_path=None):
    if out_path is None:
        out_path = json_path
    with open(json_path, 'r+') as f:
        parsed = json.load(f)
    imgs = parsed['images']
    annots = parsed['annotations']
    filtered_imgs = [filter_dict(img, lambda elem: elem[0] in filters) for img in imgs]
    filtered_annots = [filter_dict(annot, lambda elem: elem[0] in filters) for annot in annots]
    annos_to_rem = []
    imgs_to_rem = []
    for anno in filtered_annots:
        try:
            anno['keypoints']
        except Exception as e:
            imgs_to_rem.append(anno['image_id'])
            annos_to_rem.append(anno)
    filtered_imgs = list(filter(lambda img: img['id'] not in imgs_to_rem, filtered_imgs))
    parsed['images'] = filtered_imgs
    parsed['annotations'] = list(filter(lambda annot: annot not in annos_to_rem, filtered_annots))
    parsed['categories'][0]['skeleton'] = coco_skeleton
    with open(out_path, 'w') as f:
        json.dump(parsed, f)


def add_imgs_to_train_dataset(coco_json_path, dataset_dir):
    with open(coco_json_path, 'r') as f:
        parsed = json.load(f)
        imgs = parsed['images']
        # parsed['images']
        new_imgs = [copy_rename_img(img, dataset_dir) for img in imgs]
        parsed['images'] = new_imgs
    with open(coco_json_path, 'w') as f:
        json.dump(parsed, f)


def copy_rename_img(img, dst_path):
    # print(img)
    img_id = img['id']
    img['file_name'] = '%012d' % img_id + ".jpg"
    new_path = dst_path + "/" + img['file_name']
    old_path = annotator_path + img['path']
    img['path'] = new_path
    shutil.copy(old_path, new_path)
    # print(img)
    return img


if __name__ == '__main__':
    openpose_train_annots_path = openpose_train_path + "dataset/COCO/cocoapi/annotations/"
    openpose_train_raziel_dataset_path = openpose_train_path + "dataset/COCO/cocoapi/images/coco"
    if not os.path.exists(openpose_train_raziel_dataset_path):
        os.mkdir(openpose_train_raziel_dataset_path)

    # annotator_dataset_path = openpose_train_path + "datasets/Raziel Dataset"

    filtered_json_path = openpose_train_annots_path + "person_keypoints_raziel.json"
    filter_json(openpose_train_annots_path + "Raziel Dataset.json",
                ['height', 'width', 'id', 'path', 'image_id', 'segmentation', 'bbox', 'keypoints',
                 "annotated", "file_name", "num_keypoints", "area", "iscrowd", "category_id"],
                filtered_json_path)
    #
    add_imgs_to_train_dataset(filtered_json_path, openpose_train_raziel_dataset_path)

    json_field_len(filtered_json_path, "images")
    json_field_len(filtered_json_path, "annotations")
