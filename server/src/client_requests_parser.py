import datetime
import pickle
import os
import MySQLdb
import bcrypt
import MySQLdb.cursors
import facade
import output_manager
import tester
import socket
import traceback

MYSQL_HOST = '65.19.141.67'
MYSQL_PORT = 3306
MYSQL_USER = 'lironabr_roeegro'
MYSQL_PASSWORD = 'roeegro'
MYSQL_DB = 'lironabr_swimming_project'
MYSQL_CURSORCLASS = 'DictCursor'
mysql = MySQLdb.Connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, passwd=MYSQL_PASSWORD, db=MYSQL_DB,
                        cursorclass=MySQLdb.cursors.DictCursor)
FAILURE_MSG = "failure".encode('utf-8')
SUCCESS_MSG = "success".encode('utf-8')


def login(data, conn, params):
    print('LOGIN')
    return_msg = FAILURE_MSG
    try:
        username = data[data.index('username:') + 1]
        password = data[data.index('password:') + 1]
        mysql.ping(True)
        cur = mysql.cursor()
        res = cur.execute("SELECT * FROM USERS WHERE USERNAME = %s", (username,))

        if res > 0:
            user = cur.fetchone()
            if bcrypt.checkpw(password.encode('utf-8'), user['PASSWORD_HASH'].encode('utf-8')):
                return_msg = '{} {} {} {}'.format(user['ID'], user['USERNAME'], True, user['ISADMIN'] != 0).encode(
                    "utf-8")
                return
    except IndexError as e:
        print("An exception occurred: %s\nInvalid data %s" % (e, data))
    except mysql.Error as e:
        print("Something went wrong with MySQL: {}".format(e))
    except Exception as e:
        print("An error occurred when trying to upload the video: ", e)
    finally:
        return return_msg


def register(data, conn, params):
    print('REGISTER')
    return_msg = FAILURE_MSG
    try:
        username = data[data.index('username:') + 1]
        password = data[data.index('password:') + 1]
        email = data[data.index('email:') + 1]
        mysql.ping(True)
        cur = mysql.cursor()
        res = cur.execute("SELECT * FROM USERS WHERE USERNAME = %s OR EMAIL = %s", (username, email))

        if res != 0:
            return

        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cur.execute("INSERT INTO USERS(USERNAME, EMAIL, PASSWORD_HASH) VALUES (%s, %s, %s)",
                    (username, email, password_hash))

        mysql.commit()
        cur.close()
        return_msg = SUCCESS_MSG
    except IndexError as e:
        print("An exception occurred: %s\nInvalid data %s" % (e, data))
    except mysql.Error as e:
        print("Something went wrong with MySQL: {}".format(e))
    except Exception as e:
        print("An error occurred when trying to upload the video: ", e)
    finally:
        return return_msg


def view_feedbacks_list(data, conn, params):
    print('VIEW_FEEDBACK_LIST')
    return_msg = FAILURE_MSG
    try:
        user_id = data[data.index('user_id:') + 1]
        mysql.ping(True)
        cur = mysql.cursor()
        res = cur.execute("SELECT USERNAME FROM USERS WHERE ID = {}".format(user_id))
        if res == 0:
            return FAILURE_MSG
        mysql.ping(True)
        cur = mysql.cursor()
        cur.execute("SELECT * FROM FILES WHERE CREATORID = {}".format(user_id))
        results = cur.fetchall()
        answer = ''
        for result in results:
            try:
                creation_date = result['CREATION_DATE']
                movie_name = result['NAME']
                [date, time] = str(creation_date).split(' ')[0:2]
                time = time.replace(':', '-')
                to_add = '{}__{}_{}'.format(movie_name, date, time) + ','
                answer += to_add
            except KeyError as e:
                print("An exception occurred: %s\nInvalid data %s" % (e, result))
                return FAILURE_MSG
        return_msg = answer.encode("utf-8")
    except IndexError as e:
        print("An exception occurred: %s\nInvalid data %s" % (e, data))
    except mysql.Error as e:
        print("Something went wrong with MySQL: {}".format(e))
    except Exception as e:
        print("An error occurred when trying to upload the video: ", e)
    finally:
        return return_msg


