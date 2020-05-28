import pickle

from flask_login import login_user, logout_user, current_user
import socket
from gui_utils import *
from flask import render_template, url_for, flash, redirect, request, session
from forms import RegistrationForm, LoginForm
import _thread
import threading
from functools import reduce
from test_generator import run, success_sending_flag
from . import app, db, bcrypt, SERVER_IP, SERVER_PORT

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'MOV', 'mp4'])
IMG_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']


def is_admin():
    return session.get('isAdmin') if session else False


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html', isAdmin=is_admin())


@app.route('/forgot-password')
def forgot_password():
    return render_template('forgot-password.html', isAdmin=is_admin())


@app.route('/add-test', methods=['GET', 'POST'])
def add_test():
    add_test_thread = threading.Thread(target=run)
    add_test_thread.start()
    while add_test_thread.is_alive():
        time.sleep(5)

    if success_sending_flag:
        flash('The test files were uploaded successfully', 'success')
    else:
        flash('Failed to upload test files', 'info')
    return redirect(url_for("admin_index"))


@app.route('/admin-index', methods=['GET', 'POST'])
def admin_index():
    if is_admin() == 'True':
        return render_template('admin-index.html', isAdmin=is_admin())
    flash("You are not authorized to access this page", 'danger')
    return redirect(url_for('index'))


@app.route('/charts')
def charts():
    return render_template('charts.html', isAdmin=is_admin())


@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html', isAdmin=is_admin())


@app.route("/load-video", methods=['GET', 'POST'])
def load_video():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            print('full file is {} '.format(file.filename))
            videos_paths_to_upload = upload_video_file(app.config['UPLOAD_FOLDER'], file)
            userID = session.get('ID') if session and session.get('logged_in') else 0
            for video_path in videos_paths_to_upload:
                print(video_path)
                video_name = (video_path.split('/')[-1]).split('.')[0]  # no extension
                # to create the output dir from the server
                # create_dir_if_not_exists('output')
                # create_dir_if_not_exists('../../server/videos/')
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((SERVER_IP, SERVER_PORT))
                    msg = 'upload user_id: {} filename: {} '.format(userID, video_name)
                    print('UPLOAD {} '.format(msg))
                    s.sendall(msg.encode('utf-8'))
                    start_msg = s.recv(1024)  # for 'start' message
                    if start_msg.decode('utf-8') != 'start':
                        flash('Failed to upload video file. Please try again', 'failure')
                        return render_template('load-video.html', isAdmin=is_admin())
                    f = open(video_path, 'rb')
                    # send the file
                    l = f.read(1024)
                    while l:
                        s.send(l)
                        print("Sending data")
                        l = f.read(1024)
                    f.close()
            flash('The file {} was uploaded successfully'.format(file.filename), 'success')
            return redirect(url_for('index'))
        else:
            flash('Failed to upload video file. Please try again', 'failure')
    return render_template('load-video.html', isAdmin=is_admin())


# def upload_file_sql(filename, user_id=0):
#     cur = mysql.connection.cursor()
#     cur.execute('''
#         INSERT INTO FILES(NAME, CREATORID)
#         VALUE (%s, %s)
#         ''', (filename, user_id))
#     mysql.connection.commit()
#     cur.close()
#     return


@app.route('/previous-feedbacks', methods=['GET', 'POST'])
def previous_feedbacks():
    # connect and ask for all list
    user_id = session.get('ID') if session and session.get('logged_in') else 0
    data_recieved = ''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, SERVER_PORT))
        msg = 'view_feedbacks_list user_id: {}'.format(user_id)
        s.sendall(msg.encode('utf-8'))
        data = s.recv(1024)
        files_details = data.decode('utf-8')

    if files_details == 'Fail':
        return render_template('previous-feedbacks.html', data=list(), isAdmin=is_admin())

    files_details = files_details.split(',')
    # print(files_details)
    data_to_pass = list()
    for file_detail in files_details:
        try:
            name_and_date = file_detail.split('__')
            zip_date = name_and_date[1]
            new_data = dict()
            new_data['date'] = zip_date
            new_data['zip_name'] = name_and_date[0]  # with no extension
            # new_data['zip'] = file_detail
            print('new data')
            print(new_data)
            data_to_pass.append(new_data)
        except:
            continue

    return render_template('previous-feedbacks.html', data=data_to_pass, isAdmin=is_admin())


