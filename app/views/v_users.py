from flask import Blueprint, request, jsonify, make_response
from app.models.m_users import tbl_users, user_schema
from app import db
from flask_restful import Api, Resource

from sqlalchemy import func, sql
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

import re, datetime, json, dateutil.parser
from datetime import date, datetime

import random, os, hashlib

# Blueprint
users = Blueprint('users', __name__)

# http://marshmallow.readthedocs.org/en/latest/quickstart.html#declaring-schemas
#https://github.com/marshmallow-code/marshmallow-jsonapi

# Schema

user_group_schema = user_schema()


api = Api(users)

class check_origin():
    def isFromMooda():
        origin = request.environ['HTTP_ORIGIN']
        if 'mooda.id' in origin:
            return True
        else:
            return False


class user_group(Resource):
    def post(self):
        raw_dict     = request.get_json(force=True)
        print raw_dict
        # print request.environ
        # reqEnv = request.environ
        # http_origin = reqEnv['HTTP_ORIGIN']
        # print http_origin

        try:
            lastid = db.session.query(func.max(tbl_users.id)).one()[0]
            if lastid == None: lastid = 0
            userid       = int(lastid) + 1
            email        = raw_dict['email']
            password     = hashlib.sha256(raw_dict['password']).hexdigest()
            firstname    = raw_dict['firstname']
            lastname     = raw_dict['lastname']
            
            date         = raw_dict['birth']['date']
            month        = raw_dict['birth']['month']
            year         = raw_dict['birth']['year']

            birthdate= year+'-'+month+'-'+date
            # birthdate    = datetime.strftime(conver, '%Y-%m-%d')
            # birthdate = conver
            # print conver

            

            user = tbl_users(userid, email, password, firstname, lastname, birthdate)
            user.add(user)
            resp = {'status' : 'true'}
            # resp.status_code = 200
        except Exception as err:
            resp = {'success' : 'false', 'msg': err}
        return resp

class CheckUserByEmail(Resource):
    def post(self):
        raw_dict = request.get_json(force=True)
        # print request.environ
        reqEnv = request.environ        #buat ngedapetin data user dari mana aksesnya
        http_origin = reqEnv['HTTP_ORIGIN']
        # print http_origin
        
        email = raw_dict['email']
            # cek email di db
        check = tbl_users.query.filter_by(email=email).count()
        if check > 0 :                                  # if email ada return true else return false
            resp = {'status' : 'true', 'msg':'email sudah terdaftar'}
            return resp
        else :
            resp = {'status' : 'false', 'msg':'email belum terdaftar'}                 #jika tidak ada maka return falsa
            return resp

class getUsers(Resource):
    def get(self):    #parameter page_number
        page_number = request.args.get('page', None)                    #untuk set parameter
        limit = request.args.get('limit', None)
        
        # try:
        #     limit
        # except NameError:
        #    limit =50
        if page_number == limit is None:
            limit = 50
            page_number = 1
        elif limit is None:
            limit = 50
        # limitUser = tbl_users.query.limit(number_per_page).offset(page_number * number_per_page)                  #batasan user yg akan di tampilkan
        # limitUser = tbl_users.query.limit(number_per_page).offset((number_per_page*page_number)-number_per_page)  #ofseet itu untuk dari data ke berapa yang akan di tampilin
        newLimit = int(limit)
        newPage = int(page_number)
        limitUser = tbl_users.query.limit(newLimit).offset((newLimit*newPage)-newLimit)
        data = user_schema().dump(limitUser, many=True).data                        #parsing data ke JSON
        
        return data      
        

# Add Resource  
api.add_resource(user_group, '/users')
api.add_resource(CheckUserByEmail, '/usercheck')
api.add_resource(getUsers, '')
