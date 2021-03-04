from flask import Blueprint
from flask import current_app,redirect,render_template,flash,url_for
from flask_login import login_required,current_user
from APP.配置 import Operations
from APP.数据库 import User
from APP.扩展 import db,mail
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature,SignatureExpired

from threading import Thread
from flask_mail import Message


email_bp = Blueprint('email',__name__)

#生成邮箱验证令牌
def generate_token(user,operation,expire_in=None,**kwargs):
    s = Serializer(current_app.config['SECRET_KEY'],expire_in)

    data = {'id':user.id, 'operation':operation}
    data.update(**kwargs)
    return s.dumps(data)

#验证邮箱的令牌
def validate_token(user,token,operation,new_password=None):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except(SignatureExpired,BadSignature):
        return False

    if operation != data.get('operation') or user.id != data.get('id'):
        return False

    if operation == Operations.CONFIRM:
        user.confirmed = True
    elif operation == Operations.RESET_PASSWORD:
        user.set_password(new_password)
    elif operation == Operations.CHANGE_EMAIL:
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if User.query.filter_by(email=new_email).first() is not None:
            return False
        user.email = new_email
    else:
        return False

    db.session.commit()
    return True

#邮箱中点击链接验证令牌的函数
@email_bp.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('index.index'))

    if validate_token(user=current_user,token=token,operation=Operations.CONFIRM):
        flash('验证成功', 'success')
        return redirect(url_for('index.index'))
    else:
        flash('无效令牌','danger')
        return redirect(url_for('index.index'))

#异步发送邮件
def _send_async_mail(app,message):
    with app.app_context():
        mail.send(message)


def send_mail(to, subject, template, **kwargs):
    message = Message(subject, recipients=[to])
    message.body = render_template(template + '.txt', **kwargs)
    message.html = render_template(template + '.html', **kwargs)
    app = current_app._get_current_object()
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr

def send_confirm_email(user, token, to=None): #注册时发送确认电子邮件
    send_mail(subject='Email Confirm', to=to or user.email, template='emails/confirm', user=user, token=token)


def send_reset_password_email(user, token): #发送\重置\密码\电子邮件
    send_mail(subject='Password Reset', to=user.email, template='emails/reset_password', user=user, token=token)