@app.route('/previous-feedback/<zip_name>', methods=['GET', 'POST'])
def previous_feedback(zip_name):
    user_id = session.get('ID') if session and session.get('logged_in') else 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # s.setblocking(0)  # non blocking
        s.connect((SERVER_IP, SERVER_PORT))
        zip_name_to_send = zip_name.split('.')[0]
        print(zip_name_to_send)
        msg = 'view_graphs user_id: {} filename: {}'.format(user_id, zip_name_to_send)
        print('PREVIOUS FEEDBACK msg = {}'.format(msg))
        s.sendall(msg.encode('utf-8'))

        path_to_zip = os.getcwd() + '/static/temp/{}.zip'.format(zip_name)
        print('path to zip is : {}'.format(path_to_zip))
        with open(path_to_zip, 'wb') as f:
            data = s.recv(1024)
            while data:
                print('getting zip into temp directory ...')
                f.write(data)
                data = s.recv(1024)
            print('finish receiving data')

    csvs_paths = get_all_files_paths(zip_name, 'csvs', extensions_of_files_to_find=['csv'],
                                     expected_file_names=['all_keypoints', 'angles', 'detected_keypoints',
                                                          'interpolated_all_keypoints'])

    frames_paths = get_all_files_paths(zip_name, 'annotated_frames', ['jpg'])
    sort_lambda = lambda path: int((path.split('.')[0]).split('_')[-1])
    frames_paths = sorted(frames_paths, key=sort_lambda)
    frames_paths_dict = [{'path': path.replace('\\', '/')} for path in frames_paths]
    first_frame_num = int((frames_paths[0].split('.')[0]).split('_')[-1])
    data_to_pass = [{'path': path.replace('\\', '/')} for path in csvs_paths]  # for html format

    return render_template('previous-feedback.html', zip_name=zip_name, data=data_to_pass, frames=frames_paths_dict,
                           isAdmin=is_admin(), first_frame_number=first_frame_num)


# Forum
@app.route("/forum/<page>")
def forum(page):
    page = int(page)
    limit = 30
    offset = limit * page
    nextPageExists = False
    msg = 'forum_view_page offset: {} limit: {}'.format(offset, limit)
    topics = pickle.loads(send_msg_to_server(msg))
    pinned = {}

    # cur = mysql.connection.cursor()
    # if page == 0:
    #     cur.execute('''
    #         SELECT TOPICS.ID, TOPICS.NAME, USERS.USERNAME AS 'CREATOR', Count(POSTS.ID) AS 'POSTS', MAX(POSTS.CREATION_DATE) AS 'LASTPOST'
    #         FROM TOPICS
    #         INNER JOIN USERS ON TOPICS.CREATORID = USERS.ID
    #         LEFT JOIN POSTS ON POSTS.TOPICID = TOPICS.ID
    #         WHERE TOPICS.ISPINNED = TRUE
    #         GROUP BY TOPICS.ID
    #         ORDER BY LASTPOST DESC;''')
    #     pinned = cur.fetchall()
    # cur.execute('''
    #     SELECT TOPICS.ID, TOPICS.NAME, USERS.USERNAME AS 'CREATOR', Count(POSTS.ID) AS 'POSTS', MAX(POSTS.CREATION_DATE) AS 'LASTPOST'
    #     FROM TOPICS
    #     INNER JOIN USERS ON TOPICS.CREATORID = USERS.ID
    #     LEFT JOIN POSTS ON POSTS.TOPICID = TOPICS.ID
    #     WHERE TOPICS.ISPINNED = FALSE
    #     GROUP BY TOPICS.ID
    #     ORDER BY LASTPOST DESC
    #     LIMIT %s, %s''', (offset, limit + 1,))
    # topics = cur.fetchall()

    if len(topics) > limit:
        nextPageExists = True
    topics = topics[:limit]

    if len(topics) == 0 and page != 0:
        return redirect("/forum/" + str(page - 1))

    return render_template("forum.html", p=2, topics=topics, pinned=pinned, page=page, nextPageExists=nextPageExists,
                           isAdmin=is_admin())


