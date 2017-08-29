from marshmallow_jsonapi import Schema, fields
from marshmallow import validate
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from app import CRUD

# print CRUD
from app import db

# class tbl_category
class tbl_category(db.Model, CRUD):
    id = db.Column(db.Integer, primary_key = True)
    id_category = db.Column(db.Integer, nullable = False)
    name_category = db.Column(db.String(100), nullable = False)
    createDate = db.Column(db.TIMESTAMP, default=func.now(), nullable=False)
    updateDate = db.Column(db.TIMESTAMP, default=func.now(), nullable=True)

    def __init__(self, id_category, name_category):
        self.id_category = id_category
        self.name_category = name_category
        # self.createDate = createDate
        # self.updateDate = updateDate

class category_schema(Schema):
    id = fields.Integer(dump_only = True)
    id_category = fields.Integer()
    name_category = fields.String()
    # createDate = fields.Date()
    # updateDate = fields.Date()
    
    class Meta:
        type_ = 'category'
    
