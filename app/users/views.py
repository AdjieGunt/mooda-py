from flask import Blueprint, request, jsonify, make_response
from app.users.models import db, tbl_users, user_schema
from flask_restful import Api, Resource

from sqlalchemy import func, sql
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

import re, datetime, json, dateutil.parser
from datetime import date, datetime

import random, os

# Blueprint
users = Blueprint('users', __name__)

# http://marshmallow.readthedocs.org/en/latest/quickstart.html#declaring-schemas
#https://github.com/marshmallow-code/marshmallow-jsonapi

# Schema

user_group_schema = user_schema()


api = Api(users)


class user_group(Resource):
    def post(self):
        raw_dict     = request.get_json(force=True)
        # print request.environ
        reqEnv = request.environ
        http_origin = reqEnv['HTTP_ORIGIN']
        print http_origin
        try:
            lastid = db.session.query(func.max(tbl_users.id)).one()[0]
            if lastid == None: lastid = 0
            userid       = int(lastid) + 1
            email        = raw_dict['email']
            password     = raw_dict['password']
            firstname    = raw_dict['firstname']
            lastname     = raw_dict['lastname']
            birthdate    = raw_dict['birthdate']
            user = tbl_users(userid, email, password, firstname, lastname, birthdate)
            user.add(user)
            resp = {'status' : 'true'}
            # resp.status_code = 200
        except Exception as err:
            resp = {'success' : 'false', 'msg': err}
        return resp
        
# Add Resource  
api.add_resource(user_group, '/users')



