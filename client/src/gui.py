from flask import *
import os
import preprocessor
from shutil import copyfile
from waitress import serve
import shutil
from socket import *

# from werkzeug import secure_filename

app = Flask(__name__)

# searchword = request.args.get('q', '')

# UPLOAD_FOLDER = '/code/flask-test/upload_files'
UPLOAD_FOLDER = 'uploaded_files'

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'MOV', 'mp4'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CHUNKSIZE = 1_000_000


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def send_file_to_server(video_path, filename):
    sock = socket()  # Create a socket object
    host = '132.72.96.31'
    port = 12345  # Reserve a port for your service.
    sock.connect((host, port))

    with sock, open(video_path, 'rb') as f:
        sock.sendall(filename.encode() + b'\n')
        sock.sendall(f'{os.path.getsize(video_path)}'.encode() + b'\n')
        # Send the file in chunks so large files can be handled.
        while True:
            data = f.read(CHUNKSIZE)
            if not data:
                break
            sock.sendall(data)
        f.close()
        print("Done Sending")
        sock.shutdown(SHUT_WR)
        print(sock.recv(1024).decode())
        sock.close()


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            if not os.path.exists('partial_movies'):
                os.mkdir('partial_movies')
            if not os.path.exists(UPLOAD_FOLDER):
                os.mkdir(UPLOAD_FOLDER)
            # filename = secure_filename(file.filename)
            filename = file.filename
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(video_path)
            video_name = preprocessor.video_cutter(video_path)
            # send_file_to_server("partial_movies/" + video_name + ".mp4",  video_name + ".mp4")
            send_file_to_server("uploaded_files/" + video_name + ".MOV", video_name + ".MOV")
            return redirect(url_for('upload_file'))
        else:
            return '''
            <!doctype html>
            <title>Upload new File</title>
            <h1>File Select Error!</h1>
            <a href="/file">file</a>
            '''
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


if __name__ == "__main__":
    app.run(debug=True)
    # serve(app)