def view_graphs(data, conn, params):
    return_msg = FAILURE_MSG
    try:
        user_id = data[data.index('user_id:') + 1]
        filename = data[data.index('filename:') + 1]
        asked_date = data[data.index('date:') + 1]
        date = asked_date.split('_')[0]
        time = asked_date.split('_')[1].replace('-', ':')
        date_time_as_str = date + ' ' + time
        date_time_obj = datetime.datetime.strptime(date_time_as_str, '%Y-%m-%d %H:%M:%S')
        mysql.ping(True)
        cur = mysql.cursor()
        res = cur.execute("SELECT USERNAME FROM USERS WHERE ID = %s", user_id)
        if res == 0:
            return
        username = cur.fetchone()['USERNAME']
        cur.execute(
            "SELECT * FROM FILES WHERE NAME = \'{}\' AND CREATORID = {} AND CREATION_DATE = \'{}\'".format(filename,
                                                                                                           user_id,
                                                                                                           date_time_obj))
        if res == 0:
            return
        res = cur.fetchone()
        creation_date = res['CREATION_DATE']
        [date, time] = str(creation_date).split(' ')[0:2]
        time = time.replace(':', '-')
        creation_date_to_search = date + '/' + time
        path_to_search_in = '../output/{}/{}/{}'.format(username, filename, creation_date_to_search)
        zip_location = '../temp'
        if not os.path.exists(zip_location):
            os.mkdir(zip_location)
        output_manager.make_archive(path_to_search_in, zip_location, filename + ".zip")
        file_path_to_send = zip_location + '/' + filename + ".zip"
        f = open(file_path_to_send, 'rb')
        l = f.read(1024)
        while l:
            conn.send(l)
            print('sending zip...')
            l = f.read(1024)
        f.close()
        print('sent all zip successfully')
        return_msg = "success".encode("utf-8")
    except IndexError as e:
        print("An exception occurred: %s\nInvalid data %s" % (e, data))
    except mysql.Error as e:
        print("Something went wrong with MySQL: {}".format(e))
    except Exception as e:
        print("An error occurred when trying to upload the video: ", e)
    finally:
        return return_msg


def forum_view_page(data, conn, params):
    return_msg = FAILURE_MSG
    try:
        offset = int(data[data.index('offset:') + 1])
        limit = int(data[data.index('limit:') + 1])
        mysql.ping(True)
        cur = mysql.cursor()
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
        return_msg = pickle.dumps(topics)
    except IndexError as e:
        print("An exception occurred: %s\nInvalid data %s" % (e, data))
    except mysql.Error as e:
        print("Something went wrong with MySQL: {}".format(e))
    except Exception as e:
        print("An error occurred when trying to upload the video: ", e)
    finally:
        return return_msg


def forum_topic_name(data, conn, params):
    return_msg = FAILURE_MSG
    try:
        topic_id = data[data.index('topic_id:') + 1]
        mysql.ping(True)
        cur = mysql.cursor()
        cur.execute('''
                SELECT TOPICS.NAME, TOPICS.ISPINNED
                FROM TOPICS
                WHERE TOPICS.ID = %s;''', (topic_id,))
        topic = cur.fetchone()
        if not topic:
            return_msg = None
            return
        return_msg = topic['NAME'].encode("utf-8")
    except IndexError as e:
        print("An exception occurred: %s\nInvalid data %s" % (e, data))
    except mysql.Error as e:
        print("Something went wrong with MySQL: {}".format(e))
    except Exception as e:
        print("An error occurred when trying to upload the video: ", e)
    finally:
        return return_msg


def forum_view_topic(data, conn, params):
    return_msg = FAILURE_MSG
    try:
        topicID = data[data.index('topic_id:') + 1]
        page = int(data[data.index('page:') + 1])
        limit = int(data[data.index('limit:') + 1])
        mysql.ping(True)
        cur = mysql.cursor()
        cur.execute('''
                SELECT POSTS.ID, POSTS.CONTENT, POSTS.CREATION_DATE, USERS.USERNAME, USERS.ISADMIN
                FROM POSTS
                INNER JOIN USERS ON POSTS.CREATORID = USERS.ID
                WHERE POSTS.TOPICID = %s
                ORDER BY POSTS.CREATION_DATE
                LIMIT %s, %s;''', (topicID, page * limit, limit + 1))
        posts = cur.fetchall()
        return_msg = pickle.dumps(posts)
    except IndexError as e:
        print("An exception occurred: %s\nInvalid data %s" % (e, data))
    except mysql.Error as e:
        print("Something went wrong with MySQL: {}".format(e))
    except Exception as e:
        print("An error occurred when trying to upload the video: ", e)
    finally:
        return return_msg


