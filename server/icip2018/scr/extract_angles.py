# http://mathworld.wolfram.com/Two-PointForm.html
# http://www.tpub.com/math2/5.htm
# alpha: angle between the uppper arm and the water surface
# 1. y_1 = m_1 x + b_1; The line passing the shoulder and elbow
# 2. y_2 = b_2; The water surface line as the average of the non zero y positions of (Nose, Neck, Eyes, Ears)
# 3. Angle between y_1 and y_2
# 3.1. if m_1 < 0 then abs(arctan(m_1))
# 3.2. else 180-arctan(m_1)

# beta: angle between the upper arm and the forearm
# 1. y_1 = m_1 x + b_1; The line passing the shoulder and elbow
# 2. y_2 = m_2 x + b_2; the line passing the elbow and the wrist
# 3. Angle between y_1 and y_2
# 3.1. if m_1 < 0 and m_2 > 0 then beta = arctan((m_2 - m_1)/(1 + m_1 * m_2)) => if beta < 0 then beta = 180 - abs(beta)
# 3.2. else if m_1 > 0 and m_2 > 0 then beta = 180 - arctan((m_2 - m_1)/(1 + m_1 * m_2))
# 3.3. else impossible

import numpy as np
import sys

pose_header = ['Nose_x', 'Nose_y', 'Neck_x', 'Neck_y',
               'RShoulder_x', 'RShoulder_y', 'RElbow_x', 'RElbow_y', 'RWrist_x', 'RWrist_y',
               'LShoulder_x', 'LShoulder_y', 'LElbow_x', 'LElbow_y', 'LWrist_x', 'LWrist_y',
               'RKnee_x', 'RKnee_y', 'RAnkle_x', 'RAnkle_y',
               'LHip_x', 'LHip_y', 'LKnee_x', 'LKnee_y', 'LAnkle_x', 'LAnkle_y',
               'REye_x', 'REye_y', 'LEye_x', 'LEye_y', 'REar_x', 'REar_y', 'LEar_x', 'LEar_y', 'Bkg_x', 'Bkg_y']


