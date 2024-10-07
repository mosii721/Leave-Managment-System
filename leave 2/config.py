import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'pass1234#&')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'example@gmail.com') # add your default mail
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD','password') # add your default mail with your password
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER','example@gmail.com')# add your default mail
