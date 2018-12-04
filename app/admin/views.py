#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# 作者: Ggzzhh
# 创建时间: 2018/11/14

from flask import url_for, render_template, current_app, request, abort, redirect, jsonify
from flask_login import login_manager, login_user, current_user, logout_user

from . import admin
from app import db
from app.decorators import admin_required
from app.models import User, Classify, Course, Video, RadioBank, \
    JudgeBank, MultipleBank, Choice, Role
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
    user_phone = request.args.get('phone', default=None, type=int)
    user = User.query.filter_by(phone=user_phone).first()

    query = Course.query

    if user is not None:
        query = query.join(Choice).filter(Choice.user == user)
    if course_name is not None:
        query = query.filter(Course.name.like('%{}%'.format(course_name)))
    if course_status is not None and course_status != 2:
        query = query.filter(Course.status == course_status)
    pagination = query.order_by(Course.newstime.desc()) \
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


@admin.route('/course-manage/classify', methods=["POST", "GET", "DELETE"])
@admin_required
def manage_classify():
    route = [
        {
            'type': 'text',
            'text': '课程管理'
        },
        {
            'type': 'link',
            'text': '课程分类',
            'link': url_for('admin.manage_classify')
        }
    ]
    _id = request.args.get('cls_id')
    if _id:
        cls = Classify.query.get_or_404(_id)
    else:
        cls = None
    if request.method == "DELETE":
        if cls:
            db.session.delete(cls)
            return jsonify({
                'resCode': 'ok',
                'msg': '删除成功!'
            })
        else:
            return jsonify({
                'resCode': 'error',
                'msg': '删除失败!目标不存在!'
            })
    if request.method == "POST":
        name = request.args.get('name')
        if cls:
            cls.name = name
            db.session.add(cls)
            return jsonify({
                'resCode': 'ok',
                'msg': '修改成功!'
            })
        else:
            cls = Classify(name=name)
            db.session.add(cls)
            return jsonify({
                'resCode': 'ok',
                'msg': '新增成功!'
            })
    classifies = Classify.all_course_num()
    return render_template('admin/classify.html', classifies=classifies, route=route)


@admin.route('/user-manage/add', methods=["POST", "GET"])
@admin_required
def add_user():
    msg = ''
    route = [
        {
            'type': 'text',
            'text': '人员管理'
        },
        {
            'type': 'link',
            'text': '人员新增',
            'link': url_for('admin.add_user')
        }
    ]
    if request.method == "POST":
        form = request.form.to_dict()
        phone = form.get('phone')
        ex_phone = User.query.filter_by(phone=phone).all()
        pwd = form.get('password')
        if ex_phone:
            msg = "新增失败！电话号码已存在！"
        elif pwd == "" or phone == "":
            msg = "新增失败！电话号码或者密码为空！"
        elif len(phone) != 11:
            msg = "新增失败！电话号码位数错误！"
        else:
            user = User.from_json(form)
            db.session.add(user)
            msg = "新增成功! "
    return render_template('admin/add_user.html', route=route, msg=msg)


@admin.route('/user-manage/list')
@admin_required
def user_list():
    route = [
        {
            'type': 'text',
            'text': '人员管理'
        },
        {
            'type': 'link',
            'text': '人员列表',
            'link': url_for('admin.user_list')
        }
    ]
    msg = request.args.get('msg', default='')
    page = request.args.get('page', default=1, type=int)
    name = request.args.get('name', default=None)
    phone = request.args.get('phone', default=None, type=int)
    role_name = request.args.get('role', default=None)
    role = Role.query.filter_by(name=role_name).first()
    admin = Role.query.filter_by(name='Administrator').first()

    query = User.query.filter(User.role != admin)

    if name:
        query = query.filter(User.name.like('%{}%'.format(name)))
    if phone:
        query = query.filter(User.phone == phone)
    if role:
        query = query.filter(User.role == role)
    pagination = query.order_by(User.id) \
        .paginate(page, per_page=8, error_out=False)
    next = pagination.next_num
    prev = pagination.prev_num
    total = pagination.pages
    users = [user.to_json() for user in pagination.items]

    return render_template('admin/user_list.html',
                           route=route,
                           users=users,
                           next=next,
                           prev=prev,
                           total=total,
                           page=page,
                           name=name,
                           phone=phone,
                           role_name=role_name)


