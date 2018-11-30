#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# 作者: Ggzzhh
# 创建时间: 2018/11/14

from flask import url_for, render_template, current_app, request, abort, redirect
from flask_login import login_manager, login_user, current_user, logout_user

from . import admin
from app import db
from app.decorators import admin_required
from app.models import User, Classify, Course, Video
from app.tools import save_to_static

login_manager.login_view = 'admin.login'


@admin.route('/')
@admin_required
def index():
    return render_template('admin/base.html')


@admin.route('/login', methods=["GET", "POST"])
def login():
    logout_user()
    msg = request.args.get('msg', default='')
    if current_user.is_moderator:
        return redirect(url_for('admin.index'))
    if request.method == 'POST':
        form = request.form
        username = form.get('username')
        password = form.get('password')
        user = User.query.filter(User.name == username, User.password == password).first()
        if user:
            if user.is_moderator:
                login_user(user)
                return redirect(url_for('admin.index'))
            else:
                return abort(403)
        else:
            msg = '账号或密码错误！请重试！'
    admin_title = current_app.config['SYSTEMNAME'] + '后台管理系统'
    return render_template('admin/login.html', admin_title=admin_title, msg=msg)


@admin.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('admin.login', msg='账号已注销！'))


@admin.route('/index')
@admin_required
def frm_index():
    route = [
        {
            'type': 'link',
            'text': '首页',
            'link': url_for('admin.frm_index')
        }
    ]
    return render_template('admin/index.html', route=route)


@admin.route('/course-manage/add', methods=["GET", "POST"])
@admin_required
def add_course():
    route = [
        {
            'type': 'text',
            'text': '课程管理'
        },
        {
            'type': 'link',
            'text': '课程新增',
            'link': url_for('admin.add_course')
        }
    ]
    if request.method == 'POST':
        form = request.form.to_dict()
        img = request.files.get('img')
        course = Course.from_json(form)
        db.session.add(course)
        db.session.commit()
        # 存储图片并返回地址
        img_url = save_to_static(img, 'course{}.jpeg'.format(course.id))
        if img_url:
            course.img_url = img_url
            db.session.add(course)
        return redirect(url_for('admin.course_list'))
    classifies = Classify.all_to_list(True)
    return render_template('admin/add_course.html',
                           route=route,
                           classifies=classifies)


@admin.route('/course-manage/list')
@admin_required
def course_list():
    route = [
        {
            'type': 'text',
            'text': '课程管理'
        },
        {
            'type': 'link',
            'text': '课程列表',
            'link': url_for('admin.course_list')
        }
    ]
    msg = request.args.get('msg', default='')
    page = request.args.get('page', default=1, type=int)
    course_name = request.args.get('courseName', default=None)
    course_status = request.args.get('courseStatus', default=None, type=int)

    query = Course.query

    if course_name is not None:
        query = query.filter(Course.name.like('%{}%'.format(course_name)))
    if course_status is not None and course_status != 2:
        query = query.filter(Course.status == course_status)
    pagination = query.order_by(Course.newstime.desc())\
        .paginate(page, per_page=8, error_out=False)
    next = pagination.next_num
    prev = pagination.prev_num
    total = pagination.pages
    courses = [course.to_json() for course in pagination.items]
    return render_template('admin/course_list.html',
                           route=route,
                           courses=courses,
                           next=next,
                           prev=prev,
                           page=page,
                           total=total,
                           course_name=course_name,
                           course_status=course_status,
                           msg=msg
                           )


@admin.route('/user-manage/add')
@admin_required
def add_user():
    return render_template('admin/add_user.html')


@admin.route('/user-manage/list')
@admin_required
def user_list():
    return render_template('admin/user_list.html')


@admin.route('/system-setting')
@admin_required
def system_setting():
    route = [
        {
            'type': 'text',
            'text': '系统设置'
        }
    ]
    if not current_user.is_administrator:
        return abort(403)
    return render_template('admin/setting.html', route=route)


@admin.route('/course/<int:c_id>', methods=['POST', 'GET'])
@admin_required
def course_manage(c_id):
    route = [
        {
            'type': 'text',
            'text': '课程管理'
        },
        {
            'type': 'link',
            'text': '课程列表',
            'link': url_for('admin.course_list')
        },
        {
            'type': 'link',
            'text': '编辑课程',
            'link': url_for('admin.course_manage', c_id=c_id)
        },
        {
            'type': 'link',
            'text': '基础信息',
            'link': url_for('admin.course_manage', c_id=c_id)
        },
    ]
    course = Course.query.get_or_404(c_id)
    classifies = Classify.all_to_list(True)
    if request.method == 'POST':
        form = request.form.to_dict()
        img = request.files.get('img')
        img_url = save_to_static(img, 'course{}.jpeg'.format(course.id))
        if img_url:
            course.img_url = img_url
        course = Course.from_json(form, course)
        db.session.add(course)
        return redirect(url_for('admin.course_list', msg='保存成功'))
    return render_template('admin/course_edit.html', course=course, route=route, classifies=classifies)


@admin.route('/course/<int:c_id>/video')
@admin_required
def edit_video(c_id):
    route = [
        {
            'type': 'text',
            'text': '课程管理'
        },
        {
            'type': 'link',
            'text': '课程列表',
            'link': url_for('admin.course_list')
        },
        {
            'type': 'link',
            'text': '编辑课程',
            'link': url_for('admin.course_manage', c_id=c_id)
        },
        {
            'type': 'link',
            'text': '视频课件',
            'link': url_for('admin.edit_video', c_id=c_id)
        },
    ]
    course = Course.query.get_or_404(c_id)
    course.update_duration()
    videos = [video.to_json() for video in course.videos.order_by(Video.order.desc(), Video.id).all()]
    return render_template('admin/video_edit.html', route=route, course=course, videos=videos)


@admin.route('/course/<int:c_id>/exam')
@admin_required
def edit_exam(c_id):
    route = [
        {
            'type': 'text',
            'text': '课程管理'
        },
        {
            'type': 'link',
            'text': '课程列表',
            'link': url_for('admin.course_list')
        },
        {
            'type': 'link',
            'text': '编辑课程',
            'link': url_for('admin.course_manage', c_id=c_id)
        },
        {
            'type': 'link',
            'text': '题库及试卷',
            'link': url_for('admin.edit_exam', c_id=c_id)
        },
    ]
    course = Course.query.get_or_404(c_id)
    course.update_duration()
    videos = [video.to_json() for video in course.videos.order_by(Video.order.desc(), Video.id).all()]
    return render_template('admin/exam_edit.html', route=route, course=course, videos=videos)
