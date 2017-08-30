from marshmallow_jsonapi import Schema, fields
from marshmallow import validate
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from app import CRUD
# from app.models.m_users import tbl_users

# print CRUD
from app import db

#create table realtion
class tbl_interested(db.Model, CRUD):
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, db.ForeignKey('tbl_users.id'))
    id_item = db.Column(db.Integer, db.ForeignKey('tbl_item.id'))

    def __init__(self, userid, id_item):
        self.userid = userid
        self.id_item = id_item

# class tbl_category
class tbl_category(db.Model, CRUD):
    id = db.Column(db.Integer, primary_key = True)
    # id_category = db.Column(db.Integer, nullable = False)
    name_category = db.Column(db.String(100), nullable = False)
    createDate = db.Column(db.TIMESTAMP, default=func.now(), nullable=False)
    updateDate = db.Column(db.TIMESTAMP, default=func.now(), nullable=False)
    isDelete = db.Column(db.Boolean, default=False, nullable=True)
    choose = db.relationship('tbl_item', backref='tbl_category', lazy='dynamic')


    def __init__(self, id, name_category):
        self.id = id
        self.name_category = name_category
        # self.createDate = createDate
        # self.updateDate = updateDate

class category_schema(Schema):
    id = fields.Integer(dump_only = True)
    # id_category = fields.Integer()
    name_category = fields.String()
    # createDate = fields.Date()
    # updateDate = fields.Date()
    
    class Meta:
        type_ = 'category'
    
class tbl_item(db.Model, CRUD):
    id = db.Column(db.Integer, primary_key = True)
    # id_item = db.Column(db.Integer, nullable=False)
    name_item = db.Column(db.String(100), nullable= False)
    createDate = db.Column(db.TIMESTAMP, default=func.now(), nullable=False)
    updateDate = db.Column(db.TIMESTAMP, default=func.now(), nullable=False)
    isDelete = db.Column(db.Boolean, default=False, nullable=True)
    id_category = db.Column(db.Integer, db.ForeignKey('tbl_category.id'))
    choose = db.relationship('tbl_choose_category', backref='tbl_item', lazy='dynamic') 
    
    def __init__(self, id, name_item):
        self.id = id
        self.name_item =name_item

class item_schema(Schema):
    id = fields.Integer(dump_only = True)
    # id_category = fields.Integer()
    name_item = fields.String()

    class Meta:
        type_ = 'item'

