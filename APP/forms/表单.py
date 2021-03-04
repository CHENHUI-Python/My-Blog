from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField,PasswordField,BooleanField,SelectField
from wtforms.validators import DataRequired,Length,Regexp,EqualTo,ValidationError,Optional,Email
from flask_ckeditor import CKEditorField

from flask_wtf.file import FileField,FileAllowed,FileRequired

from APP.数据库 import User,Category



class RegisterForm(FlaskForm):
    name = StringField('昵称',validators=[DataRequired(message='用户名不能为空'),Length(1,20)])
    username = StringField('用户名',validators=[DataRequired(),Length(1,30),
                                             Regexp('^[a-zA-Z0-9]*$',message='只允许输入字母与数字')])
    email = StringField('邮箱',validators=[DataRequired(message='邮箱格式不正确'),Length(1,254),Email()])
    password = PasswordField('密码',validators=[DataRequired(),Length(1,128),EqualTo('password2')])
    password2 = PasswordField('确认密码',validators=[DataRequired()])
    submit = SubmitField('确认注册')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已存在')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已存在')


class ChangePasswordForm(FlaskForm):
    password = PasswordField('原密码',validators=[DataRequired(),Length(1,128)])
    change_password = PasswordField('新密码',validators=[DataRequired(),Length(1,128),EqualTo('change_password2')])
    change_password2 = PasswordField('确认密码',validators=[DataRequired()])
    submit = SubmitField('确认更改')


class EmailForm(FlaskForm):
    email = StringField('输入注册时的邮箱',validators=[DataRequired(),Email()])
    submit = SubmitField('确认找回')


class RetrievePasswordForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('新密码', validators=[DataRequired(), Length(1, 128), EqualTo('password2')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('确认')


class EditUserForm(FlaskForm):
    name = StringField('昵称',validators=[DataRequired(),Length(1,20)])
    bio = StringField('个性签名',validators=[DataRequired(),Length(0,50)])
    submit = SubmitField('确认修改')


class LoginForm(FlaskForm):
    username = StringField('用户名',validators=[DataRequired(),Length(1,30)])
    password = PasswordField('密码',validators=[DataRequired(),Length(1,128)])
    b = BooleanField('记住密码')
    SubmitField = SubmitField('登录')


class NoteForm(FlaskForm):
    title = StringField('标题',validators=[DataRequired(),Length(1,30)])
    photo = FileField('上传图片', validators=[FileRequired(),FileAllowed(['jpg', 'jpeg', 'png', 'gif']),Optional()])
    category = SelectField('类别',validators=[DataRequired(),Length(1,30)])
    body = CKEditorField('编辑文章',validators=[DataRequired(),Length(1,5000)])
    submit = SubmitField('发表')

    def __init__(self,*args,**kwargs):
        super(NoteForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name)
                                 for category in Category.query.order_by(Category.name).all()]


class EditNoteForm(FlaskForm):
    title = StringField('标题',validators=[DataRequired(),Length(1,30)])
    category = SelectField('类别',validators=[DataRequired(),Length(1,30)])
    body = CKEditorField('编辑文章',validators=[DataRequired(),Length(1,1000)])
    submit = SubmitField('发表')

    def __init__(self,*args,**kwargs):
        super(EditNoteForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name)
                                 for category in Category.query.order_by(Category.name).all()]


class CommentForm(FlaskForm):
    body = TextAreaField('评论',validators=[DataRequired(),Length(1,200)])
    submit = SubmitField('发表评论')


class CategoryForm(FlaskForm):
    name = StringField('类名',validators=[DataRequired(),Length(1,30)])
    submit = SubmitField('创建分类')

    def validate_category(self,field):
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError('此分类已存在')
