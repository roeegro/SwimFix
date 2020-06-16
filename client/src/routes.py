from io import StringIO
import pickle
import socket
from gui_utils import *
from flask import render_template, url_for, flash, redirect, request, session, jsonify
from forms import RegistrationForm, LoginForm
from threading import Thread
import re
import os
from . import app, SERVER_IP, SERVER_PORT

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'MOV', 'mp4', 'mov'])
IMG_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
sock = socket.socket()
th = Thread()
finished = False
indication_msg = None
server_response = "".encode('utf-8')


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
    if not is_admin() == 'True':
        flash("You are not authorized to access this page", 'danger')
        return redirect(url_for('index'))
    if request.method == 'POST':
        file = request.files['file']
        filename = file.filename
        path_to_temp_store_flle = os.getcwd() + '/static/temp/'+filename
        file.save(path_to_temp_store_flle)
        file_size = get_size_of_file_path(path_to_temp_store_flle)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_IP, SERVER_PORT))
            msg = 'add_test file_path: {} file_extension: {} file_size: {}'.format(filename, filename.split('.')[-1],
                                                                                   file_size)
            s.send(msg.encode('utf-8'))
            msg = None
            while msg != 'start':
                start_msg = s.recv(1024)  # for 'start' message
                msg = start_msg.decode('utf-8')
            f = open(path_to_temp_store_flle, 'rb')
            # send the file
            l = f.read(1024)
            while l:
                s.send(l)
                l = f.read(1024)
            f.close()
            os.remove(path_to_temp_store_flle)
    return render_template('add-test.html')


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


@app.route('/status')
def thread_status():
    global finished, indication_msg
    """ Return the status of the worker thread """
    return jsonify(dict(status=('finished' if finished else 'running'),
                        msg=(
                            "Video received, waiting for OpenPose to start" if indication_msg is None else indication_msg)))


response_dict = {'0': "OpenPose started, detecting keypoints",
                 '1': 'Keypoints detected, preprocessing',
                 '2': 'Keypoints preprocessed, extracting angles',
                 '3': 'Angles extracted, detecting errors',
                 '4': 'Finished error detection, calculating final grade',
                 '5': 'Final grade calculated, assessment is ready'}

num_of_steps = len(response_dict) - 1


def receive_openpose_msg():
    global sock, indication_msg, finished, server_response
    try:
        server_response = sock.recv(1).decode('utf-8')
        indication_msg = response_dict[server_response]
        sock.settimeout(60.0)
        while server_response != str(num_of_steps):
            server_response = sock.recv(1).decode('utf-8')
            if server_response is 'f':
                break
            indication_msg = response_dict[server_response]
        server_response = sock.recv(1024)  # for 'success'' message
        if server_response.decode('utf-8') == 'success':
            indication_msg = "The video was processed and assessed successfully.\n" \
                             "The feedback is waiting in Previous Feedbacks"
        sock.close()
        finished = True
    except Exception as e:
        indication_msg = 'An error occurred while processing the video: ' + str(e)
        finished = True


@app.route("/waiting-page", methods=['GET', 'POST'])
def waiting_page():
    return render_template('waiting-page.html', isAdmin=is_admin())