def extract_angles(shoulder, elbow, wrist, is_right):
    # print shoulder
    # print elbow
    # print wrist

    alpha = None
    beta = None

    shoulder = np.asarray(shoulder).astype(float)
    elbow = np.asarray(elbow).astype(float)
    wrist = np.asarray(wrist).astype(float)

    hand = shoulder + elbow + wrist
    if len(hand) - np.count_nonzero(hand) > 0:
        return alpha, beta
    try:
        if (shoulder[0] - elbow[0]) != 0:
            m_1 = -(shoulder[1] - elbow[1]) / (
                    shoulder[0] - elbow[0])  # image's Y axis is in reverse direction => (-1)*y
            alpha = abs(np.arctan(m_1))
            if (is_right and m_1 < 0) or (not is_right and m_1 > 0):
                if (is_right and elbow[0] > shoulder[0]) or (not is_right and elbow[0] < shoulder[0]):
                    alpha = np.pi - alpha
                else:
                    alpha = - alpha
        else:
            m_1 = np.inf
            alpha = np.pi / 2

        if (elbow[0] - wrist[0]) != 0:
            m_2 = -(elbow[1] - wrist[1]) / (elbow[0] - wrist[0])
        else:
            m_2 = np.inf

        if m_1 == m_2:
            beta = np.pi
        elif m_2 == np.inf:
            if m_1 != 0:
                beta = abs(np.arctan(1 / m_1))
                if (is_right and m_1 > 0) or (not is_right and m_1 < 0):
                    beta = np.pi - beta
            else:
                beta = np.pi / 2
        else:
            if (1 + m_1 * m_2) != 0:
                if m_1 < m_2:
                    beta = np.arctan((m_2 - m_1) / (1 + m_1 * m_2))
                else:
                    beta = np.arctan((m_1 - m_2) / (1 + m_1 * m_2))
            else:
                beta = np.pi / 2

                # b_2 = np.array(all but shoulde, elbow, and wrist);
                # b_2[b_2.nonzero()].mean()


    except:
        # print "Unexpected error:", sys.exc_info()[0]
        print('')
    # radian to degree
    if alpha is not None:
        alpha = alpha * (180 / np.pi)
    if beta is not None:
        beta = beta * (180 / np.pi)
    return alpha, beta

    # sample poses for Bobby in frame#770 left hand
    # poses = [[859.921,583.249,865.836,539.115,753.971,509.727,0,0,0,0,977.751,553.924,1048.32,733.379,945.311,868.77,0,0,0,0,0,0,0,0,0,0,0,0,836.369,553.893,883.426,550.852,789.242,509.783,924.593,509.735]]

    # sample poses for Bobby in frame#740 right hand
    # poses = [[0,0,32.7568,556.804,62.3601,553.894,0,0,0,0,7.80366,565.563,7.81458,618.587,0,0,82.8584,680.353,97.6243,786.204,100.583,883.535,18.1317,689.226,32.9732,789.264,59.4055,892.296,0,0,0,0,35.9031,521.499,7.79262,527.404],
    # [927.576,568.595,895.266,518.477,824.599,530.387,739.106,680.387,768.754,830.527,960.043,503.792,0,0,0,0,0,0,0,0,0,0,930.508,600.932,0,0,0,0,907.088,550.971,942.292,550.805,883.595,527.429,968.851,515.563],
    # [0,0,762.811,97.6738,762.883,97.6517,0,0,0,0,0,0,0,0,0,0,762.906,156.534,765.716,200.75,786.37,250.768,762.831,156.478,765.648,203.557,789.2,250.78,765.648,77.0094,0,0,762.978,77.0225,0,0]]

    # #test case for alpha: image 1000*500
    # poses = [[0, 0, 0, 0, 500, 250, 318, 209, 260, 360,   500, 250, 675, 210, 730, 340, 0, 0, 0],
    #          [0, 0, 0, 0, 500, 250, 318, 250, 260, 360,   500, 250, 675, 250, 730, 340, 0, 0, 0],
    #          [0, 0, 0, 0, 500, 250, 318, 300, 260, 360,   500, 250, 675, 300, 730, 340, 0, 0, 0],
    #          [0, 0, 0, 0, 500, 250, 500, 300, 260, 360,   500, 250, 500, 300, 730, 340, 0, 0, 0],
    #          [0, 0, 0, 0, 500, 250, 530, 300, 260, 360,   500, 250, 470, 300, 730, 340, 0, 0, 0]]
    #
    # #test case for beta:
    # poses = [[0, 0, 0, 0, 500, 250, 318, 209, 318, 360,   500, 250, 675, 210, 675, 340, 0, 0, 0],
    #          [0, 0, 0, 0, 500, 250, 318, 250, 318, 360,   500, 250, 675, 250, 675, 340, 0, 0, 0],
    #          [0, 0, 0, 0, 500, 250, 318, 300, 260, 360,   500, 250, 675, 300, 730, 340, 0, 0, 0],
    #          [0, 0, 0, 0, 500, 250, 500, 300, 260, 360,   500, 250, 500, 300, 730, 340, 0, 0, 0],
    #          [0, 0, 0, 0, 500, 250, 530, 300, 260, 360,   500, 250, 470, 300, 730, 340, 0, 0, 0]]
    #
    #
    # #poses = []
    # for pose in poses:
    #     [r_alpha, r_beta] = extract_angles(shoulder=pose[4:5+1], elbow=pose[6:7+1], wrist=pose[8:9+1], is_right=True)
    #     [l_alpha, l_beta] = extract_angles(shoulder=pose[10:11+1], elbow=pose[12:13+1], wrist=pose[14:15+1], is_right=False)
    #     print r_alpha,r_beta,l_alpha,l_beta
