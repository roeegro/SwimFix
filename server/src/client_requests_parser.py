import datetime

import MySQLdb
import bcrypt
import MySQLdb.cursors
import facade
from output_manager import make_archive

MYSQL_HOST = '65.19.141.67'
MYSQL_PORT = 3306
MYSQL_USER = 'lironabr'
MYSQL_PASSWORD = 'h3dChhmg'
MYSQL_DB = 'lironabr_swimming_project'
MYSQL_CURSORCLASS = 'DictCursor'
mysql = MySQLdb.Connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, passwd=MYSQL_PASSWORD, db=MYSQL_DB,
                        cursorclass=MySQLdb.cursors.DictCursor)


def login(data, conn, params):
    print('LOGIN')
    print(data)
    username = data[data.index('username:') + 1]
    password = data[data.index('password:') + 1]
    cur = mysql.cursor()
    res = cur.execute("SELECT * FROM USERS WHERE USERNAME = %s", (username,))

    if res > 0:
        user = cur.fetchone()
        if bcrypt.checkpw(password.encode('utf-8'), user['PASSWORD_HASH'].encode('utf-8')):
            return '{} {} {} {}'.format(user['ID'], user['USERNAME'], True, user['ISADMIN'] != 0)

    return 'Fail: Incorrect Login'


def register(data, conn, params):
    print('REGISTER')
    username = data[data.index('username:') + 1]
    password = data[data.index('password:') + 1]
    email = data[data.index('email:') + 1]
    cur = mysql.cursor()
    res = cur.execute("SELECT * FROM USERS WHERE USERNAME = %s OR EMAIL = %s", (username, email))

    if res != 0:
        return 'Fail: User or email already exists'

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cur.execute("INSERT INTO USERS(USERNAME, EMAIL, PASSWORD_HASH) VALUES (%s, %s, %s)",
                (username, email, password_hash))

    mysql.commit()
    cur.close()
    return 'Success: User Registered'


def download(data, conn, params):
    pass


def view_feedbacks_list(data, conn, params):
    print('VIEW_FEEDBACK_LIST')
    user_id = data[data.index('user_id:') + 1]
    cur = mysql.cursor()
    res = cur.execute("SELECT USERNAME FROM USERS WHERE ID = %s", user_id)
    if res == 0:
        return "Fail"
    username = cur.fetchone()['USERNAME']

    cur = mysql.cursor()
    cur.execute("SELECT * FROM FILES WHERE CREATORID = {}".format(user_id))
    results = cur.fetchall()
    answer = ''
    for result in results:
        creation_date = result['CREATION_DATE']
        movie_name = result['NAME']
        [date, time] = str(creation_date).split(' ')[0:2]
        time = time.replace(':', '-')
        to_add = '{}__{}_{}'.format(movie_name, date, time) + ','
        answer += to_add
    print(answer)
    return answer


def view_graphs(data, conn, params):
    user_id = data[data.index('user_id:') + 1]
    filename = data[data.index('filename:') + 1]
    cur = mysql.cursor()
    res = cur.execute("SELECT USERNAME FROM USERS WHERE ID = %s", user_id)
    if res == 0:
        return "Fail"
    username = cur.fetchone()['USERNAME']
    cur.execute("SELECT * FROM FILES WHERE NAME = \'{}\' AND CREATORID = {}".format(filename, user_id))
    if res == 0:
        return "Fail"
    res = cur.fetchone()
    print('res')
    print(res)
    creation_date = res['CREATION_DATE']
    [date, time] = str(creation_date).split(' ')[0:2]
    time = time.replace(':', '-')
    creation_date_to_search = date + '/' + time
    path_to_search_in = '../output/{}/{}/{}'.format(username, filename, creation_date_to_search)
    zip_location = '../temp'
    print(
        'ZIPING PROCESS : zip location : {} , content in : {} , will be called : {} '.format(zip_location, path_to_search_in, filename))
    make_archive(path_to_search_in, zip_location, filename + ".zip")
    file_path_to_send = zip_location + '/' + filename + ".zip"
    print('file path to send: {}'.format(file_path_to_send))
    f = open(file_path_to_send, 'rb')
    l = f.read(1024)
    while l:
        conn.send(l)
        print('sending zip...')
        l = f.read(1024)
    f.close()
    print('sent all zip')
    return "success"


