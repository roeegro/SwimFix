import sys

sys.path.append('../')
from routes import app


if __name__ == '__main__':
    # app.run(host='192.168.2.57', debug=True)
    # app.run(host='192.168.43.250', debug=False)
    app.run(host='localhost', debug=True)