def forum_create_topic(data, conn, params):
    return_msg = FAILURE_MSG
    try:
        user_id = data[data.index('user_id:') + 1]
        title = data[data.index('title:') + 1]
        content = ' '.join(data[data.index('content:') + 1:])
        mysql.ping(True)
        cur = mysql.cursor()
        cur.execute('''
                    INSERT INTO TOPICS(NAME, CREATORID)
                    VALUE (%s, %s)
                    ''', (title, user_id))
        mysql.commit()
        topicID = cur.lastrowid
        cur.close()
        createPostFunction(content, topicID, user_id)
        return_msg = str(topicID).encode("utf-8")
    except IndexError as e:
        print("An exception occurred: %s\nInvalid data %s" % (e, data))
    except mysql.Error as e:
        print("Something went wrong with MySQL: {}".format(e))
    except Exception as e:
        print("An error occurred when trying to upload the video: ", e)
    finally:
        return return_msg


def forum_create_post(data, conn, params):
    return_msg = FAILURE_MSG
    try:
        user_id = data[data.index('user_id:') + 1]
        topic_id = data[data.index('topic_id:') + 1]
        content = ' '.join(data[data.index('content:') + 1:])
        createPostFunction(content, topic_id, user_id)
        return_msg = "success".encode('utf-8')
    except IndexError as e:
        print("An exception occurred: %s\nInvalid data %s" % (e, data))
    except mysql.Error as e:
        print("Something went wrong with MySQL: {}".format(e))
    except Exception as e:
        print("An error occurred when trying to upload the video: ", e)
    finally:
        return return_msg


def createPostFunction(content, topicID, userID=0):
    mysql.ping(True)
    cur = mysql.cursor()
    cur.execute('''
        INSERT INTO POSTS(CONTENT, CREATORID, TOPICID)
        VALUE (%s, %s, %s)
        ''', (content, userID, topicID))
    mysql.commit()
    cur.close()


def add_test(data, conn, params):
    return_msg = FAILURE_MSG
    try:
        expected_videos_path = '../excepted_data/videos/'
        expected_csvs_path = '../excepted_data/csvs/'
        extension = data[data.index('file_extension:') + 1]
        file_size = int(data[data.index('file_size:') + 1])
        if extension == 'avi':
            specific_expected_dir = expected_videos_path
        elif extension == 'csv':
            specific_expected_dir = expected_csvs_path
        else:
            return_msg = 'ERROR - CAN NOT RECOGNIZE PATH'.encode('utf-8')
            return

        new_expected_file_path = specific_expected_dir + data[data.index('file_path:') + 1]
        msg = 'start'
        conn.send(msg.encode('utf-8'))
        counter = 0
        with open(new_expected_file_path, 'wb') as f:
            while file_size > counter:
                data = conn.recv(1024)
                if not data:
                    break
                # write data to a file
                f.write(data)
                counter += 1024
                print('receiving data...')
        return_msg = SUCCESS_MSG
    except FileNotFoundError as e:
        print("File not found at path: ", e.filename)
    except socket.error as e:
        print("An socket error occurred when trying to receive the uploaded video: ", e)
    except Exception as e:
        print("An error occurred when trying to upload the video: ", e)
    finally:
        return return_msg


def run_test(data, conn, params):
    return_msg = FAILURE_MSG
    try:
        filename = data[data.index('filename:') + 1]
        expected_all_kp_csv_path = output_manager.get_excepted_csv_path_for_movie(filename)
        if expected_all_kp_csv_path is None:
            return_msg = str("not found").encode('utf-8')
            return

        upload(data, conn, params)  # Run openpose to create the actual all keypoints csv
        movie_name = filename.split('_from')[0]
        movie_frames_dir, movie_ground_truth_data_dir, movie_test_results_dir = output_manager.build_test_environment_dir(
            movie_name)

        # facade.filter_and_interpolate(expected_all_kp_csv_path, filename, output_path=movie_ground_truth_data_dir)
        frames_dir_path = output_manager.get_output_dir_path('swimfix_frames_path')

        from distutils.dir_util import copy_tree
        copy_tree(frames_dir_path, movie_frames_dir)

        facade.get_angles_csv_from_keypoints_csv(expected_all_kp_csv_path,
                                                 output_path=movie_ground_truth_data_dir)
        facade.get_detected_keypoints_by_frame(expected_all_kp_csv_path, output_path=movie_ground_truth_data_dir)
        tester.start_test(output_manager.get_analytics_dir(), movie_ground_truth_data_dir, movie_test_results_dir,
                          filename)
        return_msg = str("success").encode("utf-8")
    except FileNotFoundError as e:
        print("File not found at path: ", e.filename)
    except socket.error as e:
        print("An socket error occurred when trying to receive the uploaded video: ", e)
    except Exception as e:
        print("An error occurred when trying to upload the video: ", e)
    finally:
        return return_msg


