import base64
import hashlib
import os
from psycopg2.extras import Json


INSERT_USER = '''INSERT INTO odin.identity_ledger (identity_id)
    VALUES (%s)
    ON CONFLICT (identity_id) DO NOTHING
    RETURNING *'''

SET_FULLNAME = '''INSERT INTO odin.identity_full_name_ledger
        (identity_id, full_name)
    VALUES (%s, %s)
    RETURNING *'''
SET_PASSWORD = '''INSERT INTO odin.credentials_password_ledger
        (identity_id, password, process)
    VALUES (%s, %s, %s)
    RETURNING *'''
SET_SUPERUSER = '''INSERT INTO odin.identity_superuser_ledger
        (identity_id, superuser, annotation)
    VALUES (%s, %s, %s)
    RETURNING *'''


def createuser(cnx, username, password=None):
    if len(cnx.execute(INSERT_USER, (username,))):
        print(username, "created")
    else:
        print(username, "already present")
    if password:
        setpassword(cnx, username, password)


def setfullname(cnx, username, full_name):
    cnx.assert_module('opt.full-name')
    cnx.execute(SET_FULLNAME, (username, full_name))
    print(username, "full name set")


def setpassword(cnx, username, password):
    cnx.assert_module('authn')
    salt = os.urandom(24)
    process = dict(name='pbkdf2-sha256', rounds=300000, length=32,
        salt=base64.b64encode(salt).decode('utf8'))
    pwhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf8'), salt, 300000)
    cnx.execute(SET_PASSWORD, (username, base64.b64encode(pwhash).decode('utf8'), Json(process)))
    print(username, "password set")


def setsuperuser(cnx, username, su=True, annotation=dict()):
    cnx.assert_module('authz')
    cnx.execute(SET_SUPERUSER, (username, su, Json(annotation)))
    print(username, "super user set" if su else "unpriviliged user")


class User(object):
    def __init__(self, cnx, username):
        self.cnx = cnx
        self.username = username
