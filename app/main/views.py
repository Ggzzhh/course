#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# 作者: Ggzzhh
# 创建时间: 2018/10/22
from urllib.parse import quote

from flask import jsonify, redirect, render_template, url_for, current_app, request
from flask_login import login_user, logout_user, login_required, current_user

from app.models import User, Classify, Course, Choice, Video, UserVideo
from app.decorators import admin_required, user_required
from . import main


@main.route('/')
def index():
    # 获取查询条件
    page = request.args.get('page', 1, type=int)
    classify = request.args.get('classify')
    order = request.args.get('order', 'desc', type=str)
    course_type = request.args.get('type', 'other')
    # 基础查询
    query = Course.query.join(Classify)
    if classify and classify != '不限':
        query = query.filter(Classify.name == classify)
    if course_type:
        query = Course.filter_type(query, course_type)
    if order == 'desc':
        query = query.order_by(Course.newstime.desc(), Course.id.desc())
    else:
        query = query.order_by(Course.newstime, Course.id.desc())

    pagination = query.paginate(page,
                                per_page=current_app.config['INDEX_PAGE'],
                                error_out=False)
    pers = [per.to_json() for per in pagination.items]

    user_info = {}
    if current_user.is_user:
        user_info = current_user.to_json()
    classifies = Classify.all_to_list()

    return render_template('main/index.html',
                           pagination=pagination,
                           pers=pers,
                           classify=classify,
                           course_type=course_type,
                           order=order,
                           page_title=current_app.config['SYSTEMNAME'],
                           classifies=classifies,
                           user_info=user_info)


@main.route('/login', methods=['POST', 'GET'])
def login():
    next = request.args.get('next')
    msg = ''

    if current_user.is_user:
        return redirect(url_for('main.index'))

    if current_user.is_moderator:
        return '管理页面'

    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(phone=data['phone_num']).first()
        if user:
            if data['password'] == user.password:
                login_user(user)
                return redirect(next if next else url_for('main.index'))
            else:
                msg = '密码错误！请重试！'
        else:
            msg = '用户不存在!'
    return render_template('main/login.html',
                           page_title=current_app.config['SYSTEMNAME'],
                           msg=msg,
                           next=next)


@main.route('/user/logout')
@login_required
def logout():
    logout_user()
    return redirect(request.args.get('next') or url_for('main.index'))


@main.route('/course/<int:id>/detail')
def course_detail(id):
    course = Course.query.get(id)
    if course:
        course = course.to_json()
    return render_template('main/detail.html',
                           page_title=current_app.config['SYSTEMNAME'],
                           course=course,
                           active_page=quote(url_for('main.course_detail', id=id)))


@main.route('/exam/<int:course_id>/detail')
@user_required
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
@user_required
def exam(exam_id):
    return '考卷'


@main.route('/course/<int:course_id>/video')
def course_video(course_id):
    course = Course.query.get_or_404(course_id)
    c_type = course.get_type()
    videos = [video.to_json() for video in course.videos]
    course = course.to_json()
    if c_type == '培训':
        if current_user.is_user:
            choice = current_user.choices.filter(Choice.course_id == course_id).first()
            course['learn_rate'] = choice.learn_rate()
            for video in videos:
                uv = UserVideo.query.filter(
                    UserVideo.user_id == current_user.id,
                    UserVideo.video_id == video['id']
                    ).first()
                if uv:
                    video['percent'] = uv.get_percent()
        else:
            return redirect(
                url_for('main.login',
                        next=url_for('main.course_video', course_id=course_id)))
    return render_template('main/play_video.html', videos=videos, course=course)


@main.route('/user/learn_center')
@user_required
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
@user_required
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
@user_required
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
@user_required
def archives():
    return render_template('user/archives.html')


@main.route('/user/info')
@user_required
def info():
    return render_template('user/info.html')