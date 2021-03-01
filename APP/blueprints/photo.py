import os
from flask import Blueprint
from flask import request,render_template,redirect,flash,url_for,abort
from flask import current_app,send_from_directory
from flask_login import current_user
from flask_dropzone import random_filename
from APP.扩展 import db,avatars
from APP.工具 import resize_image,redirect_back,flash_errors
from APP.数据库 import Photo,User
from APP.forms.avatars import UploadAvatarForm,CropAvatarForm


photo_bp = Blueprint('photo',__name__)

@photo_bp.route('/show_photo/<username>')
def show_photo(username):
    user = User.query.filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ALBUMY_PHOTO_PER_PAGE']
    pagination = Photo.query.with_parent(user).order_by(Photo.timestamp.desc()).paginate(page, per_page)
    photos = pagination.items
    return render_template('photo/show_photo.html',photos=photos,pagination=pagination,user=user)


@photo_bp.route('/get_photo/<path:filename>')
def get_photo(filename):
    return send_from_directory(current_app.config['ALBUMY_UPLOAD_PATH'],filename)


@photo_bp.route('/upload',methods=['GET','POST'])
def upload():
    if request.method == 'POST' and 'file' in request.files:
        f = request.files.get('file')
        filename = random_filename(f.filename)
        f.save(os.path.join(current_app.config['ALBUMY_UPLOAD_PATH'],filename))

        #调用编写的剪裁函数
        filename_s = resize_image(f,filename,400)
        filename_m = resize_image(f,filename,800)

        #将文件名写入数据库
        photo = Photo(filename=filename,
                      filename_s=filename_s,
                      filename_m=filename_m,
                      users=current_user._get_current_object())
        db.session.add(photo)
        db.session.commit()
    return render_template('photo/photo.html')


@photo_bp.route('/photo/n/<int:photo_id>')
def photo_next(photo_id):
    photo =Photo.query.get(photo_id)
    photo_n = Photo.query.with_parent(photo.users).filter(Photo.id < photo_id).order_by(Photo.id.desc()).first()

    if photo_n is None:
        flash('这已经是最后一张图片了', 'info')
        return redirect(url_for('photo.one_photo', photo_id=photo.id))
    return redirect(url_for('photo.one_photo', photo_id=photo_n.id))


@photo_bp.route('/photo/p/<int:photo_id>')
def photo_previous(photo_id):
    photo = Photo.query.get(photo_id)
    photo_p = Photo.query.with_parent(photo.users).filter(Photo.id > photo_id).order_by(Photo.id.asc()).first()

    if photo_p is None:
        flash('这已经是最后一张图片了','info')
        return redirect(url_for('photo.one_photo', photo_id=photo.id))
    return redirect(url_for('photo.one_photo', photo_id=photo_p.id))


@photo_bp.route('/delete_photo/<int:photo_id>',methods=['POST'])
def delete_photo(photo_id):
    photo = Photo.query.get(photo_id)
    if current_user != photo.users:  # 如果当前用户不是图片作者
        abort(403)

    db.session.delete(photo)
    db.session.commit()
    flash('当前图片已删除','info')


    photo_n = Photo.query.with_parent(photo.users).filter(Photo.id<photo_id).order_by(Photo.id.desc()).first()
    if photo_n is None:
        photo_p = Photo.query.with_parent(photo.users).filter(Photo.id > photo_id).order_by(Photo.id.asc()).first()
        if photo_p is None:
            return redirect(url_for('user.index',username=photo.users.username)) #current_user.id
        return redirect(url_for('photo.one_photo',photo_id=photo_p.id))
    return redirect(url_for('photo.one_photo',photo_id=photo_n.id))


@photo_bp.route('/one_photo/<int:photo_id>')
def one_photo(photo_id):
    photo = Photo.query.get(photo_id)
    return render_template('photo/one_photo.html',photo=photo)

@photo_bp.route('/avatar/<path:filename>')
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'],filename)


@photo_bp.route('/avatar_x')
def avatar():
    upload_form = UploadAvatarForm()
    crop_form = CropAvatarForm()
    return render_template('photo/avatars.html', upload_form=upload_form, crop_form=crop_form)


@photo_bp.route('/upload_avatar',methods=['POST'])
def upload_avatar():
    form = UploadAvatarForm()
    if form.validate_on_submit():
        image = form.image.data
        filename = avatars.save_avatar(image)
        current_user.avatar_raw = filename
        db.session.commit()
        flash('上传头像成功，请剪裁后使用','success')
    flash_errors(form)
    return redirect(url_for('photo.avatar'))

@photo_bp.route('/crop_avatar',methods=['POST'])
def crop_avatar():
    form = CropAvatarForm()
    if form.validate_on_submit():
        x = form.x.data
        y = form.y.data
        w = form.w.data
        h = form.h.data

        filename = avatars.crop_avatar(current_user.avatar_raw, x,y,w,h)
        current_user.avatar_s = filename[0]
        current_user.avatar_m = filename[1]
        current_user.avatar_l = filename[2]
        db.session.commit()
        flash('头像已更新','success')
        return redirect(url_for('user.index',username=current_user.username))
    flash_errors(form)
    return redirect(url_for('photo.avatar'))