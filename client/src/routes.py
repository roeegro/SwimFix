from flask_login import login_user, logout_user, current_user

from gui_utils import upload_file, get_previous_feedbacks
from flask import render_template, url_for, flash, redirect, request
from forms import RegistrationForm, LoginForm
from client.src.models import User
from . import app, db, bcrypt

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


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm(request.form)

    if form.validate_on_submit():
        print(form.email.data)
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            print(2)
            login_user(user, remember=form.remember.data)
            print(3)
            return redirect(url_for('index'))
        else:
            print(4)
            flash('Login Unsuccessful. Please check username and password', 'danger')
    print(5)
    return render_template('login.html', title='Login', form=form)


@app.route('/previous-feedbacks', methods=['GET', 'POST'])
def previous_feedbacks(add_to_table=False):
    data_to_pass = get_previous_feedbacks()
    return render_template('previous-feedbacks.html', data=data_to_pass)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/tables", methods=['GET', 'POST'])
def tables():
    return render_template('tables.html')
