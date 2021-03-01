import os
import click
from flask import Flask,render_template
from APP.配置 import config
from APP.blueprints.index import index_bp
from APP.blueprints.user import user_bp
from APP.blueprints.photo import photo_bp
from APP.扩展 import db,bootstrap,avatars,moment,login,ckeditor,csrf,dropzone


def make_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG','development')

        app = Flask('APP')
        app.config.from_object(config[config_name])

        register_blueprint(app)
        register_command(app)
        register_extend(app)
        register_errors(app)

        return app


def register_blueprint(app):
    app.register_blueprint(index_bp)
    app.register_blueprint(user_bp,url_prefix='/user')
    app.register_blueprint(photo_bp, url_prefix='/photo')


def register_extend(app):
    db.init_app(app)
    bootstrap.init_app(app)
    avatars.init_app(app)
    moment.init_app(app)
    login.init_app(app)
    ckeditor.init_app(app)
    csrf.init_app(app)
    dropzone.init_app(app)


def register_errors(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500



def register_command(app):
    @app.cli.command(help='创建数据库')
    @click.option('--drop',is_flag=True)
    def initdb(drop):
        if drop:
            click.confirm('是否初始化数据库？',abort=True)
            db.drop_all()
            click.echo('数据库已删除')
        db.create_all()
        click.echo('数据库初始化已完成')

