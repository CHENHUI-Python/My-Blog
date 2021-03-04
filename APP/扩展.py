from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_avatars import Avatars
from flask_login import LoginManager
from flask_moment import Moment
from flask_ckeditor import CKEditor
from flask_wtf import CSRFProtect
from flask_mail import Mail

from flask_dropzone import Dropzone


db = SQLAlchemy()
bootstrap = Bootstrap()
avatars = Avatars()
login = LoginManager()
moment = Moment()
ckeditor = CKEditor()
csrf = CSRFProtect()
mail = Mail()

dropzone = Dropzone()


@login.user_loader
def load_user(user_id):
    from APP.数据库 import User
    user = User.query.get(user_id)
    return user

login.login_view = 'user.login'
login.login_message = '需要登录后才能访问'