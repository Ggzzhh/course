#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 作者: Ggzzhh
# 创建时间: 2018/11/6

from random import randint, choice

from .models import db, Choice, Course, Classify, UserVideo, User, Video


class CreateCourse:

    def __init__(self):
        self.user = User.query.first()
        if self.user is None:
            self.user = User(name='测试人员', phone='18737532369', password='123')
            db.session.add(self.user)
        if not Classify.query.all():
            cls1 = Classify(name='测试1')
            cls2 = Classify(name='测试2')
            db.session.add(cls1)
            db.session.add(cls2)
        self.base_num = 100
        db.session.commit()
        self.cls = Classify.query.all()

    @staticmethod
    def random_bool():
        return True if randint(0, 1) else False

    def create_course(self):
        pub = self.random_bool()
        course = Course(
            name='测试课程{}'.format(self.base_num),
            need_exam=False if pub else self.random_bool(),
            need_learn=True if pub else self.random_bool(),
            is_public=pub
        )
        self.base_num += 1
        course.classify = choice(self.cls)
        _choice = self._create_choice(course)
        db.session.add(course)
        db.session.add(_choice)
        db.session.commit()

    def _create_choice(self, course):
        return Choice(user=self.user, course=course)


class CreateVideo:

    def __init__(self):
        self.courses = Course.query.all()
        self.user = User.query.first()
        self.srcs = ['/static/videos/pig1.mp4', '/static/videos/pig2.mp4', '/static/videos/pig3.mp4']

    def create_video(self):
        src = choice(self.srcs)
        course = choice(self.courses)
        video = Video(
            title='测试用标题{}'.format(randint(1, 10000)),
            duration=randint(200, 400),
            video_src=src,
            course=course)
        ch = Choice.query.filter_by(course_id=course.id).first()
        ch.update_nums()
        return video

    def _create_u_v(self, video):
        return UserVideo(user=self.user, video=video, duration=video.duration)

    def run(self, num=1):
        for i in range(num):
            video = self.create_video()
            self._create_u_v(video)






