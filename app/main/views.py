#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# 作者: Ggzzhh
# 创建时间: 2018/10/22

from flask import jsonify, redirect, render_template, url_for, current_app, request

from flask_login import login_user, logout_user, login_required

from . import main


@main.route('/')
# @login_required
def index():
    classifies = ['党建', '十八大', '等等等', '四矿']
    return render_template('main/index.html',
                           page_title=current_app.config['SYSTEMNAME'], classifies=classifies)


@main.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        data = request.data
        print(data)
        return redirect(url_for('main.index'))
    return render_template('main/login.html', page_title=current_app.config['SYSTEMNAME'])


@main.route('/course/<int:id>/detail')
def course_detail(id):
    course = {
        'title': '学习十八大重要讲话',
        'newstime': '2018-11-12',
        'classify': '学习、考试',
        'total_time': '200',
        'img_url': '../../static/images/bg.jpg'
    }
    return render_template('main/detail.html', page_title=current_app.config['SYSTEMNAME'],
                           course=course)
