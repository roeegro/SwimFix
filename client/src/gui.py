from flask import *
import os
import preprocessor
from shutil import copyfile
from waitress import serve
import shutil

# from werkzeug import secure_filename

app = Flask(__name__)

# searchword = request.args.get('q', '')

# UPLOAD_FOLDER = '/code/flask-test/upload_files'
UPLOAD_FOLDER = 'uploaded_files'

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'MOV', 'mp4'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def create_dir_if_not_exists(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)
        print('Created dir' + dir)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def send_file_to_server(video_path):
    video_name = video_path.split('/')[-1]
    # to create the output dir from the server
    create_dir_if_not_exists('output')
    create_dir_if_not_exists('../../server/videos/')
    copyfile(video_path, "../../server/videos/" + video_name)
    # os.remove(video_path)
    shutil.rmtree('partial_movies')
    print("Sent file!")


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
            new_video_paths = preprocessor.video_cutter(video_path)
            for new_video_path in new_video_paths:
                send_file_to_server(new_video_path)
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
    app.run(host='0.0.0.0', debug=True)
    # serve(app)
