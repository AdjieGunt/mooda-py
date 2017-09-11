from flask import Blueprint, request, jsonify, make_response
from app.models.m_users import tbl_users, user_schema
from app.views.sendEmail import senEmail
from app import db
from flask_restful import Api, Resource

from sqlalchemy import func, sql, update, delete
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

#nanti akan di panggil di __init__.py
api = Api(users)


class user_group(Resource):
    def post(self):
        raw_dict     = request.get_json(force=True)
        # print raw_dict
        # print request.environ
        # reqEnv = request.environ
        # http_origin = reqEnv['HTTP_ORIGIN']
        # print http_origin

        try:
            lastid = db.session.query(func.max(tbl_users.id)).one()[0]
            if lastid == None: lastid = 0
            id           = int(lastid) + 1
            email        = raw_dict['email']
            password     = raw_dict['password']
            firstname    = raw_dict['firstname']
            lastname     = raw_dict['lastname']

                        
            date         = raw_dict['birth']['date']
            month        = raw_dict['birth']['month']
            year         = raw_dict['birth']['year']

            # print date +'-'+month +'-'+ year

            # logic if date from google / facebook are nol data
            if date == "00" and month == "00" and year == "0000" :
                date = "01"
                month = "01"
                year = "2000"

                # print date +'-'+month +'-'+ year

            birthdate= year+'-'+month+'-'+date
            # birthdate    = datetime.strftime(conver, '%Y-%m-%d')
            # birthdate = conver
            # print conver

            user = tbl_users(id, email, password, firstname, lastname, birthdate)
            user.add(user)
            resp = {'status' : 'true'}

            # send email
            sen = senEmail(email)
            sen.oto()

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

class getLimitUsers(Resource):
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

        data = user_schema().dump(limitUser, many = True).data                        #parsing data ke JSON
        
        data1 = []
        for i in range(len(data['data'])):
            data2 = []
            data2.insert(i, {
                'id':data['data'][i]['id'],
                'email':data['data'][i]['attributes']['email'],
                'firsname':data['data'][i]['attributes']['firstname'],
                'lastname':data['data'][i]['attributes']['lastname'],
                'birthdate':data['data'][i]['attributes']['birthdate'],
                'isActive':data['data'][i]['attributes']['isactive']
            })
            for a in data2:
                data1.append(a)
        
        data['data'] = data1
        result = data

        return result

class getUserById(Resource):
    def get(self):
        id_rw = request.args.get('id', None)

        # reqEnv = request.environ        #buat ngedapetin data user dari mana aksesnya
        # http_origin = reqEnv['HTTP_ORIGIN']

        # user = tbl_users.query.filter_by(userid = id_user)                #untuk select all via id = id

        user = db.session.query(
            tbl_users.id,                                                #ini juga bisa
            tbl_users.email,       
            tbl_users.firstname, 
            tbl_users.lastname,
            tbl_users.birthdate            
        ).filter_by(id = id_rw)
    
        data=user_schema().dump(user, many = True).data      #many=True harus ada space mungkin , susah bgt cm nampilin data doang
        
        #get birthdate and split them
        dt=datetime.strptime(data['data'][0]['attributes']['birthdate'],'%Y-%m-%d')
        d=dt.day
        m=dt.month
        y=dt.year

        #create new object
        newDate = {}
        newDate['date'] = d
        newDate['month'] = m
        newDate['year'] = y

        #replacing databirthdate
        data['data'][0]['attributes']['birthdate'] = newDate
        
        data1 = []
        for i in range(len(data['data'])):
            data2 = []
            data2.insert(i, {
                'id':data['data'][i]['id'],
                'email':data['data'][i]['attributes']['email'],
                'firsname':data['data'][i]['attributes']['firstname'],
                'lastname':data['data'][i]['attributes']['lastname'],
                'birthdate':data['data'][i]['attributes']['birthdate']
            })
            for a in data2:
                data1.append(a)

        # replace real data to data1 
        data['data'] = data1 
        result= data
        # result['result']=data['data']
        
        return result


class deleteUser(Resource):
    def post(self):

        id_rw = request.args.get('id', None)
        if id_rw is None :
            raw_dict     = request.get_json(force=True)
            id_rw=raw_dict['id']

        # reqEnv = request.environ
        # http_origin = reqEnv['HTTP_ORIGIN']

        try:
            
            sql = db.session.query(tbl_users).filter_by(id = id_rw).update({"isDelete":True})
            db.session.commit()
            resp = {'status' : 'true'}
        except Exception as err:
            resp = {'success':'false', 'msg':err}

        return resp

# class updateUser(Resource):
#     def post(self):



# class OtosendEmail():
#     def send():

        

# Add Resource  
api.add_resource(user_group, '/register')
api.add_resource(getUserById, '/getuser')
api.add_resource(deleteUser, '/delete')
api.add_resource(CheckUserByEmail, '/usercheck')
api.add_resource(getLimitUsers, '')
