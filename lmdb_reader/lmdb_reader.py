import os
import sys

cwd = os.getcwd()
print("cwd: ", cwd)
sCaffePythonPath = os.path.join('../openpose_caffe_train', 'python/')
sys.path.insert(0, sCaffePythonPath)

import caffe
import lmdb
import numpy as np
import matplotlib.pyplot as plt
import cv2

# N = 100
#
# # Let's pretend this is interesting data
# X = np.zeros((N, 3, 32, 32), dtype=np.uint8)
# y = np.arange(N)
# y = np.zeros(N)
#
# # We need to prepare the database for the size. We'll set it 10 times
# # greater than what we theoretically need. There is little drawback to
# # setting this too big. If you still run into problem after raising
# # this, you might want to try saving fewer entries in a single
# # transaction.
# map_size = X.nbytes * 100
# print(X.nbytes)
# lmdb_file = 'mylmdb2'
#
# env = lmdb.open(lmdb_file, map_size=map_size)
# #
# with env.begin(write=True) as txn:
#     # txn is a Transaction object
#     for i in range(N):
#         datum = caffe.proto.caffe_pb2.Datum()
#         datum.channels = X.shape[1]
#         datum.height = X.shape[2]
#         datum.width = X.shape[3]
#         datum.data = X[i].tobytes()  # or .tostring() if numpy < 1.9
#         datum.label = int(y[i])
#         str_id = '{:08}'.format(i)
#
#         # The encode is only essential in Python 3
#         txn.put(str_id.encode('ascii'), datum.SerializeToString())
#     print("done writing")
#
#     lmdb_cursor = txn.cursor()
#     datum = caffe.proto.caffe_pb2.Datum()
#     print("env info: ", env.info())
#     for key, value in lmdb_cursor:
#         datum.ParseFromString(value)
#         label = datum.label
#         data = caffe.io.datum_to_array(datum)
#         im = data.astype(np.uint8)
#         im = np.transpose(im, (2, 1, 0))  # original (dim, col, row)
#         print("label ", label, " key ", key, " value ", value)

# Wei Yang 2015-08-19
# Source
#   Read LevelDB/LMDB
#   ==================
#       http://research.beenfrog.com/code/2015/03/28/read-leveldb-lmdb-for-caffe-with-python.html
#   Plot image
#   ==================
#       http://www.pyimagesearch.com/2014/11/03/display-matplotlib-rgb-image/
#   Creating LMDB in python
#   ==================
#       http://deepdish.io/2015/04/28/creating-lmdb-in-python/

lmdb_file = "../openpose_train/dataset/lmdb_coco"
lmdb_env = lmdb.open(lmdb_file)
lmdb_txn = lmdb_env.begin()
lmdb_cursor = lmdb_txn.cursor()
datum = caffe.proto.caffe_pb2.Datum()
print("env info: ", lmdb_env.info())
for key, value in lmdb_cursor:
    datum.ParseFromString(value)
    label = datum.label
    data = caffe.io.datum_to_array(datum)
    im = data.astype(np.uint8)
    im = np.transpose(im, (2, 1, 0))  # original (dim, col, row)
    print("im shape ", im.shape, " key ", key)
    # img = cv2.cvtColor(im, cv2.COLOR_YCR_CB2BGR)
    # print(img.shape)
    # plt.imshow(img)
    # plt.show()


