from APP.扩展 import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash

from flask_avatars import Identicon


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(30), unique=True)
    email = db.Column(db.String(254),unique=True)
    password_hash = db.Column(db.String(128))
    bio = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime,default=datetime.utcnow)

    confirmed = db.Column(db.Boolean, default=False)  # 验证用户的邮箱认证状态

    # 保存用户头像的3种尺寸的字段
    avatar_s = db.Column(db.String(64))
    avatar_m = db.Column(db.String(64))
    avatar_l = db.Column(db.String(64))
    avatar_raw = db.Column(db.String(64))  # 支持自定义头像字段（储存用户上传的头像文件原图以及文件名)

    notes = db.relationship('Note',back_populates='users', cascade='all' )

    comments = db.relationship('Comment',back_populates='user', cascade='all' )

    photos = db.relationship('Photo',back_populates='users',cascade='all')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.generate_avatar()  # 生成头像

    def generate_avatar(self):
        avatar = Identicon()  # 首先实例化处理头像的扩展包
        filenames = avatar.generate(text=self.username)  # 先使用 generate（）方法获取生成九宫格头像的对象，text参数生成随机文本
        self.avatar_s = filenames[0]  # 然后将生成的3个不同大小文件名分别赋值给User模型的3个字段
        self.avatar_m = filenames[1]  # [0,1,2]分别代表3种不同尺寸
        self.avatar_l = filenames[2]
        db.session.commit()


    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self,password):
        return check_password_hash(self.password_hash,password)


class Note(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(30))
    body = db.Column(db.String(5000))
    can_comment = db.Column(db.Boolean,default=True) #评论区开关
    timestamp = db.Column(db.DateTime,default=datetime.utcnow,index=True)

    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    users = db.relationship('User',back_populates='notes')

    comment = db.relationship('Comment',back_populates='note', cascade='all')

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'),index=True)
    categorys = db.relationship('Category',back_populates='notes')

    photos = db.relationship('Photo',back_populates='notes', cascade='all')


class Comment(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime,default=datetime.utcnow)

    note_id = db.Column(db.Integer,db.ForeignKey('note.id'))
    note = db.relationship('Note',back_populates='comment')

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='comments')


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20),unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    notes = db.relationship('Note',back_populates='categorys')


class Photo(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    description = db.Column(db.String(500)) #关于照片的描述

    filename = db.Column(db.String(64)) #储存正常尺寸文件名称
    filename_s = db.Column(db.String(64)) #储存小尺寸文件名称
    filename_m = db.Column(db.String(64)) #储存中尺寸文件名称

    filename_x = db.Column(db.String(64)) #储存发表文章时的配图【小图】

    timestamp = db.Column(db.DateTime,default=datetime.utcnow) #时间戳（储存图片上传时间）

    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    users = db.relationship('User', back_populates='photos')

    note_id = db.Column(db.Integer,db.ForeignKey('note.id'))
    notes = db.relationship('Note',back_populates='photos')


import   os
from flask import current_app
@db.event.listens_for(Photo, 'after_delete', named=True)
def delete_photos(**kwargs):
    target = kwargs['target']
    for filename in [target.filename,target.filename_s,target.filename_m,target.filename_x]: #首先循环Photo数据库里的文件名记录，获取对象
        if filename is not None: #如果该文件名存在
            path = os.path.join(current_app.config['ALBUMY_UPLOAD_PATH'],filename) #则获取该文件名所对应的本地文件地址
            if os.path.exists(path): #如果上面获取的地址在本地存在
                os.remove(path) #则 移除 对应文件