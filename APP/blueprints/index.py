from flask import Blueprint
from flask import render_template,flash,redirect,url_for,request,current_app
from APP.数据库 import Note
from datetime import datetime

index_bp = Blueprint('index',__name__)


@index_bp.route('/')
def index():
    #notes = Note.query.all()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_POST_PER_PAGE']
    pagination = Note.query.order_by(Note.timestamp.desc()).paginate(page, per_page=per_page)
    notes = pagination.items
    return render_template('index/index.html',notes=notes,pagination=pagination)