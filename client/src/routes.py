from flask_login import login_user, logout_user, current_user
from gui_utils import upload_file, get_previous_feedbacks
from flask import render_template, url_for, flash, redirect, request, session
from forms import RegistrationForm, LoginForm
from client.src.models import User
from . import app, db, bcrypt, mysql

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


## Groiser's Login
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('index'))
#     form = LoginForm(request.form)
#
#     if form.validate_on_submit():
#         print(form.email.data)
#         user = User.query.filter_by(email=form.email.data).first()
#         if user and bcrypt.check_password_hash(user.password, form.password.data):
#             print(2)
#             login_user(user, remember=form.remember.data)
#             print(3)
#             return redirect(url_for('index'))
#         else:
#             print(4)
#             flash('Login Unsuccessful. Please check username and password', 'danger')
#     print(5)
#     return render_template('login.html', title='Login', form=form)


@app.route('/previous-feedbacks', methods=['GET', 'POST'])
def previous_feedbacks(add_to_table=False):
    data_to_pass = get_previous_feedbacks()
    return render_template('previous-feedbacks.html', data=data_to_pass)


## Groiser's register
# @app.route("/register", methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#         user = User(username=form.username.data, email=form.email.data, password=hashed_password)
#         db.session.add(user)
#         db.session.commit()
#         flash(f'Account created for {form.username.data}!', 'success')
#         return redirect(url_for('login'))
#     return render_template('register.html', title='Register', form=form)


# @app.route("/tables", methods=['GET', 'POST'])
# def tables():
#     return render_template('tables.html')


########Forum#######
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

    return render_template("forum.html", p=2, topics=topics, pinned=pinned, page=page, nextPageExists=nextPageExists)


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
                           page=page, nextPageExists=nextPageExists, isPinned=isPinned, isAdmin=session.get('isAdmin'))


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


# Panel
# @app.route("/panel")
# def panel():
#     if session.get('logged_in') == True:
#         cur = mysql.connection.cursor()
#         cur.execute("SELECT * FROM USERS WHERE USERNAME = %s", (session['username'],))
#         return render_template("panel.html", p=3, user=cur.fetchone())
#     return render_template("login2.html", p=3)


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