def view_forum(data, conn, params):
    pass


def forum_post(data, conn, params):
    pass


def forum_comment(data, conn, params):
    pass


def analyze_video(data, conn, params):
    pass


def add_test(data, conn, params):
    msg = 'start'
    conn.send(msg.encode('utf-8'))
    expected_videos_path = '../excepted_data/videos/'
    expected_csvs_path = '../excepted_data/csvs/'
    new_expected_video_path = expected_videos_path + data[data.index('video_path:') + 1]
    new_expcted_csv_path = expected_csvs_path + data[data.index('csv_path:') + 1]
    msg = 'start'
    conn.send(msg.encode('utf-8'))
    with open(new_expected_video_path, 'wb') as video_file:
        while True:
            print('receiving video...')
            data = conn.recv(1024)
            if not data:
                break
            # write data to a file
            video_file.write(data)
            try:
                msg = data.decode('utf-8')
                if msg == 'end first': # move to next file
                    break
            except:
                continue
    print('-------------------start with csv -------------------')
    with open(new_expcted_csv_path, 'wb') as csv_file:
        while True:
            print('receiving csv...')
            data = conn.recv(1024)
            if not data:
                break
            # write data to a file
            csv_file.write(data)


def run_test(data, conn, params):
    pass


def upload(data, conn, params):
    user_id = data[data.index('user_id:') + 1]
    cur = mysql.cursor()
    cur.execute("SELECT USERNAME FROM USERS WHERE ID = %s", user_id)

    username = cur.fetchone()['USERNAME']
    filename = data[data.index('filename:') + 1]
    # for handshake
    msg = 'start'
    conn.send(msg.encode('utf-8'))
    videos_path = '../videos/'
    path_to_video = videos_path + filename
    with open(path_to_video, 'wb') as f:
        while True:
            print('receiving data...')
            data = conn.recv(1024)
            if not data:
                break
            # write data to a file
            f.write(data)
    print('Successfully get the file')
    print("Analysing path...")

    facade.create_output_dir_for_movie_of_user(path_to_video, username)
    all_keypoints_csv_path = facade.get_keypoints_csv_from_video(path_to_video, params)
    interpolated_keypoints_path = facade.interpolate_and_plot(all_keypoints_csv_path)
    facade.get_angles_csv_from_keypoints_csv(interpolated_keypoints_path)
    facade.get_detected_keypoints_by_frame(all_keypoints_csv_path)
    facade.get_average_swimming_period_from_csv(interpolated_keypoints_path)
    zip_path = facade.zip_output()
    creation_date = facade.get_output_dir_path('date_path').split('/')[-1]
    creation_time = facade.get_output_dir_path('time_path').split('/')[-1]
    creation_time = creation_time.replace('-', ':')
    date_time_as_str = creation_date + " " + creation_time
    date_time_obj = datetime.datetime.strptime(date_time_as_str, '%Y-%m-%d %H:%M:%S')
    cur.execute('''
        INSERT INTO FILES(NAME, CREATORID, CREATION_DATE)
        VALUE (%s, %s, %s)
        ''', (filename, user_id, date_time_obj))
    mysql.commit()
    cur.close()


def upload_file_sql(filename, user_id=0):
    cur = mysql.connection.cursor()
    cur.execute('''
        INSERT INTO FILES(NAME, CREATORID)
        VALUE (%s, %s)
        ''', (filename, user_id))
    mysql.connection.commit()
    cur.close()
    return


requests_dict = {'login': login, 'register': register, 'download': download, 'view_feedbacks_list': view_feedbacks_list,
                 'view_graphs': view_graphs,
                 'view_forum': view_forum,
                 'forum_post': forum_post, 'forum_comment': forum_comment, 'analyze_video': analyze_video,
                 'add_test': add_test, 'run_test': run_test, 'upload': upload}


def main_parser(data, conn, params):
    data = data.decode('utf-8')
    data_lst = (data.split(' '))
    print('request type: {}'.format(data_lst[0]))
    print('decoded data :')
    print(data)
    return (requests_dict[data_lst[0]])(data_lst[1:], conn, params)
