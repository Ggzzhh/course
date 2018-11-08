#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 作者: Ggzzhh
# 创建时间: 2018/10/22

from datetime import datetime

from flask import url_for
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
    def can(self):
        return False

    @property
    def is_administrator(self):
        return False

    @property
    def is_user(self):
        return False

    @property
    def is_moderator(self):
        return False

    @staticmethod
    def has_course():
        return False


login_manager.anonymous_user = AnonymousUser


class Choice(db.Model):
    __tablename__ = 'choices'

    def __init__(self, **kwargs):
        super(Choice, self).__init__(**kwargs)
        self.update_nums()

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), primary_key=True)
    video_nums = db.Column(db.Integer, default=0)
    finish_nums = db.Column(db.Integer, default=0)
    last_seen = db.Column(db.DateTime, default=datetime.now())

    def to_json(self):
        data = {
            'user_id': self.user_id,
            'course_id': self.course_id,
            'course_name': self.course.name if self.course else None,
            'course_url': url_for('main.course_detail', id=self.course_id),
            'newstime': self.course.newstime if self.course else None,
            'is_pass': '已通过' if self.is_pass() else '未通过',
            'learn_rate': self.learn_rate()
        }
        return data

    def is_pass(self):
        self.update_nums()
        return False if self.video_nums == 0 else self.finish_nums >= self.video_nums

    def update_nums(self):
        if self.course:
            self.video_nums = len(self.course.videos.all())
            db.session.add(self)
            db.session.commit()

    def update_seen(self):
        self.last_seen = datetime.now()
        db.session.add(self)
        db.session.commit()

    def learn_rate(self):
        if self.finish_nums < 1:
            return 0
        self.update_nums()
        return round(self.finish_nums / self.video_nums * 100)


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

    def to_json(self):
        current_choice = self.choices.order_by(Choice.last_seen.desc()).first()

        if current_choice:
            current_choice = current_choice.to_json()
        else:
            current_choice = {
                'user_id': None,
                'course_id': None,
                'course_name': '没有正在学习的课程,请尽快选课',
                'course_url': '#',
                'newstime': '',
                'is_pass': '',
                'learn_rate': 0
            }

        data = {
            'name': self.name,
            'phone': self.phone,
            'current_choice': current_choice,
        }
        return data

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def get_course_percent(self, course_id):
        res = self.get_choice_course(course_id)
        return res.learn_rate() if res else 0

    def has_course(self, course_id):
        return True if self.get_choice_course(course_id) else False

    def get_choice_course(self, course_id):
        return self.choices.filter(Choice.course_id == course_id).first()

    @property
    def is_administrator(self):
        return self.can(Permission.ADMINISTRATOR)

    @property
    def is_user(self):
        return self.can(Permission.LEARN)

    @property
    def is_moderator(self):
        return self.can(Permission.ADD_COURSE)

    def __repr__(self):
        return '<用户 %r>' % self.name


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    img_url = db.Column(db.String(256), default='/static/images/bg.jpg')
    need_exam = db.Column(db.Boolean, default=False)
    need_learn = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=False)
    newstime = db.Column(db.Date, default=datetime.now().date())
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

    def to_json(self):
        data = {
            'id': self.id,
            'name': self.name,
            'classify': self.classify.name if self.classify else None,
            'type': self.get_type(),
            'duration': self.duration,
            'newstime': self.newstime,
            'img_url': self.img_url
        }
        return data

    @staticmethod
    def filter_type(query, _type):
        if _type == 'public':
            return query.filter(Course.is_public == 1)
        if _type == 'exam':
            return query.filter(
                Course.need_exam == 1,
                Course.is_public == 0,
                Course.need_learn == 0
            )
        if _type == 'learn':
            return query.filter(
                Course.need_exam == 0,
                Course.is_public == 0,
                Course.need_learn == 1
            )
        if _type == 'all':
            return query.filter(
                Course.need_exam == 1,
                Course.is_public == 0,
                Course.need_learn == 1
            )
        return query

    def get_type(self):

        if self.is_public:
            res = '公共'
        elif self.need_exam and self.need_learn:
            res = '培训'
        elif not self.need_learn and self.need_exam:
            res = '考试'
        elif self.need_learn and not self.need_exam:
            res = '学习'
        else:
            res = ''
        return res



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

    @staticmethod
    def all_to_list():
        cls = Classify.query.order_by(Classify.id).all()
        return [c.name for c in cls]

    def __repr__(self):
        return '<课程分类 %r>' % self.name

    __str__ = __repr__

