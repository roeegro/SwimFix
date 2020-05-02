from gui_utils import upload_file
from flask import render_template, url_for, flash, redirect,request
from forms import RegistrationForm, LoginForm
from . import app

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'MOV', 'mp4'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html')


@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html')


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route("/load-video", methods=['GET', 'POST'])
def load_video():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            upload_file(app.config['UPLOAD_FOLDER'], file)
            flash('The file {} was uploaded successfully'.format(file.filename), 'success')
            return previous_feedbacks(add_to_table=True)
        else:
            flash('Failed to upload video file. Please try again', 'failure')
    return render_template('load-video.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@blog.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/previous-feedbacks', methods=['GET', 'POST'])
def previous_feedbacks(add_to_table=False):
    if add_to_table:
        return render_template('previous-feedbacks.html', data=[{'date': 1, 'zip': 2}])
    else:
        return render_template('previous-feedbacks.html')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/tables", methods=['GET', 'POST'])
def tables():
    return render_template('tables.html')
