import re
from settings import *
import MySQLdb
import hashlib
import getpass
import arrow
from twilio.rest import TwilioRestClient
import bcrypt
import requests

def Sanatize(str):
    return re.sub('[^a-zA-Z0-9 \']+', '',str) 


def check_db():
    try:
        myDB = MySQLdb.connect(host='localhost', port=3306, user=DB_USER_USER, passwd=DB_USER_PASS, db='halenow')
        c = myDB.cursor()
        c.execute("SELECT * from number")
        result = c.fetchone()
        return result and len(result) > 0
    except:
        return False

def setup_db():
    root_pass = getpass.getpass("mysql root pass:")
    myDB = MySQLdb.connect(host='localhost', port=3306, user='root', passwd=root_pass)
    c = myDB.cursor()
    c.execute('CREATE DATABASE IF NOT EXISTS halenow;')
    myDB.commit()
    c.execute('USE halenow;')
    c.execute('CREATE TABLE IF NOT EXISTS `admin` (user varchar(25), password varchar(64));')
    myDB.commit()
    c.execute("""
    CREATE TABLE IF NOT EXISTS `number` (numb INT, last_date varchar(60));
    """)
    myDB.commit()
    c.execute("""
    CREATE TABLE IF NOT EXISTS `users` (numb INT, phone_number varchar(60), user_id varchar(60), user_name varchar(60), send_text INT);
    """)
    myDB.commit()
    c.execute("""
    CREATE TABLE IF NOT EXISTS `status` (state INT, last_date varchar(60));
    """)
    myDB.commit()
    c.execute("INSERT INTO number (numb, last_date) VALUES (0,0);")
    myDB.commit()
    c.execute("INSERT INTO status (state, last_date) VALUES (0,0);")
    myDB.commit()
    user = raw_input("admin's username:")
    password = getpass.getpass("password:")
    check_password = getpass.getpass("retype password:")
    while (password != check_password):
        print 'ERROR! passwords do not match:'
        password = getpass.getpass("password:")
        check_password = getpass.getpass("retype password:")
    if USE_BCRYPT:
        hashed_pass = bcrypt.hashpw(password, bcrypt.gensalt())
    else:
        m = hashlib.sha256()
        m.update(password)
        hashed_pass = m.digest().encode('hex')
    # print hashed_pass
    c.execute("INSERT INTO admin (user, password) VALUES (%s,%s)", (user, hashed_pass))
    try:
        c.execute("CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';",(DB_USER_USER, DB_USER_PASS))
    except:
        pass
    c.execute("flush privileges;")
    c.execute("GRANT SELECT on halenow.* to '%s'@'localhost';",(DB_USER_USER,))
    c.execute("GRANT SELECT, INSERT, DELETE, UPDATE on halenow.number to '%s'@'localhost';",(DB_USER_USER,))
    c.execute("GRANT SELECT, INSERT, DELETE, UPDATE on halenow.users to '%s'@'localhost';",(DB_USER_USER,))
    c.execute("GRANT SELECT, INSERT, DELETE, UPDATE on halenow.status to '%s'@'localhost';",(DB_USER_USER,))
    c.execute("flush privileges;")
    myDB.commit()
    myDB.close()

def authenticate_user(user, password):
    myDB = MySQLdb.connect(host='localhost', port=3306, user=DB_USER_USER, passwd=DB_USER_PASS, db='halenow')
    cursor = myDB.cursor()
    cursor.execute("SELECT password FROM admin WHERE user=%s", (user,))
    result=cursor.fetchone()
    if result is not None and len(result) > 0:
        if USE_BCRYPT:
            entered_pass = password.encode('utf-8')
            hashed = result[0].encode('utf-8')
            return bcrypt.hashpw(entered_pass, hashed) == hashed
        else:
            m = hashlib.sha256()
            m.update(password)
            entered_pass = m.digest().encode('hex')
            return entered_pass == result[0]
    return False

def get_current_number():
    myDB = MySQLdb.connect(host='localhost', port=3306, user=DB_USER_USER, passwd=DB_USER_PASS, db='halenow')
    cursor = myDB.cursor()
    cursor.execute("SELECT numb, last_date FROM number")
    result = cursor.fetchone()
    return result

def inc_current_number():
    myDB = MySQLdb.connect(host='localhost', port=3306, user=DB_USER_USER, passwd=DB_USER_PASS, db='halenow')
    cursor = myDB.cursor()
    cursor.execute("SELECT numb FROM number")
    cur_num = cursor.fetchone()[0]
    new_num = (cur_num+1) % MAX_NUMBER
    if new_num == 0:
        new_num = 1
    cursor.execute("UPDATE number SET numb = {};".format(new_num))
    cursor.execute("UPDATE number SET last_date = %s",(arrow.now().timestamp,))
    myDB.commit()
    cursor.execute("SELECT numb, last_date FROM number")
    result = cursor.fetchone()

    cursor.execute("SELECT user_id FROM users WHERE numb={}".format(cur_num))
    r = cursor.fetchone()
    if r:
        delete_unique_id(r[0])
    cursor.execute("SELECT phone_number FROM users WHERE numb={}".format(new_num))
    r = cursor.fetchone()
    if r:
        send_sms(r[0], TEXT_MESSAGE)
    return result

