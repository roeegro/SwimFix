import numpy as np
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
import pandas as pd
from sklearn.externals import joblib
import pickle as pkl
import sklearn.metrics as metrics

header = ['Name', 'Line', 'Frame',
          'Nose_x', 'Nose_y', 'Neck_x', 'Neck_y',
          'RShoulder_x', 'RShoulder_y', 'RElbow_x', 'RElbow_y', 'RWrist_x', 'RWrist_y',
          'LShoulder_x', 'LShoulder_y', 'LElbow_x', 'LElbow_y', 'LWrist_x', 'LWrist_y',
          'RKnee_x', 'RKnee_y', 'RAnkle_x', 'RAnkle_y',
          'LHip_x', 'LHip_y', 'LKnee_x', 'LKnee_y', 'LAnkle_x', 'LAnkle_y',
          'REye_x', 'REye_y', 'LEye_x', 'LEye_y', 'REar_x', 'REar_y', 'LEar_x', 'LEar_y', 'Bkg_x', 'Bkg_y',
          'R_Alpha', 'R_Beta', 'L_Alpha', 'L_Beta',
          'ManualLabel']


def train(training_set, output, feature_set="all_point", classifier='rf'):
    df = pd.read_csv(training_set, header=0)
    if feature_set == "arm_points":
        features = ['RShoulder_x', 'RShoulder_y', 'RElbow_x', 'RElbow_y', 'RWrist_x', 'RWrist_y','LShoulder_x', 'LShoulder_y', 'LElbow_x', 'LElbow_y', 'LWrist_x', 'LWrist_y']
    elif feature_set == "arm_angles":
        features = ['R_Alpha', 'R_Beta', 'L_Alpha', 'L_Beta']
    elif feature_set == "arm_points_angles":
        features = ['RShoulder_x', 'RShoulder_y', 'RElbow_x', 'RElbow_y', 'RWrist_x', 'RWrist_y','LShoulder_x', 'LShoulder_y', 'LElbow_x', 'LElbow_y', 'LWrist_x', 'LWrist_y','R_Alpha', 'R_Beta', 'L_Alpha', 'L_Beta']
    else:
        features = header[3:-1]

    if classifier == 'rf':
        clf = RandomForestClassifier(n_jobs=-1, random_state=2017)
    else:
        clf = LinearSVC(random_state=2017)

    df.fillna(value=0, inplace=True)
    clf.fit(df[features], df['ManualLabel'])
    # joblib.dump(clf, output)
    pkl.dump(clf, output)


def test(test_set, model, output, feature_set="all_point"):
    df = pd.read_csv(test_set, header=0)
    if feature_set == "arm_points":
        features = ['RShoulder_x', 'RShoulder_y', 'RElbow_x', 'RElbow_y', 'RWrist_x', 'RWrist_y', 'LShoulder_x',
                    'LShoulder_y', 'LElbow_x', 'LElbow_y', 'LWrist_x', 'LWrist_y']
    elif feature_set == "arm_angles":
        features = ['R_Alpha', 'R_Beta', 'L_Alpha', 'L_Beta']
    elif feature_set == "arm_points_angles":
        features = ['RShoulder_x', 'RShoulder_y', 'RElbow_x', 'RElbow_y', 'RWrist_x', 'RWrist_y', 'LShoulder_x',
                    'LShoulder_y', 'LElbow_x', 'LElbow_y', 'LWrist_x', 'LWrist_y', 'R_Alpha', 'R_Beta', 'L_Alpha',
                    'L_Beta']
    else:
        features = header[3:-1]

    df.fillna(value=0, inplace=True)
    clfLoad = pkl.load(model)
    pre = clfLoad.predict(df[features])
    df['PredictedValue'] = pre
    with open(output, 'w') as file:
        file.write("Name,Frame,PredictedValue\n")
        for i, value in enumerate(pre):
            file.write("{0},{1},{2}\n".format(df['Name'][i], df['Frame'][i], value))

    # swimmers = df.Name.unique()
    # filename = ("_hist.").join(output.rsplit('.', 1))
    # with open(filename, 'w') as file:
    #     file.write("Name,PredictedValue,Frequency\r\n")
    #     for swimmer in swimmers:
    #         swimmer_iloc = df.loc[df['Name'] == swimmer]
    #         swimmer_pred = swimmer_iloc[['Name', 'PredictedValue']]
    #         hist = plt.hist(swimmer_pred['PredictedValue'])
    #         for i in range(0, len(hist[0])):
    #             file.write("{0},{1},{2}\n".format(swimmer, hist[1][i], hist[0][i]))


def evaluate(training_set, feature_set="all_point", k=10, classifier='rf'):
    df = pd.read_csv(training_set, header=0)
    if feature_set == "arm_points":
        features = ['RShoulder_x', 'RShoulder_y', 'RElbow_x', 'RElbow_y', 'RWrist_x', 'RWrist_y', 'LShoulder_x',
                    'LShoulder_y', 'LElbow_x', 'LElbow_y', 'LWrist_x', 'LWrist_y']
    elif feature_set == "arm_angles":
        features = ['R_Alpha', 'R_Beta', 'L_Alpha', 'L_Beta']
    elif feature_set == "arm_points_angles":
        features = ['RShoulder_x', 'RShoulder_y', 'RElbow_x', 'RElbow_y', 'RWrist_x', 'RWrist_y', 'LShoulder_x',
                    'LShoulder_y', 'LElbow_x', 'LElbow_y', 'LWrist_x', 'LWrist_y', 'R_Alpha', 'R_Beta', 'L_Alpha',
                    'L_Beta']
    else:
        features = header[3:-1]
    df.fillna(value=0, inplace=True)
    if classifier == 'rf':
        clf = RandomForestClassifier(n_estimators=100, n_jobs=-1, random_state=2017)
    else:
        clf = LinearSVC(random_state=2017)

    #to be stratified k-fold
    X, y = df[features], df['ManualLabel']
    result = []
    for train_index, test_index in KFold(n_splits=k, random_state=2017).split(X, y):
        predicted = clf.fit(X.iloc[train_index], y.iloc[train_index]).predict(X.iloc[test_index])
        p, r, f, s = metrics.precision_recall_fscore_support(y.iloc[test_index], predicted, average='weighted')
        a = metrics.accuracy_score(y.iloc[test_index], predicted)
        result.append([p,r,f,a])
    print(np.mean(a=np.asarray(result), axis=0))


