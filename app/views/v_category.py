from flask import Blueprint, request, jsonify, make_response
from app.models.m_category import tbl_category, category_schema
from flask_restful import Api, Resource

from sqlalchemy import func, sql
from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

import re, datetime, json, dateutil.parser
from datetime import date, datetime

import random, os

# Blueprint
categories = Blueprint('category', __name__)


category_group_schema = category_schema()

api = Api(categories)


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
            id_category = int(lastId) + 1
            name_category = raw_dict['name_category']
            # createDate = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
            cat = tbl_category(id_category, name_category)
            cat.add(cat)

            resp = {'success':'true'}

        except Exception as err:
            resp = {'success':'false', 'msg': err}
        return resp

#endpoint
api.add_resource(create_category, '/create') #post only