import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Operations:
    CONFIRM = 'confirm' #确认认证邮箱
    RESET_PASSWORD = 'reset-password' #重置密码
    CHANGE_EMAIL = 'change-email' #更改电子邮件

class BaseConfig(object):
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('管理员', MAIL_USERNAME)

    ALBUMY_UPLOAD_PATH = os.path.join(basedir, 'uploads')  # 将上传的文件保存到程序的根目录 'uploads' 中

    ALBUMY_PHOTO_PER_PAGE = 6                             # 每页照片数量
    ALBUMY_PHOTO_SIZE = {'x':350,'small': 400, 'medium': 800}      # 设置剪裁的小型文件与中型文件的尺寸
    ALBUMY_PHOTO_SUFFIX = {
        ALBUMY_PHOTO_SIZE['x']: '_x',                  # 设置图片后缀
        ALBUMY_PHOTO_SIZE['small']: '_s',                  # 小型缩略图 - 后缀
        ALBUMY_PHOTO_SIZE['medium']: '_m',                 # 中型图标 - 后缀
    }

                                                            # 上传文件大小配置【服务器端验证】
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024                    # 文件大小超过3 Mb将返回413错误响应【服务器端验证】

    # 上传图片配置【本地验证】
    DROPZONE_ALLOWED_FILE_TYPE = 'image'                    # 允许上传的文件类型
    DROPZONE_MAX_FILE_SIZE = 3                              # 文件最大体积，单位：M
    DROPZONE_MAX_FILES = 30                                 # 单次最大上传数量
    DROPZONE_ENABLE_CSRF = True                             # 是否开启CSRF上传保护（ 依赖 Flask_wtf 提供的 CSRFProtect ）
    DROPZONE_DEFAULT_MESSAGE = '请将文件拖到此处放置或单击以上传'  # 自定义上传区域文字

    # 设置用户头像的配置变量
    AVATARS_SAVE_PATH = os.path.join(ALBUMY_UPLOAD_PATH, 'avatars')  # 设置用户头像本地保存路径（保存到根目录上传文件夹的avatars目录中）
    AVATARS_SIZE_TUPLE = (30, 100, 200)

    SECRET_KEY = os.getenv('SECRET_KEY','div key')          #秘钥
    SQLALCHEMY_TRACK_MODIFICATIONS = False                  # 数据库修改跟踪

    BLUELOG_POST_PER_PAGE = 10                              #页码




class DevelopmentConfig(BaseConfig):  #开发数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.db')
    REDIS_URL = "redis://localhost"


class ProductionConfig(BaseConfig):  #生产数据库
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL','sqlite:///' + os.path.join(basedir, 'data.db'))


config = {'development': DevelopmentConfig,  'production': ProductionConfig,}