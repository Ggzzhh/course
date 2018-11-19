#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# 作者: Ggzzhh
# 创建时间: 2018/11/14

from flask import url_for, render_template, current_app, request, abort, redirect
from flask_login import login_manager, login_user, current_user, logout_user

from . import admin
from app import db
from app.decorators import admin_required
from app.models import User, Classify, Course
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
            'text': '新增课程',
            'link': url_for('admin.add_course')
        }
    ]
    if request.method == 'POST':
        form = request.form.to_dict()
        img = request.files.get('img')
        course = Course.get_json(form)
        db.session.commit()
        # 存储图片并返回地址
        img_src = save_to_static(img, 'test.jpeg')
        print(img_src)
    classifies = Classify.all_to_list(True)
    return render_template('admin/add_course.html',
                           route=route,
                           classifies=classifies)


@admin.route('/course-manage/list')
@admin_required
def course_list():
    return render_template('admin/course_list.html')


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
    if not current_user.is_administrator:
        return abort(403)
    return render_template('admin/setting.html')



