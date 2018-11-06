#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 作者: Ggzzhh
# 创建时间: 2018/10/22

from datetime import datetime

from flask_login import UserMixin, AnonymousUserMixin

from . import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# 权限类
class Permission:
    LEARN = 0x01  # 可以学习
    ADD_COURSE = 0x03  # 可以增加课程以及试卷
    ADMINISTRATOR = 0xff  # 管理员权限


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permissions = db.Column(db.Integer)
    default = db.Column(db.Boolean, default=False, index=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_role():
        roles = {
            'User': (Permission.LEARN, True),
            'Moderator': (Permission.ADD_COURSE, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                # 如果用户角色没有创建: 创建用户角色
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


class AnonymousUser(AnonymousUserMixin):

    @staticmethod
    def can(permissions):
        return False

    @staticmethod
    def is_administrator():
        return False

    @staticmethod
    def is_user():
        return False

    @staticmethod
    def is_moderator():
        return False


login_manager.anonymous_user = AnonymousUser


class Choice(db.Model):
    __tablename__ = 'choices'

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.update_nums()

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), primary_key=True)
    video_nums = db.Column(db.Integer, default=0)
    finish_nums = db.Column(db.Integer, default=0)
    newstime = db.Column(db.Date, default=datetime.now().date())

    def update_nums(self):
        if self.course:
            self.video_nums = len(self.course.videos.all())
            db.session.add(self)
            db.session.commit()


class UserVideo(db.Model):
    __tablename__ = 'user_videos'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), primary_key=True)
    duration = db.Column(db.Integer, default=0)
    learn_time = db.Column(db.Integer, default=0)
    learn_status = db.Column(db.Boolean, default=False)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    phone = db.Column(db.String(11), unique=True)
    password = db.Column(db.String(64), nullable=False)
    choices = db.relationship('Choice',
                              foreign_keys=[Choice.user_id],
                              backref=db.backref('user', lazy='joined'),
                              lazy='dynamic'
                              )
    u_videos = db.relationship('UserVideo',
                              foreign_keys=[UserVideo.user_id],
                              backref=db.backref('user', lazy='joined'),
                              lazy='dynamic'
                              )
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTRATOR)

    def is_user(self):
        return self.can(Permission.LEARN)

    def is_moderator(self):
        return self.can(Permission.ADD_COURSE)

    def __repr__(self):
        return '<用户 %r>' % self.name


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    need_exam = db.Column(db.Boolean, default=False)
    need_learn = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=False)
    # 课程总时长 计算分钟数
    duration = db.Column(db.Integer, default=0)
    classify_id = db.Column(db.Integer, db.ForeignKey('classifies.id'))
    videos = db.relationship('Video',
                             backref='course',
                             lazy='dynamic',
                             cascade='all, delete-orphan')
    choices = db.relationship('Choice',
                              foreign_keys=[Choice.course_id],
                              backref=db.backref('course', lazy='joined'),
                              lazy='dynamic'
                              )

    def __repr__(self):
        return '<课程 %r>' % self.name


class Video(db.Model):
    __tablename__ = 'videos'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256))
    # 总时长 按秒计算
    duration = db.Column(db.Integer)
    video_src = db.Column(db.String(512))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    u_videos = db.relationship('UserVideo',
                               foreign_keys=[UserVideo.video_id],
                               backref=db.backref('video', lazy='joined'),
                               lazy='dynamic'
                               )

    def __repr__(self):
        return '<视频 %r>' % self.title


class Classify(db.Model):
    __tablename__ = 'classifies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    courses = db.relationship('Course', backref='classify', lazy='dynamic')

    def __repr__(self):
        return '<视频 %r>' % self.title

    __str__ = __repr__