@app.route("/load-video", methods=['GET', 'POST'])
def load_video():
    global finished, indication_msg, server_response
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            videos_paths_to_upload = upload_video_file(app.config['UPLOAD_FOLDER'], file)
            print(videos_paths_to_upload)
            userID = session.get('ID') if session and session.get('logged_in') else 0
            for video_path in videos_paths_to_upload:
                video_name = (video_path.split('/')[-1]).split('.')[0]  # no extension
                # to create the output dir from the server
                # create_dir_if_not_exists('output')
                # create_dir_if_not_exists('../../server/videos/')
                global sock
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((SERVER_IP, SERVER_PORT))
                msg = 'upload user_id: {} filename: {} '.format(userID, video_name)
                print('UPLOAD {} '.format(msg))
                sock.sendall(msg.encode('utf-8'))
                start_msg = sock.recv(1024)  # for 'start' message
                if start_msg.decode('utf-8') != 'start':
                    flash('Failed to upload video file. Please try again', 'failure')
                    return render_template('load-video.html', isAdmin=is_admin())
                f = open(video_path, 'rb')
                # video_size = os.path.getsize(video_path)
                # upload_percent = 0
                # send the file
                l = f.read(1024)
                while l:
                    sock.send(l)
                    print("Sending data")
                    # upload_percent += 1024 / video_size * 100
                    l = f.read(1024)
                f.close()
            # flash('The file {} was uploaded successfully'.format(file.filename), 'success')
            #     sock.close()
            global th
            finished = False
            th = Thread(target=receive_openpose_msg, args=())
            th.start()
            # return render_template('waiting-page.html', isAdmin=is_admin())
            return redirect(url_for('waiting_page'))
        else:
            flash(u'Failed to upload video file. Please try again', 'error')
    if indication_msg is None:
        finished = False
    elif server_response.decode('utf-8') == 'success':
        flash(indication_msg, 'success')
        indication_msg = None
    else:
        flash(indication_msg, 'danger')
        indication_msg = None
    finished = False
    return render_template('load-video.html', isAdmin=is_admin())


def get_size_of_file_path(file_path):
    f = open(file_path, 'rb')
    f.seek(0, 2)  # moves the file object's position to the end of the file.
    size = f.tell()
    f.close()
    return size


@app.route("/run-test", methods=['GET', 'POST'])
def run_test():
    if not is_admin() == 'True':
        flash("You are not authorized to access this page", 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            videos_paths_to_upload = upload_video_file(app.config['UPLOAD_FOLDER'], file, should_take_full_video=True)
            userID = session.get('ID') if session and session.get('logged_in') else 0
            for video_path in videos_paths_to_upload:
                video_name = (video_path.split('/')[-1]).split('.')[0]  # no extension
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((SERVER_IP, SERVER_PORT))
                    msg = 'run_test user_id: {} filename: {} file_size: {}'.format(userID, video_name,
                                                                                   get_size_of_file_path(video_path))
                    s.sendall(msg.encode('utf-8'))
                    start_msg = s.recv(1024)  # for 'start' message
                    while start_msg.decode('utf-8') != 'start':
                        if start_msg.decode('utf-8') == 'not found':
                            flash('No test found for this video', 'info')
                            return render_template('run-test.html')
                        start_msg = s.recv(1024)
                    f = open(video_path, 'rb')
                    # send the file
                    l = f.read(1024)
                    while l:
                        s.send(l)
                        print("Sending data")
                        l = f.read(1024)
                    f.close()
                flash('The file {} was uploaded successfully'.format(file.filename), 'success')
                return redirect(url_for('admin_index'))
        else:
            flash('Failed to upload video file. Please try again', 'failure')
    return render_template('run-test.html')


@app.route('/tests-results', methods=['GET', 'POST'])
def tests_results():
    if not is_admin() == 'True':
        flash("You are not authorized to access this page", 'danger')
        return redirect(url_for('index'))

    # connect and ask for all list
    data_recieved = ''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, SERVER_PORT))
        msg = 'view_tests_list'
        s.sendall(msg.encode('utf-8'))
        data = s.recv(1024)
        files_details = data.decode('utf-8')

    if files_details == 'Fail':
        return render_template('tests-results.html', data=list(), isAdmin=is_admin())
    print('available tests are : {}'.format(files_details))
    files_details = files_details.split(',')
    data_to_pass = list()
    for file_detail in files_details[:-1]:
        try:
            new_data = dict()
            new_data['video_name'] = file_detail
            data_to_pass.append(new_data)
        except:
            continue

    return render_template('tests-results.html', data=data_to_pass, isAdmin=is_admin())


