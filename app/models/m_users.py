from marshmallow_jsonapi import Schema, fields
from marshmallow import validate
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from app import CRUD

# print CRUD
from app import db


class tbl_users(db.Model, CRUD):
    id = db.Column(db.Integer, primary_key=True)
    # userid = db.Column(db.String(250), nullable=False)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(35), nullable=False)
    firstname = db.Column(db.String(150), default=True)
    lastname = db.Column(db.String(150), nullable=False)
    birthdate = db.Column(db.DATE, nullable=False)
    registerdate = db.Column(db.TIMESTAMP, default=func.now(), nullable=False)
    updateDate = db.Column(db.TIMESTAMP, default=func.now(), nullable=False)
    isactive = db.Column(db.Boolean, default=False, nullable=False)
    isDelete = db.Column(db.Boolean, default=False, nullable=True)
    choose = db.relationship('tbl_choose_category', backref='tbl_users', lazy='dynamic')
    
    def __init__(self, id, email, password, firstname, lastname, birthdate):
        self.id = id
        self.email = email
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.birthdate = birthdate
        # self.registerdate = registerdate
        # self.isactive = isactive


class user_schema(Schema):              #buat ini jika ingin data di tampilkan
    # not_blank = validate.Length(min=1, error='Field cannot be blank')
    id = fields.Integer(dump_only=True)
    # userid = fields.String()    
    email = fields.String()
    password = fields.String()
    firstname = fields.String()
    lastname = fields.String()
    birthdate = fields.Date()       

    class Meta:
        type_ = 'users'


# class tbl_category
