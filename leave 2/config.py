import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'pass1234#&')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '91111mike@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD','iwcx escz hcve xbng')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER','91111mike@gmail.com')