@app.route('/test-results/<video_name>', methods=['GET', 'POST'])
def test_results(video_name):
    if not is_admin() == 'True':
        flash("You are not authorized to access this page", 'danger')
        return redirect(url_for('index'))

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, SERVER_PORT))
        msg = 'view_test_results filename: {}'.format(video_name)
        s.sendall(msg.encode('utf-8'))

        path_to_zip = os.getcwd() + '/static/temp/{}.zip'.format(video_name)
        with open(path_to_zip, 'wb') as f:
            data = s.recv(1024)
            while data:
                print('getting test zip into temp directory ...')
                f.write(data)
                data = s.recv(1024)
            print('finish receiving data')

    csvs_paths = get_all_files_paths(video_name, 'csvs', extensions_of_files_to_find=['csv'],
                                     predicate=lambda x: x.endswith('_comparison'))

    frames_paths = get_all_files_paths(video_name, 'annotated_frames', ['jpg'],
                                       predicate=lambda x: x.startswith('swimfix'))
    sort_lambda = lambda path: int((path.split('.')[0]).split('_')[-1])
    frames_paths = sorted(frames_paths, key=sort_lambda)
    print(frames_paths)
    frames_paths_dict = [{'path': path.replace('\\', '/')} for path in frames_paths]
    first_frame_num = int((frames_paths[0].split('.')[0]).split('_')[-1])

    data_to_pass = [{'path': path.replace('\\', '/')} for path in csvs_paths]  # for html format
    return render_template('test-result.html', data=data_to_pass, frames=frames_paths_dict,
                           isAdmin=is_admin(), first_frame_number=first_frame_num)


@app.route('/previous-feedbacks', methods=['GET', 'POST'])
def previous_feedbacks():
    # connect and ask for all list
    user_id = session.get('ID') if session and session.get('logged_in') else 0
    files_details = ''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((SERVER_IP, SERVER_PORT))
        msg = 'view_feedbacks_list user_id: {}'.format(user_id)
        s.sendall(msg.encode('utf-8'))
        data = s.recv(1024)
        while data:
            files_details += data.decode('utf-8')
            data = s.recv(1024)

    if files_details == 'Fail':
        return render_template('previous-feedbacks.html', data=list(), isAdmin=is_admin())

    files_details = files_details.split(',')
    files_details.reverse()  # To view new feedbacks first.
    data_to_pass = list()
    for file_detail in files_details:
        try:
            name_and_date = file_detail.split('__')
            zip_date = name_and_date[1]
            new_data = dict()
            new_data['date'] = zip_date
            new_data['zip_name'] = name_and_date[0]  # with no extension
            new_data['movie_name'] = name_and_date[0].split('_from')[0]
            data_to_pass.append(new_data)
        except:
            continue

    return render_template('previous-feedbacks.html', data=data_to_pass, isAdmin=is_admin())