def upload_image_fix(data, conn, params):
    return_msg = FAILURE_MSG
    try:
        file_size = int(data[data.index('file_size:') + 1])
        user_id = data[data.index('user_id:') + 1]
        video_name = data[data.index('video_name:') + 1]
        date = data[data.index('date:') + 1]
        time = data[data.index('time:') + 1]
        filename = data[data.index('filename:') + 1]
        video_name_with_no_extension = video_name.split('.')[0]
        mysql.ping(True)
        cur = mysql.cursor()
        res = cur.execute("SELECT USERNAME FROM USERS WHERE ID = %s", user_id)
        if res == 0:
            return
        username = cur.fetchone()['USERNAME']
        path_to_update = os.getcwd() + '/../output/{}/{}/{}/{}/swimfix_annotated_frames/{}'.format(username,
                                                                                                   video_name_with_no_extension,
                                                                                                   date,
                                                                                                   time,
                                                                                                   filename)
        msg = 'start'
        conn.send(msg.encode('utf-8'))
        with open(path_to_update, 'wb') as f:
            counter = 0
            data = conn.recv(1024)
            while data:
                # write data to a file
                f.write(data)
                data = conn.recv(1024)
                counter += 1024
                print(counter)
                print('receiving data...')
        return_msg = SUCCESS_MSG
    except IndexError as e:
        print("An exception occurred: %s\nInvalid data %s" % (e, data))
    except mysql.Error as e:
        print("Something went wrong with MySQL: {}".format(e))
    except Exception as e:
        print("An error occurred when trying to upload the video: ", e)
        return return_msg


def upload(data, conn, params):
    return_msg = FAILURE_MSG
    try:
        user_id = data[data.index('user_id:') + 1]
        mysql.ping(True)
        cur = mysql.cursor()
        cur.execute("SELECT USERNAME FROM USERS WHERE ID = {}".format(user_id))

        username = cur.fetchone()['USERNAME']
        filename = data[data.index('filename:') + 1]
        # for handshake
        msg = 'start'
        conn.send(msg.encode('utf-8'))
        videos_path = '../videos/'
        if not os.path.exists(videos_path):
            os.mkdir(videos_path)
        path_to_video = videos_path + filename
        f = open(path_to_video, 'wb')
        data = conn.recv(1024)
        conn.settimeout(5.0)
        while data:
            if not data:
                break
            # write data to a file
            f.write(data)
            try:
                data = conn.recv(1024)
            except Exception as e:
                break
        conn.settimeout(None)
        f.close()
        print('Successfully get the file')
        print("Analysing path...")

        facade.create_output_dir_for_movie_of_user(path_to_video, username)
        all_keypoints_csv_path = facade.get_keypoints_csv_from_video(path_to_video, params)
        filtered_and_interpolated_csv_path = facade.filter_and_interpolate(all_keypoints_csv_path, filename)
        facade.plot_keypoints(filtered_and_interpolated_csv_path)
        # interpolated_keypoints_path = facade.interpolate_and_plot(all_keypoints_csv_path)
        angles_csv_path = facade.get_angles_csv_from_keypoints_csv(filtered_and_interpolated_csv_path)
        facade.get_detected_keypoints_by_frame(filtered_and_interpolated_csv_path)
        facade.get_average_swimming_period_from_csv(filtered_and_interpolated_csv_path)
        facade.evaluate_errors(filtered_and_interpolated_csv_path, angles_csv_path)
        # zip_path = facade.zip_output()
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
        return_msg = "success".encode('utf-8')
    except FileNotFoundError as e:
        print("File not found at path: ", e.filename)
    except socket.error as e:
        print("An socket error occurred when trying to receive the uploaded video: ", e)
    except mysql.Error as e:
        print("Something went wrong with MySQL: {}".format(e))
    except Exception as e:
        print("An error occurred when trying to upload the video: ", e)
    finally:
        return return_msg


def upload_file_sql(filename, user_id=0):
    return_msg = FAILURE_MSG
    try:
        mysql.ping(True)
        cur = mysql.cursor()
        cur.execute('''
            INSERT INTO FILES(NAME, CREATORID)
            VALUE (%s, %s)
            ''', (filename, user_id))
        mysql.commit()
        cur.close()
        return_msg = SUCCESS_MSG
    except mysql.Error as e:
        print("Something went wrong with MySQL: {}".format(e))
    except Exception as e:
        print("An error occurred when trying to upload the video: ", e)
    return return_msg