def set_current_number(number):
    myDB = MySQLdb.connect(host='localhost', port=3306, user=DB_USER_USER, passwd=DB_USER_PASS, db='halenow')
    cursor = myDB.cursor()
    cursor.execute("UPDATE number SET numb = {};".format(number,))
    cursor.execute("UPDATE number SET last_date = %s",(arrow.now().timestamp,))
    myDB.commit()
    cursor.execute("SELECT numb, last_date FROM number")
    result = cursor.fetchone()
    return result

def send_sms(number, msg=TEXT_MESSAGE):
    if SEND_TEXTS:
        myDB = MySQLdb.connect(host='localhost', port=3306, user=DB_USER_USER, passwd=DB_USER_PASS, db='halenow')
        cursor = myDB.cursor()
        cursor.execute("SELECT send_text FROM users WHERE phone_number=%s",(number,))
        r = cursor.fetchone()
        if r and not r[0]:
            phone_number = re.sub('[^+0-9]','',number)
            if USE_TWILLIO:
                client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
                message = client.messages.create(body=msg,
                    to=phone_number,
                    from_=TWILIO_FROM_NUMB)
            else:
                r = requests.post("http://textbelt.com/text", data={'number':phone_number,'message':TEXT_MESSAGE})
            cursor.execute("UPDATE users SET send_text=1 WHERE phone_number=%s",(number,))
            myDB.commit()

def get_users_number(user_id):
    myDB = MySQLdb.connect(host='localhost', port=3306, user=DB_USER_USER, passwd=DB_USER_PASS, db='halenow')
    cursor = myDB.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id=%s",(user_id,))
    result = cursor.fetchone()
    return result

def get_new_number(user_id, phone_number, user_name):
    myDB = MySQLdb.connect(host='localhost', port=3306, user=DB_USER_USER, passwd=DB_USER_PASS, db='halenow')
    cursor = myDB.cursor()
    cursor.execute("SELECT COUNT(*) from users")
    cnt = cursor.fetchone()[0]
    if cnt > MAX_NUMBER:
        return False
    cursor.execute("SELECT numb from users ORDER BY user_id DESC LIMIT 1")
    result = cursor.fetchone()
    if result:
        number = (result[0] + 1) % MAX_NUMBER
        if number == 0: # Never assign 0
            number = 1
    else:
        cursor.execute("SELECT numb FROM number")
        result = cursor.fetchone()
        number = result[0]
        if number == 0: #At the beginning of each day, reset counter
            number = 1
        else:
            if seeing_people()[0]:
                send_sms(phone_number, TEXT_MESSAGE)
    cursor.execute("INSERT INTO users (numb, phone_number, user_id, user_name, send_text) VALUES ({}, %s, %s, %s, 0)".format(number), (phone_number, user_id, user_name))
    myDB.commit()
    return number

def get_unique_id():
    temp_id = arrow.now().timestamp
    myDB = MySQLdb.connect(host='localhost', port=3306, user=DB_USER_USER, passwd=DB_USER_PASS, db='halenow')
    cursor = myDB.cursor()
    cursor.execute("SELECT numb FROM users WHERE user_id=%s",(str(temp_id),))
    result = cursor.fetchone()
    while result:
        temp_id+=1
        cursor.execute("SELECT numb FROM users WHERE user_id=%s",(str(temp_id),))
        result = cursor.fetchone()
    return str(temp_id)

def delete_unique_id(user_id):
    print 'Deleting user {}'.format(user_id)
    if user_id:
        myDB = MySQLdb.connect(host='localhost', port=3306, user=DB_USER_USER, passwd=DB_USER_PASS, db='halenow')
        cursor = myDB.cursor()
        cursor.execute("DELETE FROM users WHERE user_id=%s",(str(user_id),))
        myDB.commit()

def get_all_users():
    myDB = MySQLdb.connect(host='localhost', port=3306, user=DB_USER_USER, passwd=DB_USER_PASS, db='halenow')
    cursor = myDB.cursor()
    cursor.execute("SELECT user_name, phone_number FROM users")
    return cursor.fetchall()

def seeing_people():
    myDB = MySQLdb.connect(host='localhost', port=3306, user=DB_USER_USER, passwd=DB_USER_PASS, db='halenow')
    cursor = myDB.cursor()
    cursor.execute("SELECT state, last_date FROM status")
    result = cursor.fetchone()
    return result

def set_seeing_people(state):
    cur_time = arrow.now().timestamp
    myDB = MySQLdb.connect(host='localhost', port=3306, user=DB_USER_USER, passwd=DB_USER_PASS, db='halenow')
    cursor = myDB.cursor()
    cursor.execute("UPDATE status SET state={}".format(int(state)))
    cursor.execute("UPDATE status SET last_date=%s",(cur_time,))
    myDB.commit()
    return (state, cur_time)

def clear_schedule():
    myDB = MySQLdb.connect(host='localhost', port=3306, user=DB_USER_USER, passwd=DB_USER_PASS, db='halenow')
    cursor = myDB.cursor()
    cursor.execute("DELETE FROM users")
    myDB.commit()

def start_receiving():
    myDB = MySQLdb.connect(host='localhost', port=3306, user=DB_USER_USER, passwd=DB_USER_PASS, db='halenow')
    cursor = myDB.cursor()
    cursor.execute("SELECT phone_number from users ORDER BY user_id LIMIT 1")
    result = cursor.fetchone()
    if result:
        send_sms(result[0])
