import pickle
from typing import Dict, Any
import gzip
from six.moves import cPickle


def main():
    """ Main program """
    # Code goes over here.
    pkl = 'rf_arm_angles.pkl'
    with open(pkl, 'rb') as f:
        print(f)
        datadict = cPickle.load(f, encoding='latin1')
        f.close()
    print(datadict)
    return 0


if __name__ == "__main__":
    main()