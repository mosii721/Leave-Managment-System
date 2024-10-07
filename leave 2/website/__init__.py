from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import Config
from os import path

db = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)

    from .admin import admin
    from .auth import auth
    from .user import user        #########################

    app.register_blueprint(admin,url_prefix='/')
    app.register_blueprint(auth,url_prefix='/')
    app.register_blueprint(user,url_prefix='/')

    from .models import Admin,Employee

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'# specifies the default route to be sent to when one tries to access an unauthorized page/ without login in
    login_manager.init_app(app)

    @login_manager.user_loader #Flask-Login uses this function to reload the user object from the user ID stored in the session
    def load_user(id):#This function is defined to load a user from the database
        user = Admin.query.get(int(id)) 
        if user:
            return user
        return  Employee.query.get(int(id)) #

    return app

def create_database(app):
    with app.app_context():
        if not path.exists('website/' + app.config['SQLALCHEMY_DATABASE_URI'].split('/')[-1]):
            db.create_all()
            print('Created Database!')
