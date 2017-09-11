from flask import Blueprint, request, jsonify, make_response
from app.models.m_category import tbl_category, category_schema, tbl_item, item_schema, tbl_interested
from app import db
from flask_restful import Api, Resource

from sqlalchemy import func, sql, update
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

import re, datetime, json, dateutil.parser
from datetime import date, datetime

import random, os

# Blueprint
categories = Blueprint('category', __name__)

category_group_schema = category_schema()
# item_group_schema = item_schema()

api = Api(categories)

#upload file
app_root = os.path.dirname(os.path.abspath(__file__))

class upload(Resource):
    def post(self):
        target = os.path.join(app_root, 'images/')
        print(target)

        if not os.path.isdir(target):
            os.mkdir(target)


#class endpoint
class create_category(Resource):
    # def get(self):
    #     return "Hi.. this is msg from create_category class with method get"
    def post(self):
        raw_dict = request.get_json(force=True)
        # reqEnv = request.environ
        # http_origin = reqEnv['ORIGIN']

        try :
            lastId = db.session.query(func.max(tbl_category.id)).one()[0]
            if lastId == None : lastId = 0
            id = int(lastId) + 1
            name_category = raw_dict['name_category']
            # createDate = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            data = tbl_category(id, name_category)
            data.add(data)

            resp = {'success':'true'}

        except Exception as err:
            resp = {'success':'false', 'msg': err}
        return resp

class select_category(Resource):
    def get(self):

        select = tbl_category.query.all()
        data = category_schema().dump(select,  many = True).data

        # print data
        dataA = []
        for i in range(len(data['data'])):
            
            data1 =[]
            data1.insert(i, {
                'id_category': data['data'][i]['id'],
                'name_category': data['data'][i]['attributes']['name_category'],
                'img_category':data['data'][i]['attributes']['img_category'],
                'parent':''
                })
            for a in data1:
                dataA.append(a)
        data['data'] = dataA        
        result = data
        return result

#class endpoint
class create_item(Resource):
    def post(self):
        raw_dict = request.get_json(force=True)
        # reqEnv = request.environ
        # http_origin = reqEnv['ORIGIN']

        try :
            lastId = db.session.query(func.max(tbl_item.id)).one()[0]
            if lastId == None : lastId = 0
            id = int(lastId) + 1
            name_item = raw_dict['name_item']
            # createDate = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            data = tbl_item(id, name_item)
            data.add(data)

            resp = {'success':'true'}

        except Exception as err:
            resp = {'success':'false', 'msg': err}
        return resp
    
class select_items(Resource):
    def get(self):
        select = tbl_item.query.all()
        data = item_schema().dump(select,  many = True).data

        # belum selesai joining
        # data1 = []
        # for i in range(len(data['data'][0]['attributes'])):
        #     data2 = []
        #     data2.insert(i, {
        #         'id_item':data['data'][i]['id'],
        #         'name_item':data['data'][i]['name_item'],
        #         'img_item':data['data'][i]['img_item'],
        #         'parent':data['data'][i]['']
        #     })

        return data

class update_category(Resource):
    def patch(self):
        raw_dict = request.get_json(force=True)

        try:
            id_rw = raw_dict['id_category']
            name_rw = raw_dict['name_category']

            updt = db.session.query(tbl_category).filter_by(id = id_rw).update({"name_category" : name_rw})   #script singkat
            # updt = db.session.query(tbl_category).filter_by(id_category=id_rw).first()                #select id first
            # updt.name_category=name_rw             #isi data nya dengan apa
            db.session.commit()

            resp = {'success':'true'}
        except Exception as err:
            resp = {'success':'false', 'msg': err}
        
        return resp

class userchooseitem(Resource):
    def post(self):
        # raw_dict = request.json.get()
        id_user = request.json.get("id_user")
        id_item = request.json.get("id_item")

        try:
            data = tbl_interested(id_user, id_item)
            data.add(data)

            resp = {'success':'true'}

        except Exception as err:
            resp = resp = {'success':'false', 'msg': err}

        return resp




#endpoint categroy
api.add_resource(create_category, '/create') #post only
api.add_resource(select_category, '')
api.add_resource(update_category, '/update')

#endpoint item
api.add_resource(create_item, '/item')
api.add_resource(select_items, '/item')
api.add_resource(userchooseitem, '/userchoose')