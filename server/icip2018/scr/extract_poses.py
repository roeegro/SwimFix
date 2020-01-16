import json
import os
import csv
import extract_angles as a

header = ['Name', 'Line', 'Frame',
          'Nose_x', 'Nose_y', 'Neck_x', 'Neck_y',
          'RShoulder_x', 'RShoulder_y', 'RElbow_x', 'RElbow_y', 'RWrist_x', 'RWrist_y',
          'LShoulder_x', 'LShoulder_y', 'LElbow_x', 'LElbow_y', 'LWrist_x', 'LWrist_y',
          'RKnee_x', 'RKnee_y', 'RAnkle_x', 'RAnkle_y',
          'LHip_x', 'LHip_y', 'LKnee_x', 'LKnee_y', 'LAnkle_x', 'LAnkle_y',
          'REye_x', 'REye_y', 'LEye_x', 'LEye_y', 'REar_x', 'REar_y', 'LEar_x', 'LEar_y', 'Bkg_x', 'Bkg_y',
          'R_Alpha', 'R_Beta', 'L_Alpha', 'L_Beta',
          'ManualLabel']


def output_train_dataset(input, output, threshold=0.1):
    professionals = ['Bobby', 'Brad', 'Danica', 'Sokratis', 'Keely', 'Leo', 'SaraH', 'Brittany', 'Pedrum'];
    novices = ['Hossein2', 'Michelle', 'Pieter', 'Cathaine', 'Jason', 'Danijel'];
    beginners = ['Dora1', 'Dora2', 'Hossein1', 'Irina', 'Dora', 'Robert', 'Keaton', 'Melanie', 'Setephanie'];

    f = open(output, "w")
    writer = csv.writer(f)
    writer.writerows([header])
    for swimmer in next(os.walk(input + '\.'))[1]:
        line = 1
        if swimmer in professionals:
            line = 3
        elif swimmer in novices:
            line = 5
        for pose in next(os.walk(input + swimmer + "\poses\."))[2]:
            frame_id = int(str.split(pose, '_')[1]);
            instances = extract_poses_by_file(swimmer, line, frame_id, None, input + swimmer + "\poses\\" + pose, threshold)
            writer.writerows(instances)


def output_test_dataset(input, swimmer, output, threshold=0.1):
    f = open(output, "w")
    writer = csv.writer(f)
    writer.writerows([header])
    for pose in next(os.walk(input))[2]:
        frame_id = int(str.split(pose, '_')[1]);
        instances = extract_poses_by_file(swimmer, None, frame_id, None, input + "\\" + pose, threshold)
        writer.writerows(instances)


def extract_poses_by_file(swimmer, line, frame_id, label, file, threshold=0.1):
    instances = []
    data = json.load(open(file))
    for people in data["people"]:
        poses = [swimmer, line, frame_id]
        pose_x = 0;
        pose_y = 0;
        conf = 0;
        for i, val in enumerate(people["pose_keypoints"]):
            if i % 3 == 0:
                pose_x = val;
            elif i % 3 == 1:
                pose_y = val;
            else:
                conf = val;
                if conf < threshold:
                    pose_x = 0;
                    pose_y = 0;
                    conf = 0;
                poses.append(pose_x)
                poses.append(pose_y)
                # poses.append(conf)
        if sum(poses[3:]) > 0:
            # print(poses)
            [r_alpha, r_beta] = a.extract_angles(shoulder=poses[4:5 + 1], elbow=poses[6:7 + 1], wrist=poses[8:9 + 1],
                                                 is_right=True)
            [l_alpha, l_beta] = a.extract_angles(shoulder=poses[10:11 + 1], elbow=poses[12:13 + 1],
                                                 wrist=poses[14:15 + 1], is_right=False)
            poses = poses + [r_alpha, r_beta]
            poses = poses + [l_alpha, l_beta]
            poses.append(label)
            instances.append(poses)
    return instances

    # output_train_dataset(input="D:\ComputerVision\\train_data_exp_1\\", output="D:\ComputerVision\\trainset_exp_1_0_1.csv")
    # output_test_dataset(input="D:\ComputerVision\\test_data\\", output="D:\ComputerVision\\testset.csv")
    # extract_poses_by_file('','','','','D:\ComputerVision\\train_data_exp_1\Bobby\poses\\frame_245_keypoints.json')
