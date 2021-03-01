from flask_wtf import FlaskForm
from wtforms import SubmitField

from wtforms import HiddenField
from flask_wtf.file import FileField,FileAllowed,FileRequired

class UploadAvatarForm(FlaskForm):
    image = FileField('上传头像(文件需<=3M)',validators=[FileRequired(),FileAllowed(['jpg','png'],'文件格式应为:jpg或png')])
    submit = SubmitField('确认')

class CropAvatarForm(FlaskForm):
    x = HiddenField()
    y = HiddenField()
    w = HiddenField()
    h = HiddenField()
    submit = SubmitField('剪裁并更新')