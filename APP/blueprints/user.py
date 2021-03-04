import os
from flask import Blueprint
from flask import render_template,flash,redirect,url_for,request,current_app
from flask_login import current_user,login_user,logout_user,login_required
from APP.forms.表单 import RegisterForm,LoginForm,CategoryForm,CommentForm,NoteForm
from APP.forms.表单 import EditNoteForm,EditUserForm,ChangePasswordForm
from APP.数据库 import User,Note,Category,Comment,Photo
from APP.扩展 import db
from APP.工具 import redirect_back,resize_image

from flask_dropzone import random_filename


user_bp = Blueprint('user',__name__)


@user_bp.route('/index/<username>')
@login_required
def index(username):
    user = User.query.filter_by(username=username).first()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ALBUMY_PHOTO_PER_PAGE']
    pagination = Note.query.with_parent(user).order_by(Note.timestamp.desc()).paginate(page, per_page)
    notes = pagination.items
    return render_template('user/index.html',notes=notes,pagination=pagination,user=user)

@user_bp.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        username = form.username.data
        user = User(name=name,username=username)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('恭喜你注册成功','success')
        return redirect(url_for('index.index'))
    return render_template('user/register.html',form=form)


@user_bp.route('/change_password',methods=['GET','POST'])
def change_password():
    form = ChangePasswordForm()
    user = User.query.filter_by(username=current_user.username).first()
    if form.validate_on_submit():
        if user.validate_password(form.password.data):
            user.set_password(form.change_password.data)
            db.session.commit()
            flash('密码修改成功','info')
            return redirect(url_for('user.index', username=current_user.username))
        flash('原密码错误，请再试一次','danger')
        return redirect_back()
    return render_template('user/change_password.html',form=form)


@user_bp.route('/edit_user',methods=['GET','POST'])
@login_required
def edit_user():
    form = EditUserForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('修改资料成功','info')
        return redirect(url_for('user.index',username=current_user.username))
    form.name.data = current_user.name
    form.bio.data = current_user.bio
    return render_template('user/edit_user.html',form=form)


@user_bp.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        b = form.b.data
        if user is not None and user.validate_password(form.password.data):
            login_user(user, b)
            flash('登陆成功', 'info')
            return redirect_back()
        flash('用户名或密码不匹配','danger')
    return render_template('user/login.html',form=form)


@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('注销成功','info')
    return redirect(url_for('index.index'))


@user_bp.route('/new_note',methods=['GET','POST'])
@login_required
def new_note():
    form = NoteForm()
    if form.validate_on_submit():
        title = form.title.data
        category = Category.query.get(form.category.data)
        body = form.body.data
        note = Note(
            title=title,
            categorys=category,
            body=body,
            users=current_user._get_current_object()
            ) #当前用户的真实代理对象
        db.session.add(note)
        db.session.commit()

        f = form.photo.data
        filename = random_filename(f.filename)
        f.save(os.path.join(current_app.config['ALBUMY_UPLOAD_PATH'], filename))
        filename_x = resize_image(f, filename, 350)

        photo = Photo(filename=filename,
                      filename_x=filename_x,
                      ) #users=current_user._get_current_object()
        photo.notes = note
        db.session.add(photo)
        db.session.commit()

        flash('帖子发表成功','info')
        return redirect(url_for('index.index'))
    return render_template('user/new_note2.html',form=form)


@user_bp.route('/new_note2',methods=['GET','POST'])
def new_note2():
    form = EditNoteForm()
    if form.validate_on_submit():
        title = form.title.data
        category = Category.query.get(form.category.data)
        body = form.body.data
        note = Note(
            title=title,
            categorys=category,
            body=body,
            users=current_user._get_current_object()
        )  # 当前用户的真实代理对象
        db.session.add(note)
        db.session.commit()
        flash('帖子发表成功', 'info')
        return redirect(url_for('index.index'))
    return render_template('user/new_note.html', form=form)


@user_bp.route('/new_category',methods=['GET','POST'])
@login_required
def new_category():
    form = CategoryForm()
    category = Category.query.all()
    if form.validate_on_submit():
        name = form.name.data
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        flash('成功添加一条分类','info')
        return redirect_back()
    return render_template('admin/new_category.html',form=form,category=category)


@user_bp.route('/show_note/<int:note_id>',methods=['GET','POST'])
def show_note(note_id):
    note = Note.query.get(note_id)
    form = CommentForm()
    if form.validate_on_submit():
        body = form.body.data
        comment = Comment(body=body,note_id=note_id,user=current_user._get_current_object())
        db.session.add(comment)
        db.session.commit()
        return redirect_back()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ALBUMY_PHOTO_PER_PAGE']
    pagination = Comment.query.with_parent(note).order_by(Comment.timestamp.desc()).paginate(page, per_page)
    comments = pagination.items
    return render_template('user/show_note.html',note=note,form=form,comments=comments,pagination=pagination)


@user_bp.route('/can_comment/<int:note_id>',methods=['POST'])
@login_required
def can_comment(note_id):
    note = Note.query.get(note_id)
    if note.can_comment:
        note.can_comment = False
        flash('评论区已关闭','info')
    else:
        note.can_comment = True
        flash('评论区已开启','info')
    db.session.commit()
    return redirect_back()



@user_bp.route('/show_category/<int:category_id>')
@login_required
def show_category(category_id):
    category = Category.query.get(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ALBUMY_PHOTO_PER_PAGE']
    pagination = Note.query.with_parent(category).order_by(Note.timestamp.desc()).paginate(page, per_page)
    notes = pagination.items
    return render_template('user/show_category.html',notes=notes,pagination=pagination,category=category)


@user_bp.route('/edit_note/<int:note_id>',methods=['GET','POST'])
def edit_note(note_id):
    form = EditNoteForm()
    notes = Note.query.get(note_id)
    if form.validate_on_submit():
        notes.title = form.title.data
        notes.categorys = Category.query.get(form.category.data)
        notes.body = form.body.data
        db.session.commit()
        flash('编辑成功','info')
        return redirect(url_for('user.index',username=notes.users.username))
    form.title.data = notes.title
    form.category.data = notes.category_id
    form.body.data = notes.body
    return render_template('user/new_note.html',form=form)


@user_bp.route('/delete_note/<int:note_id>',methods=['POST'])
def delete_note(note_id):
    notes = Note.query.get(note_id)
    db.session.delete(notes)
    db.session.commit()
    flash('成功删除了一篇文章','info')
    return redirect_back()

@user_bp.route('/delete_comment/<int:comment_id>',methods=['POST'])
def delete_comment(comment_id):
    comments = Comment.query.get(comment_id)
    db.session.delete(comments)
    db.session.commit()
    flash('成功删除一条评论','info')
    return redirect_back()

@user_bp.route('/delete_category/<int:category_id>',methods=['POST'])
def delete_category(category_id):
    categorys = Category.query.get(category_id)
    db.session.delete(categorys)
    db.session.commit()
    flash('成功删除一条分类','info')
    return redirect_back()