@app.route('/previous-feedback/<details>', methods=['GET', 'POST'])
def previous_feedback(details):
    [zip_name, date] = details.split('__')
    user_id = session.get('ID') if session and session.get('logged_in') else 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # s.setblocking(0)  # non blocking
        s.connect((SERVER_IP, SERVER_PORT))
        zip_name_to_send = zip_name.split('.')[0]
        msg = 'view_graphs user_id: {} filename: {} date: {}'.format(user_id, zip_name_to_send, date)
        print('PREVIOUS FEEDBACK msg = {}'.format(msg))
        s.sendall(msg.encode('utf-8'))
        zip_location = os.getcwd() + '/static/temp'
        path_to_zip = zip_location + '/{}.zip'.format(zip_name)
        if not os.path.exists(zip_location):
            os.mkdir(zip_location)
        with open(path_to_zip, 'wb') as f:
            data = s.recv(1024)
            while data:
                # print('getting zip into temp directory ...')
                f.write(data)
                data = s.recv(1024)
            print('finish receiving data')

    csvs_paths = get_all_files_paths(zip_name, 'csvs', extensions_of_files_to_find=['csv'],
                                     predicate=(lambda x: x in ['all_keypoints', 'angles',
                                                                'interpolated_and_filtered_all_keypoints']))
    [swimmer_errors_path] = get_all_files_paths(zip_name, 'error_detection_csvs',
                                                extensions_of_files_to_find=['csv'],
                                                predicate=lambda x: x in ['swimmer_errors'])
    error_description_by_frames, score = match_error_description_to_frames(swimmer_errors_path)
    frames_paths = get_all_files_paths(zip_name, 'annotated_frames', ['jpg'])
    sort_lambda = lambda path: int((path.split('.')[0]).split('_')[-1])
    frames_paths = sorted(frames_paths, key=sort_lambda)
    frames_paths_dict = [{'path': path.replace('\\', '/')} for path in frames_paths]
    first_frame_num = int((frames_paths[0].split('.')[0]).split('_')[-1])
    data_to_pass = [{'path': path.replace('\\', '/')} for path in csvs_paths]  # for html format

    return render_template('previous-feedback.html', zip_name=zip_name, data=data_to_pass, frames=frames_paths_dict,
                           errors_list=error_description_by_frames, score=score,
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

    if len(topics) > limit:
        nextPageExists = True
    topics = topics[:limit]

    if len(topics) == 0 and page != 0:
        return redirect("/forum/" + str(page - 1))

    return render_template("forum.html", p=2, topics=topics, pinned=pinned, page=page,
                           nextPageExists=nextPageExists,
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
            answer += part_answer
            part_answer = s.recv(1024)
        return answer


# Login / Register / Logout scripts
@app.route('/', methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if not form.validate_on_submit():
        return render_template('login.html', title='Login', form=form)

    _username = request.form['username']
    _passwd = request.form['password']

    msg = 'login username: {} password: {}'.format(_username, _passwd)

    answer = send_msg_to_server(msg).decode("utf-8")
    answer = answer.split()
    if answer[0] != "failure":
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
        data = s.recv(1024).decode("utf-8")
        if data.split(' ')[0] == "failure":
            flash('Fail: User or email already exists', "danger")
            return redirect(url_for('register'))

    flash(u"You're now registered!", "success")
    return redirect(url_for('login'))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route("/plug-and-play", methods=['POST', 'GET'])
def plug_and_play():
    if not is_admin() == 'True':
        flash("You are not authorized to access this page", 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        file = request.files['file']
        if file:
            success = upload_python_file(app.config['UPLOAD_FOLDER'], file)
            if success:
                flash('The file {} was uploaded successfully'.format(file.filename), 'success')
                return admin_index()
            else:
                flash('Failed to upload python file. Please try again', 'danger')
        else:
            flash('Failed to upload python file. Please try again', 'danger')

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, SERVER_PORT))
        msg = 'get_defined_error_list'
        s.sendall(msg.encode('utf-8'))
        defined_errors_list_as_str = ''
        data = s.recv(1024)
        while data:
            defined_errors_list_as_str += data.decode('utf8')
            data = s.recv(1024)
    defined_errors_list = defined_errors_list_as_str.split(',')
    print(data)
    print(defined_errors_list)
    items = [{'id': defined_errors_list.index(defined_error), 'description': defined_error} for defined_error in
             defined_errors_list]
    return render_template('plug-and-play.html', items=items, isAdmin=is_admin())


# Helpers

@app.route("/_pass_data/", methods=['GET', 'POST'])
def _pass_data():
    data_as_json = request.get_json()
    image_b64 = data_as_json['img']
    path_to_save_img_in = os.getcwd() + data_as_json['current img path']
    print(path_to_save_img_in)
    import base64
    image_data = re.sub('^data:image/.+;base64,', '', image_b64)
    image_data = base64.b64decode(image_data)
    userID = session.get('ID') if session and session.get('logged_in') else 0
    filename = path_to_save_img_in.split('/')[-1]
    zip_and_date = data_as_json['current url'].split('/')[-1]
    video_name = zip_and_date.split('__')[0]
    video_date_and_time = zip_and_date.split('__')[1]
    date = video_date_and_time.split('_')[0]
    time = video_date_and_time.split('_')[1]

    with open(path_to_save_img_in, "wb") as f:
        f.write(image_data)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_IP, SERVER_PORT))
        msg = 'upload_image_fix user_id: {} video_name: {} date: {} time: {} filename: {} file_size: {}'.format(userID,
                                                                                                                video_name,
                                                                                                                date,
                                                                                                                time,
                                                                                                                filename,
                                                                                                                get_size_of_file_path(
                                                                                                                    path_to_save_img_in))
        print(msg)
        s.sendall(msg.encode('utf-8'))
        start_msg = s.recv(1024)  # for 'start' message
        while start_msg.decode('utf-8') != 'start':
            if start_msg.decode('utf-8') == 'not found':
                flash('No test found for this video', 'info')
                return render_template('run-test.html')
            start_msg = s.recv(1024)
        with open(path_to_save_img_in, "rb") as f:
            l = f.read(1024)
            while l:
                s.send(l)
                print("Sending data")
                l = f.read(1024)
    return jsonify({'returned_url': url_for('previous_feedback', details=zip_and_date)})


