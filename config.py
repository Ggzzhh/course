# -*- coding: utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """基础配置，导入所有配置中"""
    # 数据库账号
    SQL_USERNAME = 'root'

    # 数据库密码
    SQL_PASSWORD = 'Gg657000'

    # 密匙
    SECRET_KEY = os.environ.get('SECRET_KEY') or "W2s4S4sa2FS96Ok"

    # 超级管理员账号 默认为skzzk 可修改 第一次运行时会自动注册
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'skzzk'
    # 超级管理员密码 默认为skzzk 可修改 第一次运行时会自动注册
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'skzzk'

    # 数据库自动提交数据
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # 如果设置成 True (默认情况)，Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。
    # 这需要额外的内存， 如果不必要的可以禁用它。
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # 查询耗时过长的时间
    SLOW_DB_QUERY_TIME = 0.5

    # 可以用于显式地禁用或者启用查询记录
    SQLALCHEMY_RECORD_QUERIES = True

    # SSL安全协议开关 False会打开
    SSL_DISABLE = True

    # 禁止转换asc码
    JSON_AS_ASCII = False

    # 存储图片的位置
    # windows用'app\static\image'  linux用'app//static//image' 或自定义
    UPLOAD_FOLDER = 'app//static//image'

    # 分页设置 每页显示数量

    # 系统名称
    SYSTEMNAME = '三会一课'

    # 配置类可以定义 init_app() 类方法，其参数是程序实例。
    # 在这个方法中，可以执行对当前 环境的配置初始化。
    # 现在，基类 Config 中的 init_app() 方法为空。
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """开发配置 以及开发时使用的数据库地址"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = \
        'mysql+pymysql://root:65700@localhost:3306/course?charset=utf8'


class TestingConfig(Config):
    """测试配置 以及测试时使用的数据库地址"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    """正常使用时的配置 以及数据库地址 发生错误时自动发送邮件"""
    SQLALCHEMY_DATABASE_URI = \
        'mysql+pymysql://root:65700@localhost:3306/course?charset=utf8'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}