def view_tests_list(data, conn, params):
    print('view_tests_list')
    return_msg = FAILURE_MSG
    answer = ''
    path_to_look_at = '../tests'
    try:
        test_list = os.listdir(path_to_look_at)
        for test in test_list:
            answer = answer + test + ','
        print('answer is ')
        print(answer)
        return_msg = answer.encode("utf-8")
    except FileNotFoundError as e:
        print("File not found at path: ", e.filename)
    except mysql.Error as e:
        print("Something went wrong with MySQL: {}".format(e))
    except Exception as e:
        print("An error occurred when trying to upload the video: ", e)
    finally:
        return return_msg


def view_test_results(data, conn, params):
    return_msg = FAILURE_MSG
    try:
        filename = data[data.index('filename:') + 1]
        path_to_search_in = '../tests/{}'.format(filename)
        print('search in {}'.format(path_to_search_in))
        zip_location = '../temp'
        output_manager.make_archive(path_to_search_in, zip_location, filename + ".zip")
        file_path_to_send = zip_location + '/' + filename + ".zip"
        f = open(file_path_to_send, 'rb')
        l = f.read(1024)
        while l:
            conn.send(l)
            print('sending zip...')
            l = f.read(1024)
        f.close()
        print('sent all test zip')
        return_msg = SUCCESS_MSG
    except FileNotFoundError as e:
        print("File not found at path: ", e.filename)
    except Exception as e:
        print("An error occurred when trying to upload the video: ", e)
    finally:
        return return_msg


def view_users(data, conn, params):
    return_msg = FAILURE_MSG
    try:
        mysql.ping(True)
        cur = mysql.cursor()
        cur.execute('''
                SELECT ID, USERNAME, EMAIL, ISADMIN
                FROM USERS''')
        users_details = cur.fetchall()
        return_msg = pickle.dumps(users_details)
    except IndexError as e:
        print("An exception occurred: %s\nInvalid data %s" % (e, data))
    except mysql.Error as e:
        print("Something went wrong with MySQL: {}".format(e))
    except Exception as e:
        print("An error occurred when trying to upload the video: ", e)
    finally:
        return return_msg


def make_admin(data, conn, params):
    return_msg = FAILURE_MSG
    user_id = data[data.index('user_id:') + 1]
    try:
        mysql.ping(True)
        cur = mysql.cursor()
        cur.execute(''' UPDATE USERS
        SET ISADMIN = 1
        WHERE ID= %s''', user_id)
        mysql.commit()
        cur.close()
        return_msg = SUCCESS_MSG

    except IndexError as e:
        print("An exception occurred: %s\nInvalid data %s" % (e, data))
    except mysql.Error as e:
        print("Something went wrong with MySQL: {}".format(e))
    except Exception as e:
        print("An error occurred when trying to upload the video: ", e)
    finally:
        return return_msg


def get_defined_error_list(data, conn, params):
    return_msg = FAILURE_MSG
    try:
        defined_errors_list = facade.get_defined_errors_list()
        from functools import reduce
        defined_errors_list_as_str = reduce(lambda acc,x: acc + ','+x,defined_errors_list)
        print('before sending the list')
        conn.send(defined_errors_list_as_str.encode('utf-8'))
        print('after sending')
        return_msg = SUCCESS_MSG
    except Exception as e:
        print("An error occurred when trying to send defined errors: ", e)
    finally:
        return return_msg



requests_dict = {'login': login, 'register': register, 'view_feedbacks_list': view_feedbacks_list,
                 'view_graphs': view_graphs,
                 'forum_view_page': forum_view_page, 'forum_view_topic': forum_view_topic,
                 'forum_topic_name': forum_topic_name,
                 'forum_create_topic': forum_create_topic, 'forum_create_post': forum_create_post, 'add_test': add_test,
                 'run_test': run_test, 'upload': upload, 'upload_image_fix': upload_image_fix,
                 'view_tests_list': view_tests_list, 'view_test_results': view_test_results, 'view_users': view_users,
                 'make_admin': make_admin, 'get_defined_error_list':get_defined_error_list}


def main_parser(data, conn, params):
    """ Parser for different types of requests. The requests and their handlers defined in the dictionary above.

    :param data: The message got from client side.
    :param conn: TCP socket
    :param params: Dictionary with confiugrations for OpenPose activation.
    :return:
    """
    return_msg = FAILURE_MSG
    try:
        data = data.decode('utf-8')
        data_lst = (data.split(' '))
        print('decoded data :')
        print(data)
        return_msg = (requests_dict[data_lst[0]])(data_lst[1:], conn, params)
    except IndexError as e:
        print("An error occurred: %s\nOn data: %s" % (data, e))
    except Exception as e:
        print("An error occurred while trying to process the user request: ", e)
    finally:
        return return_msg
