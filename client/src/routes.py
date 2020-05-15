from flask_login import login_user, logout_user, current_user
from gui_utils import *
from flask import render_template, url_for, flash, redirect, request, session
from forms import RegistrationForm, LoginForm
from client.src.models import User
from test_generator import run
from . import app, db, bcrypt

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'MOV', 'mp4'])


def is_admin():
    return session.get('isAdmin') if session and session.get('logged_in') else False

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html',isAdmin=is_admin())


@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html',isAdmin=is_admin())


@app.route('/add-test', methods=['GET', 'POST'])
def add_test():
    try:
        run()
    finally:
        return redirect(url_for("admin_index"))


@app.route('/admin-index', methods=['GET', 'POST'])
def admin_index():
    if is_admin():
        return render_template('admin-index.html',isAdmin=is_admin())
    flash("You are not authorized to access this page", 'failure')
    return redirect(url_for('index'))


@app.route('/charts')
def charts():
    return render_template('charts.html',isAdmin=is_admin())


@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html',isAdmin=is_admin())


@app.route("/load-video", methods=['GET', 'POST'])
def load_video():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            upload_video_file(app.config['UPLOAD_FOLDER'], file)
            userID = session.get('ID') if session and session.get('logged_in') else 0
            upload_file_sql(file.filename.split('.')[0],userID)
            flash('The file {} was uploaded successfully'.format(file.filename), 'success')
            return previous_feedbacks()
        else:
            flash('Failed to upload video file. Please try again', 'failure')
    return render_template('load-video.html',isAdmin=is_admin())


def upload_file_sql(filename, user_id=0):
    cur = mysql.connection.cursor()
    cur.execute('''
        INSERT INTO FILES(NAME, CREATORID)
        VALUE (%s, %s)
        ''', (filename, user_id))
    mysql.connection.commit()
    cur.close()
    return


@app.route('/previous-feedbacks', methods=['GET', 'POST'])
def previous_feedbacks():
    user_id= session.get('ID') if session and session.get('logged_in') else 0
    data_to_pass = get_previous_feedbacks(user_id)
    return render_template('previous-feedbacks.html', data=data_to_pass,isAdmin=is_admin())


@app.route('/previous-feedback/<zip_name>', methods=['GET', 'POST'])
def previous_feedback(zip_name):
    csvs_dir, csvs_paths = get_all_csvs_paths(zip_name)
    data_to_pass = [{'path': path.replace('\\', '/')} for path in csvs_paths]  # for html format
    return render_template('previous-feedback.html', zip_name=zip_name, data=data_to_pass,isAdmin=is_admin())



# Forum
@app.route("/forum/<page>")
def forum(page):
    page = int(page)
    cur = mysql.connection.cursor()
    limit = 30
    offset = limit * page
    nextPageExists = False
    pinned = {}
    if page == 0:
        cur.execute('''
            SELECT TOPICS.ID, TOPICS.NAME, USERS.USERNAME AS 'CREATOR', Count(POSTS.ID) AS 'POSTS', MAX(POSTS.CREATION_DATE) AS 'LASTPOST'
            FROM TOPICS
            INNER JOIN USERS ON TOPICS.CREATORID = USERS.ID
            LEFT JOIN POSTS ON POSTS.TOPICID = TOPICS.ID
            WHERE TOPICS.ISPINNED = TRUE
            GROUP BY TOPICS.ID
            ORDER BY LASTPOST DESC;''')
        pinned = cur.fetchall()
    cur.execute('''
        SELECT TOPICS.ID, TOPICS.NAME, USERS.USERNAME AS 'CREATOR', Count(POSTS.ID) AS 'POSTS', MAX(POSTS.CREATION_DATE) AS 'LASTPOST'
        FROM TOPICS
        INNER JOIN USERS ON TOPICS.CREATORID = USERS.ID
        LEFT JOIN POSTS ON POSTS.TOPICID = TOPICS.ID
        WHERE TOPICS.ISPINNED = FALSE
        GROUP BY TOPICS.ID
        ORDER BY LASTPOST DESC
        LIMIT %s, %s''', (offset, limit + 1,))
    topics = cur.fetchall()

    if len(topics) > limit:
        nextPageExists = True
    topics = topics[:limit]

    if len(topics) == 0 and page != 0:
        return redirect("/forum/" + str(page - 1))

    return render_template("forum.html", p=2, topics=topics, pinned=pinned, page=page, nextPageExists=nextPageExists,isAdmin=is_admin())