@app.route('/user-feedback/<details>', methods=['GET', 'POST'])
def user_feedback(details):
    [zip_name, date] = details.split('__')
    user_id = session.get('ID') if session and session.get('logged_in') else 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # s.setblocking(0)  # non blocking
        s.connect((SERVER_IP, SERVER_PORT))
        zip_name_to_send = zip_name.split('.')[0]
        msg = 'view_graphs user_id: {} filename: {} date: {}'.format(user_id, zip_name_to_send, date)
        print('USER FEEDBACK msg = {}'.format(msg))
        s.sendall(msg.encode('utf-8'))
        zip_location = os.getcwd() + '/static/temp'
        path_to_zip = zip_location + '/{}.zip'.format(zip_name)
        if not os.path.exists(zip_location):
            os.mkdir(zip_location)
        with open(path_to_zip, 'wb') as f:
            data = s.recv(1024)
            while data:
                # print('getting zip into temp directory ...')
                f.write(data)
                data = s.recv(1024)
            print('finish receiving data')

    [swimmer_errors_path] = get_all_files_paths(zip_name, 'error_detection_csvs',
                                                extensions_of_files_to_find=['csv'],
                                                predicate=lambda x: x in ['swimmer_errors'])
    error_description_by_frames, score = match_error_description_to_frames(swimmer_errors_path)
    print(error_description_by_frames, score)
    frames_paths = get_all_files_paths(zip_name, 'annotated_frames', extensions_of_files_to_find=['jpg'],
                                       predicate=lambda x: x.startswith('swimfix'))
    sort_lambda = lambda path: int((path.split('.')[0]).split('_')[-1])
    frames_paths = sorted(frames_paths, key=sort_lambda)
    frames_paths_dict = [{'path': path.replace('\\', '/')} for path in frames_paths]
    first_frame_num = int((frames_paths[0].split('.')[0]).split('_')[-1])
    last_frame_num = int((frames_paths[-1].split('.')[0]).split('_')[-1])

    return render_template('user-feedback.html', zip_name=zip_name, data=[], frames=frames_paths_dict,
                           errors_list=error_description_by_frames, score=score,
                           isAdmin=is_admin(), first_frame_number=first_frame_num, last_frame_number=last_frame_num)


@app.route('/add-admin/<id_to_promote>/', methods=['GET', 'POST'])
def add_admin(id_to_promote):
    if not is_admin() == 'True':
        flash("You are not authorized to access this page", 'danger')
        return redirect(url_for('index'))

    if id_to_promote and int(id_to_promote):
        print(id_to_promote)
        promote_msg = "make_admin user_id: {}".format(id_to_promote)
        answer = send_msg_to_server(promote_msg).decode('utf-8')
        if answer == "failure":
            flash("Failed to promote user. Please try again", "danger")
        else:
            flash("Promoted successfully", 'success')

    msg = 'view_users'
    users_details = pickle.loads(send_msg_to_server(msg))

    return render_template('add-admin.html', data=users_details, isAdmin=is_admin())