@admin.route('/user/choice/course')
@admin_required
def user_c_course():
    route = [
        {
            'type': 'text',
            'text': '课程管理'
        },
        {
            'type': 'link',
            'text': '选课的人员',
            'link': url_for('admin.user_c_course')
        }
    ]
    msg = request.args.get('msg', default='')
    page = request.args.get('page', default=1, type=int)
    name = request.args.get('name', default=None)
    c_id = request.args.get('c_id', default=0, type=int)
    status = request.args.get('status', default=0, type=int)

    query = Choice.query

    if name:
        query = query.join(Course).filter(Course.name.like('%{}%'.format(name)))
    if status:
        if status == 1:
            query = query.filter(Choice.is_pass == "1")
        if status == 2:
            query = query.filter(Choice.is_pass == "0")
    if c_id:
        query = query.filter(Choice.course_id == c_id)

    pagination = query.order_by(Choice.course_id) \
        .paginate(page, per_page=8, error_out=False)
    next = pagination.next_num
    prev = pagination.prev_num
    total = pagination.pages
    choices = [choice.to_json() for choice in pagination.items]

    return render_template('admin/course_users.html',
                           route=route,
                           choices=choices,
                           next=next,
                           prev=prev,
                           total=total,
                           page=page,
                           name=name,
                           status=status)


@admin.route('/course/choice/user')
@admin_required
def user_courses():
    route = [
        {
            'type': 'text',
            'text': '人员管理'
        },
        {
            'type': 'link',
            'text': '人员的选课',
            'link': url_for('admin.user_courses')
        }
    ]
    msg = request.args.get('msg', default='')
    page = request.args.get('page', default=1, type=int)
    name = request.args.get('name', default=None)
    u_id = request.args.get('u_id', default=0, type=int)
    phone = request.args.get('phone', default=0)

    query = Choice.query.join(User)

    if name:
        query = query.filter(User.name.like('%{}%'.format(name)))
    if phone:
        query = query.filter(User.phone == phone)
    if u_id:
        query = query.filter(Choice.user_id == u_id)

    pagination = query.order_by(Choice.user_id) \
        .paginate(page, per_page=8, error_out=False)
    next = pagination.next_num
    prev = pagination.prev_num
    total = pagination.pages
    choices = [choice.to_json() for choice in pagination.items]

    return render_template('admin/user_courses.html',
                           route=route,
                           choices=choices,
                           next=next,
                           prev=prev,
                           total=total,
                           page=page,
                           name=name,
                           phone=phone)


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
    return render_template('admin/exam_edit.html', route=route, course=course)


@admin.route('/course/<int:c_id>/exam/judge')
@admin_required
def judge_list(c_id):
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
        {
            'type': 'link',
            'text': '判断题列表',
            'link': url_for('admin.judge_list', c_id=c_id)
        },
    ]
    course = Course.query.get_or_404(c_id)
    q = request.args.get('q')
    if q and q != '':
        judges = course.judges.filter(JudgeBank.question.like('%{}%'.format(q))).order_by(JudgeBank.id).all()
    else:
        judges = course.judges.order_by(JudgeBank.id).all()
    judges = [judge.to_json() for judge in judges]
    return render_template('admin/judge_list.html', route=route, course=course, judges=judges)


@admin.route('/course/<int:c_id>/exam/radio')
@admin_required
def radio_list(c_id):
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
        {
            'type': 'link',
            'text': '单选题列表',
            'link': url_for('admin.radio_list', c_id=c_id)
        },
    ]
    course = Course.query.get_or_404(c_id)
    q = request.args.get('q')
    if q and q != '':
        radios = course.radios.filter(RadioBank.question.like('%{}%'.format(q))).order_by(RadioBank.id).all()
    else:
        radios = course.radios.order_by(RadioBank.id).all()
    radios = [radio.to_json() for radio in radios]
    return render_template('admin/radio_list.html', route=route, course=course, radios=radios)


@admin.route('/course/<int:c_id>/exam/multiple')
@admin_required
def multiple_list(c_id):
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
        {
            'type': 'link',
            'text': '多选题列表',
            'link': url_for('admin.multiple_list', c_id=c_id)
        },
    ]
    course = Course.query.get_or_404(c_id)
    q = request.args.get('q')
    if q and q != '':
        multiples = course.multiples.filter(MultipleBank.question.like('%{}%'.format(q))).order_by(MultipleBank.id).all()
    else:
        multiples = course.multiples.order_by(MultipleBank.id).all()
    multiples = [multiple.to_json() for multiple in multiples]
    return render_template('admin/multiple_list.html', route=route, course=course, multiples=multiples)