@app.route("/forum/topic/<forumPage>/<topicID>/<page>")
def topic(forumPage, topicID, page):
    page = int(page)
    limit = 10
    nextPageExists = False
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT TOPICS.NAME, TOPICS.ISPINNED
        FROM TOPICS
        WHERE TOPICS.ID = %s;''', (topicID,))
    topic = cur.fetchone()
    if not topic:
        return redirect("/forum/" + forumPage)
    name = topic['NAME']
    isPinned = int(topic['ISPINNED'])
    cur.execute('''
        SELECT POSTS.ID, POSTS.CONTENT, POSTS.CREATION_DATE, USERS.USERNAME, USERS.ISADMIN
        FROM POSTS
        INNER JOIN USERS ON POSTS.CREATORID = USERS.ID
        WHERE POSTS.TOPICID = %s
        ORDER BY POSTS.CREATION_DATE
        LIMIT %s, %s;''', (topicID, page * limit, limit + 1))
    posts = cur.fetchall()
    if len(posts) > limit:
        nextPageExists = True
    if len(posts) == 0 and page != 0:
        return redirect("/forum/topic/" + forumPage + "/" + topicID + "/" + str(page - 1))
    posts = posts[:limit]
    return render_template("topic.html", p=2, posts=posts, name=name, topicID=topicID, forumPage=forumPage,
                           page=page, nextPageExists=nextPageExists, isPinned=isPinned, isAdmin=is_admin())


# Create post, topic

def createPostFunction(content, topicID, userID=0):
    cur = mysql.connection.cursor()
    cur.execute('''
        INSERT INTO POSTS(CONTENT, CREATORID, TOPICID)
        VALUE (%s, %s, %s)
        ''', (content, userID, topicID))
    mysql.connection.commit()
    cur.close()
    return


@app.route("/forum/createPost", methods=['POST'])
def createPost():
    content = request.form['content']
    topicID = request.form['topicID']
    page = request.form['page']
    # if not session.get('logged_in'):
    #     flash(u"You must be logged in!", "danger")
    if not content:
        flash(u"Post must contain content!", "danger")
    else:
        userID = session.get('ID') if session and session.get('logged_in') else 0
        createPostFunction(content, topicID, userID)
    return redirect("/forum/topic/0/" + topicID + "/" + page)


@app.route("/forum/createTopic", methods=['POST'])
def createTopic():
    content = request.form['content']
    title = request.form['title']
    userID = session.get('ID') if session and session.get('logged_in') else 0
    # if not userID or not session.get('logged_in'):
    #     flash(u"You must be logged in!", "danger")
    if not content or not title:
        flash(u"Topic must contain content and title!", "danger")
    else:
        cur = mysql.connection.cursor()
        cur.execute('''
            INSERT INTO TOPICS(NAME, CREATORID)
            VALUE (%s, %s)
            ''', (title, userID))
        mysql.connection.commit()
        topicID = cur.lastrowid
        cur.close()
        createPostFunction(content, topicID, userID)
        return redirect("/forum/topic/0/" + str(topicID) + "/0")
    return redirect("/forum")


# Login / Register / Logout scripts
@app.route('/', methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    # if session and session['logged_in']:
    #     print(session['logged_in'])
    #     return redirect(url_for('index'))

    form = LoginForm(request.form)
    if not form.validate_on_submit():
        return render_template('login.html', title='Login', form=form)

    _username = request.form['username']
    _passwd = request.form['password']

    cur = mysql.connection.cursor()
    res = cur.execute("SELECT * FROM USERS WHERE USERNAME = %s", (_username,))

    if res > 0:
        user = cur.fetchone()

        if bcrypt.check_password_hash(user['PASSWORD_HASH'], _passwd):
            session['ID'] = user['ID']
            session['username'] = user['USERNAME']
            session['logged_in'] = True
            session['isAdmin'] = (user['ISADMIN'] == 1)
            flash(u"You're now logged in!", "info")
            return redirect(url_for('index'))

    flash(u"Incorrect login", "danger")
    return redirect(url_for('login'))


@app.route("/register", methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    if not form.validate_on_submit():
        return render_template('register.html', title='Register', form=form)

    _username = form.username.data
    _passwd = request.form['password']
    _email = request.form['email']

    if len(_username) < 2 or len(_username) > 20:
        flash(u"Incorrect username lenght!", "danger")
        return redirect(url_for('panel'))

    cur = mysql.connection.cursor()
    res = cur.execute("SELECT * FROM USERS WHERE USERNAME = %s OR EMAIL = %s", (_username, _email))

    if res != 0:
        flash(u"User exists!", "danger")
        return redirect(url_for('panel'))

    passwordHash = bcrypt.generate_password_hash(_passwd).decode('utf-8')
    cur.execute("INSERT INTO USERS(USERNAME, EMAIL, PASSWORD_HASH) VALUES (%s, %s, %s)",
                (_username, _email, passwordHash))

    mysql.connection.commit()
    cur.close()
    flash(u"You're now registered!", "info")
    return redirect(url_for('login'))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route("/plug-and-play", methods=['POST', 'GET'])
def plug_and_play():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            success = upload_python_file(app.config['UPLOAD_FOLDER'], file)
            if success:
                flash('The file {} was uploaded successfully'.format(file.filename), 'success')
                return admin_index()
            else:
                flash('Failed to upload python file. Please try again', 'failure')
        else:
            flash('Failed to upload python file. Please try again', 'failure')
    return render_template('plug-and-play.html',isAdmin=is_admin())
