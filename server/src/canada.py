import extract_frames as f
import extract_poses as p
import classifier as clf
import os
import warnings
warnings.filterwarnings("ignore")


# Steps to train classifier to learn pulling classifier c:
# The dataset should include one folder for each swimmer with the video (*.MOV) inside.
# The name of the swimmer folder and video file should be the same!
def train(dataset_folder, open_pose_path):
    # 1. Extract the frames from the given videos of swimmers
    # f.extract_frames_by_folder(dataset_folder)

    # 2. (LOOP) For each swimmer,
    for swimmer in next(os.walk(dataset_folder + '\.'))[1]:
        # 2.1. Input the frames to the openpose demo application
        os.system(open_pose_path + " "
                  "--image_dir " + dataset_folder + swimmer + "\\frames "
        		  "--write_keypoint_json " + dataset_folder + swimmer + "\\poses "
                  "--write_images " + dataset_folder + swimmer + "\\images "
        		  "--net_resolution \"1312x736\" "
                  "--scale_number 4 "
                  "--scale_gap 0.25")

    # 2.2. Extract the poses (x,y) positions from the frames
    # p.output_train_dataset(input=dataset_folder, output=dataset_folder + "data.csv")

    # 2.3. To do manual labeling, override the 'ManualLabel' column in the output file manually

    # 3. Train classifier on the labeled dataset and save it
    clf.train(training_set=dataset_folder + "data.csv", output=dataset_folder + "rf_arm_points_angles.pkl", feature_set="arm_points_angles", classifier='rf')
    clf.train(training_set=dataset_folder + "data.csv", output=dataset_folder + "rf_arm_points.pkl", feature_set="arm_points", classifier='rf')
    clf.train(training_set=dataset_folder + "data.csv", output=dataset_folder + "rf_arm_angles.pkl", feature_set="arm_angles", classifier='rf')
    clf.train(training_set=dataset_folder + "data.csv", output=dataset_folder + "rf_all_point.pkl", feature_set="all_point", classifier='rf')

    clf.train(training_set=dataset_folder + "data.csv",output=dataset_folder + "svm_arm_points_angles.pkl", feature_set="arm_points_angles", classifier='svm')
    clf.train(training_set=dataset_folder + "data.csv", output=dataset_folder + "svm_arm_points.pkl", feature_set="arm_points", classifier='svm')
    clf.train(training_set=dataset_folder + "data.csv", output=dataset_folder + "svm_arm_angles.pkl", feature_set="arm_angles", classifier='svm')
    clf.train(training_set=dataset_folder + "data.csv", output=dataset_folder + "svm_all_point.pkl", feature_set="all_point", classifier='svm')


# Steps to predict the pulling pose of new frames of a sample swimmer
def predict(swimmer_video, open_pose_path, model_folder,*path_for_csv):
    # 1. Extract the frames from the given video
    # f.extract_frames_by_file(file=swimmer_video, output=os.path.dirname(swimmer_video))

    # 2. Input the frames to the openpose demo application
    os.system(open_pose_path + " "
              "--image_dir " + os.path.dirname(swimmer_video) + "\\frames "
              "--write_keypoint_json " + os.path.dirname(swimmer_video) + "\\poses "
              "--write_images " + os.path.dirname(swimmer_video) + "\\images "
              "--net_resolution \"1312x736\" "
              "--scale_number 4 "
              "--scale_gap 0.25")

    # # 3. Extract the poses (x,y) positions from the frames
    # filename_w_ext = os.path.basename(swimmer_video)
    # swimmer, file_extension = os.path.splitext(filename_w_ext)
    # p.output_test_dataset(input=os.path.dirname(swimmer_video) + "\\poses", swimmer=swimmer, output=os.path.dirname(swimmer_video) + "\data.csv")

    print("The path is ".format(path_for_csv))
    # 4. Predict the frame's pulling pose
    clf.test(test_set=os.path.dirname(path_for_csv[0]) + "\data.csv", model=model_folder + "rf_arm_points_angles.pkl", output=os.path.dirname(path_for_csv[0]) + "\predict_rf_arm_points_angles.csv", feature_set="arm_points_angles")
    clf.test(test_set=os.path.dirname(path_for_csv) + "\data.csv", model=model_folder + "rf_arm_points.pkl", output=os.path.dirname(path_for_csv) + "\predict_rf_arm_points.csv", feature_set="arm_points")
    clf.test(test_set=os.path.dirname(path_for_csv) + "\data.csv", model=model_folder + "rf_arm_angles.pkl", output=os.path.dirname(path_for_csv) + "\predict_rf_arm_angles.csv", feature_set="arm_angles")
    clf.test(test_set=os.path.dirname(path_for_csv) + "\data.csv", model=model_folder + "rf_all_point.pkl", output=os.path.dirname(path_for_csv) + "\predict_rf_all_point.csv", feature_set="all_points")
    clf.test(test_set=os.path.dirname(path_for_csv) + "\data.csv", model=model_folder + "svm_arm_points_angles.pkl", output=os.path.dirname(path_for_csv) + "\predict_svm_arm_points_angles.csv", feature_set="arm_points_angles")
    clf.test(test_set=os.path.dirname(path_for_csv) + "\data.csv", model=model_folder + "svm_arm_points.pkl", output=os.path.dirname(path_for_csv) + "\predict_svm_arm_points.csv", feature_set="arm_points")
    clf.test(test_set=os.path.dirname(path_for_csv) + "\data.csv", model=model_folder + "svm_arm_angles.pkl", output=os.path.dirname(path_for_csv) + "\predict_svm_arm_angles.csv", feature_set="arm_angles")
    clf.test(test_set=os.path.dirname(path_for_csv) + "\data.csv", model=model_folder + "svm_all_point.pkl", output=os.path.dirname(path_for_csv) + "\predict_svm_all_point.csv", feature_set="all_points")


if __name__ == '__main__':
    dataset_folder="..\dataset\swimmers\\"
    train(dataset_folder=dataset_folder, open_pose_path="..\openpose\\build\\x64\Release\\OpenPoseDemo.exe")
    predict(swimmer_video="..\dataset\swimmers\Hossein2\Hossein2.MOV", open_pose_path="..\openpose\\build\\x64\Release\\OpenPoseDemo.exe", model_folder=dataset_folder)

    # models stratified-k-fold-x-val evaluations
    clf.evaluate(training_set=dataset_folder + "data.csv", feature_set="arm_points_angles", classifier='rf')
    clf.evaluate(training_set=dataset_folder + "data.csv", feature_set="arm_points", classifier='rf')
    clf.evaluate(training_set=dataset_folder + "data.csv", feature_set="arm_angles", classifier='rf')
    clf.evaluate(training_set=dataset_folder + "data.csv", feature_set="all_points", classifier='rf')
    clf.evaluate(training_set=dataset_folder + "data.csv", feature_set="arm_points_angles", classifier='svm')
    clf.evaluate(training_set=dataset_folder + "data.csv", feature_set="arm_points", classifier='svm')
    clf.evaluate(training_set=dataset_folder + "data.csv", feature_set="arm_angles", classifier='svm')
    clf.evaluate(training_set=dataset_folder + "data.csv", feature_set="all_points", classifier='svm')

    pass