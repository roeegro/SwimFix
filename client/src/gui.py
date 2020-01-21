from flask import *
import os
import preprocessor
from shutil import copyfile
from waitress import serve

# from werkzeug import secure_filename

app = Flask(__name__)

# searchword = request.args.get('q', '')

# UPLOAD_FOLDER = '/code/flask-test/upload_files'
UPLOAD_FOLDER = 'uploaded_files'

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'MOV','mp4'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route("/")
def hello(name=None):
    return render_template('hello.html', name=name)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def send_file_to_server(video_path):
    copyfile(video_path, "../../server/videos/output.mp4")
    print("Sent file!")


@app.route('/file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            # filename = secure_filename(file.filename)
            filename = file.filename
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(video_path)
            preprocessor.video_cutter(video_path)
            send_file_to_server("partial_movies/output.mp4")
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


@app.route("/user/<username>")
def profile(username):
    return u"こんにちは！" + username + u"くん！"


if __name__ == "__main__":
    app.run(debug=True)
    # serve(app)
