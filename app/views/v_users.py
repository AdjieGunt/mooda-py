from flask import Blueprint, request, jsonify, make_response
from app.models.m_users import tbl_users, user_schema
from app.views.sendEmail import senEmail
from app import db
from flask_restful import Api, Resource
import Crypto.Hash
from Crypto.Hash import SHA256          #encrypt password
# import file config for generete token JWT
from config import SECRET_KEY, JWT_ALGORITHM, JWT_EXP_DELTA_SECONDS
from app.views.session_authorization import token_required
import jwt

from sqlalchemy import func, sql, update, delete
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

import re, datetime, json, dateutil.parser
from datetime import date, datetime, timedelta

import random, os, hashlib

# Blueprint
users = Blueprint('users', __name__)

# http://marshmallow.readthedocs.org/en/latest/quickstart.html#declaring-schemas
#https://github.com/marshmallow-code/marshmallow-jsonapi

# Schema
user_group_schema = user_schema()

#nanti akan di panggil di __init__.py
api = Api(users)

class check_origin():
    def isFromMooda():
        origin = request.environ['HTTP_ORIGIN']
        if 'mooda.id' in origin:
            return True
        else:
            return False


class createuser(Resource):
    @token_required
    def post(current_user, self):
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
            password     = hashlib.sha256(raw_dict['password']).hexdigest()
            firstname    = raw_dict['firstname']
            lastname     = raw_dict['lastname']
            date         = raw_dict['birth']['date']
            month        = raw_dict['birth']['month']
            year         = raw_dict['birth']['year']

            # encryption password
            # encript(password)
            pass_enc = encript(password)
            
            # print pass_enc, "resgis"

            # print date +'-'+month +'-'+ year
            # logic if date from google / facebook are nol data
            if date == "00" and month == "00" and year == "0000" :
                date = "01"
                month = "01"
                year = "2000"
            birthdate= year+'-'+month+'-'+date
            # birthdate    = datetime.strftime(conver, '%Y-%m-%d')
            # birthdate = conver
            # print conver

            user = tbl_users(id, email, pass_enc, firstname, lastname, birthdate)
            user.add(user)
            resp = {'status' : 'true'}, 201                             #201 status created

            # send email
            sen = senEmail(email)
            sen.oto()
        except Exception as err:
            resp = {'success' : 'false', 'msg': err}, 400               #400 bad request
        return resp

class CheckUserByEmail(Resource):                                       #tambahkan disini juga sebagai request parameter token
    @token_required
    def post(current_user, self):
        raw_dict = request.get_json(force=True)
        # print request.environ
        reqEnv = request.environ        #buat ngedapetin data user dari mana aksesnya
        http_origin = reqEnv['HTTP_ORIGIN']
        # print http_origin
        
        email = raw_dict['email']
            # cek email di db
        check = tbl_users.query.filter_by(email=email).count()
        if check > 0 :                                  # if email ada return true else return false
            resp = {'status' : 'true', 'msg':'email sudah terdaftar'}, 302              #302 status found
            return resp
        else :
            resp = {'status' : 'false', 'msg':'email belum terdaftar'}, 202                 #202 status accepted , jika tidak ada maka return falsa
            return resp

class getLimitUsers(Resource):
    @token_required
    def get(current_user, self):    #parameter page_number
        page_number = request.args.get('page', None)                    #untuk set parameter
        limit = request.args.get('limit', None)

        checkdata = tbl_users.query.all()
        if not checkdata:
            resp = {'msg':'No found data !'}, 200                   #status ok tp data tidak ada
            return resp
        
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
        

        #membuat structure json baru
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

        return result, 200                                  #200 status ok

class getUserById(Resource):
    @token_required
    def get(current_user, self):
        id_rw = request.args.get('id', None)

        checkdata = tbl_users.query.filter_by(id=id_rw).all()

        if not checkdata:
            resp = {'msg':'No data found !'}, 200
            return resp

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
        
        return result, 200


class deleteUser(Resource):
    @token_required
    def post(current_user, self):
        print current_user
        #buat logic jika bukan admin maka tidak bisa delete
        # if not current_user == 11:
        #     resp = {'msg':'Cannot perform that function !'}, 401, {'WWW-Authenticate':'Basic realm="Admin required !" '}
        #     return resp

        id_rw = request.args.get('id', None)            #parameter header untuk delete
        if id_rw is None :
            raw_dict     = request.get_json(force=True)
            id_rw=raw_dict['id']

        # reqEnv = request.environ
        # http_origin = reqEnv['HTTP_ORIGIN']

        try:
            sql = db.session.query(tbl_users).filter_by(id = id_rw).update({"isDelete":True})
            db.session.commit()
            resp = {'status' : 'true'}, 200
        except Exception as err:
            resp = {'success':'false', 'msg':err}, 400

        return resp

# class updateUser(Resource):
#     def post(self):

class login(Resource):
    def post(self):

        #authentication session
        auth = request.authorization                                    #get request header from browser
        
        email_rw = auth.username                                        #data yg di kirim lewat header
        password_rw = auth.password                                     #data yg di kirim lewat header
        
        # email_rw = request.json.get("email")                          #data yg di kirim lewat json
        # password_rw = request.json.get("password")                    #data yg di kirim lewat json

        passw_enc = encript(password_rw)                                #encript password

        sql = tbl_users.query.filter_by(email=email_rw).filter_by(password=passw_enc).count()
        # sql = db.session.query(tbl_users.id).filter_by(email=email_rw).filter_by(password=passw_enc).count()

        if sql > 0 :

            sql1 = db.session.query(
                tbl_users.id   
            ).filter_by(email=email_rw)

            data_user = user_schema().dump(sql1, many=True).data

            for i in range(len(data_user['data'])):
                # get id user for generet token jwt
                userid = data_user['data'][i]['id']
            
            #generete new token
            payload = {
                'userid':userid,
                'exp':datetime.utcnow() + timedelta(weeks=JWT_EXP_DELTA_SECONDS)
            }
            token = jwt.encode(payload, SECRET_KEY, JWT_ALGORITHM)                                             #SECRET_KEY, JWT_ALGORITHM di ambil dari file config
            token_decode = token.decode('utf-8')
            # print token2
            # resp = { 'success':'true', 'data': data_user}, 202
            resp = {'success':'true', 'token':token_decode}, 202                                                                        #200  status accepted
        else:
            resp = {'success':'false', 'msg':'Email salah.'}, 401, {'WWW-Authenticate':'Basic realm="Login required !" '}       #401 status UNAUTHORIZED, WWW-Authenticate itu untuk response error di header
        return resp


def encript(password):
    enc = SHA256.new(password)
    pass_en=enc.hexdigest()
    return pass_en
        

# Add Resource  
api.add_resource(createuser, '/register')
api.add_resource(getUserById, '/getuser')
api.add_resource(deleteUser, '/delete')
api.add_resource(CheckUserByEmail, '/usercheck')
api.add_resource(getLimitUsers, '')
api.add_resource(login, '/login')
