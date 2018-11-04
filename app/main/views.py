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


@main.route('/exam/<int:course_id>/detail')
def exam_detail(course_id):
    detail = {
        'course_id': course_id,
        'course': '学习十八大重要讲话',
        'exam_time': 45,
        'total_score': 100,
        'question_type': {
            'judge': {
                'nums': 10,
                'score': 3,
            },
            'single_selection': {
                'nums': 10,
                'score': 3
            },
            'multi_selection': {
                'nums': 10,
                'score': 4
            }
        }
    }
    return render_template('main/exam_detail.html', page_title=current_app.config['SYSTEMNAME'],
                           detail=detail)


@main.route('/exam/<int:exam_id>/progress')
def exam(exam_id):
    return '考卷'


@main.route('/course/<int:course_id>/video')
def course_video(course_id):
    videos = [
        {
            'title': '小猪佩奇11111111111111',
            'src': '../../static/videos/pig1.mp4',
            'percent': '58',
            'duration': '5:03'
        },
        {
            'title': '小猪佩奇2222222222222221231231231232222222222223333333',
            'src': '../../static/videos/pig2.mp4',
            'percent': '81',
            'duration': '5:03'
        },
        {
            'title': '小猪佩奇3',
            'src': '../../static/videos/pig3.mp4',
            'percent': '3',
            'duration': '5:03'
        }
    ]
    return render_template('main/play_video.html', videos=videos)


@main.route('/user/learn_center')
def learn_center():
    course = {
        'title': '学习十八大重要讲话',
        'newstime': '2018-11-12',
        'classify': '学习、考试',
        'total_time': '200',
        'img_url': '../../static/images/bg.jpg',
        'url': url_for('main.course_detail', id=1)
    }
    return render_template('user/learn_center.html', course=course)


@main.route('/user/examination')
def examination():
    exam = {
        'title': '学习十八大重要讲话',
        'exam_time': 90,
        'newstime': '2018-11-12',
        'img_url': '../../static/images/bg.jpg',
        'url': url_for('main.course_detail', id=1),
        'exam_url': url_for('main.exam_detail', course_id=1)
    }
    return render_template('user/examination.html', exam=exam)


@main.route('/user/exercise')
def exercise():
    exam = {
        'title': '学习十八大重要讲话',
        'exam_time': 90,
        'newstime': '2018-11-12',
        'img_url': '../../static/images/bg.jpg',
        'url': url_for('main.course_detail', id=1),
        'exam_url': url_for('main.exam_detail', course_id=1)
    }
    return render_template('user/exercise.html', exam=exam)


@main.route('/user/archives')
def archives():
    return render_template('user/archives.html')

@main.route('/user/info')
def info():
    return render_template('user/info.html')