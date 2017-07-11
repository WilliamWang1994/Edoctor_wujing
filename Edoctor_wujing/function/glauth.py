#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from functools import wraps
from flask import request
from function.glconfig import auth_cfg

def check_auth(username, password,url,func):
    """This function-1 is called to check if a username /
    password combination is valid.
    """
    # print(url)
    # print(func)
    # print(username)
    # print(password)
    # return username == 'kettle' and password == 'Edoctor123!'
    return True

def auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password,request.url,request.method):
            return {'success': False, 'error_code': 1, 'message': 'Auth Fail'}, 401
        return f(*args, **kwargs)
    return decorated

