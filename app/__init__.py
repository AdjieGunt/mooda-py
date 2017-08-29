from flask import Flask, Response
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class MyResponse(Response):
    default_mimetype = 'application/xml'


class CRUD():   
    def add(self, resource):
        db.session.add(resource)
        return db.session.commit()   

    def update(self):
        return db.session.commit()

    def delete(self, resource):
        db.session.delete(resource)
        return db.session.commit()

# http://flask.pocoo.org/docs/0.10/patterns/appfactories/
def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    app.response_class = MyResponse

    # from app.models.models import db
    db.init_app(app)

    # Blueprints   
    from app.views.v_users import users    
    app.register_blueprint(users, url_prefix='/api/v1/users')

    from app.views.v_category import categories
    app.register_blueprint(categories, url_prefix='/api/v1/category')

    return app
    