@app.route("/forum/topic/<forumPage>/<topicID>/<page>")
def topic(forumPage, topicID, page):
    page = int(page)
    limit = 10
    nextPageExists = False

    msg = 'forum_topic_name topic_id: {}'.format(topicID)
    name = send_msg_to_server(msg).decode("utf-8")

    # cur = mysql.connection.cursor()
    # cur.execute('''
    #     SELECT TOPICS.NAME, TOPICS.ISPINNED
    #     FROM TOPICS
    #     WHERE TOPICS.ID = %s;''', (topicID,))
    # topic = cur.fetchone()
    # if not topic:
    #     return redirect("/forum/" + forumPage)
    if not name:
        return redirect("/forum/" + forumPage)
    # name = topic['NAME']
    # isPinned = int(topic['ISPINNED'])
    isPinned = 0
    msg = 'forum_view_topic topic_id: {} page: {} limit: {}'.format(topicID, page, limit)
    posts = pickle.loads(send_msg_to_server(msg))

    # cur.execute('''
    #     SELECT POSTS.ID, POSTS.CONTENT, POSTS.CREATION_DATE, USERS.USERNAME, USERS.ISADMIN
    #     FROM POSTS
    #     INNER JOIN USERS ON POSTS.CREATORID = USERS.ID
    #     WHERE POSTS.TOPICID = %s
    #     ORDER BY POSTS.CREATION_DATE
    #     LIMIT %s, %s;''', (topicID, page * limit, limit + 1))
    # posts = cur.fetchall()

    if len(posts) > limit:
        nextPageExists = True
    if len(posts) == 0 and page != 0:
        return redirect("/forum/topic/" + forumPage + "/" + topicID + "/" + str(page - 1))
    posts = posts[:limit]
    return render_template("topic.html", p=2, posts=posts, name=name, topicID=topicID, forumPage=forumPage,
                           page=page, nextPageExists=nextPageExists, isPinned=isPinned, isAdmin=is_admin())


# Create post, topic

# def createPostFunction(content, topicID, userID=0):
#     cur = mysql.connection.cursor()
#     cur.execute('''
#         INSERT INTO POSTS(CONTENT, CREATORID, TOPICID)
#         VALUE (%s, %s, %s)
#         ''', (content, userID, topicID))
#     mysql.connection.commit()
#     cur.close()
#     return


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
        msg = 'forum_create_post user_id: {} topic_id: {} content: {}'.format(userID, topicID, content)
        send_msg_to_server(msg)
        # createPostFunction(content, topicID, userID)
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
        msg = 'forum_create_topic user_id: {} title: {} content: {}'.format(userID, title, content)
        topicID = send_msg_to_server(msg).decode("utf-8")

        # cur = mysql.connection.cursor()
        # cur.execute('''
        #     INSERT INTO TOPICS(NAME, CREATORID)
        #     VALUE (%s, %s)
        #     ''', (title, userID))
        # mysql.connection.commit()
        # topicID = cur.lastrowid
        # cur.close()
        # createPostFunction(content, topicID, userID)
        return redirect("/forum/topic/0/" + str(topicID) + "/0")
    return redirect("/forum")


def send_msg_to_server(msg):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, SERVER_PORT))
        s.sendall(msg.encode('utf-8'))
        answer = b''
        part_answer = s.recv(1024)
        while part_answer:
            print('getting answer from server..')
            answer += part_answer
            part_answer = s.recv(1024)
        print(answer)
        return answer


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

    msg = 'login username: {} password: {}'.format(_username, _passwd)

    answer = send_msg_to_server(msg).decode("utf-8")
    print("Answer is : " + answer)
    answer = answer.split()
    if answer[0] != "Fail:":
        session['ID'] = answer[0]
        session['username'] = answer[1]
        session['logged_in'] = answer[2]
        session['isAdmin'] = answer[3]
        flash(u"You're now logged in!", "success")
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
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, SERVER_PORT))
        msg = 'register username: {} password: {} email: {}'.format(_username, _passwd, _email)
        s.sendall(msg.encode('utf-8'))
        data = s.recv(1024)
        data = data.decode("utf-8")
        print(data)
        if data.split(' ')[0] == "Fail:":
            flash(data, "danger")
            return redirect(url_for('register'))

    flash(u"You're now registered!", "success")
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
    return render_template('plug-and-play.html', isAdmin=is_admin())
