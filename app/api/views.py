
from flask import jsonify, request

from . import api
from app.models import db, User, Course, Choice, Video, UserVideo
from app.decorators import admin_required, user_required


@api.route('/')
def main():
    return jsonify({'resCode': '200', 'msg': 'ok'})


@api.route('/auth_pwd', methods=['POST'])
@user_required
def auth_pwd():
    if request.method == 'POST':
        data = request.get_json()
        if data is None:
            return jsonify({'resCode': 'ok', 'msg':'无内容'})
        _id = data.get('u_id')
        pwd = data.get('pwd')
        user = User.query.get(_id)
        if user and user.password == pwd:
            return jsonify({'resCode': 'ok', 'msg': '密码正确'})
        return jsonify({'resCode': 'err', 'msg': '密码错误'})
    return jsonify({'resCode': 'err', 'msg': 'em.........'})


@api.route('/update_pwd', methods=['POST'])
@user_required
def update_pwd():
    if request.method == 'POST':
        data = request.get_json()
        if data is None:
            return jsonify({'resCode': 'ok', 'msg':'无内容'})
        _id = data.get('u_id')
        pwd = data.get('pwd')
        user = User.query.get(_id)
        if user:
            user.password = pwd
            db.session.add(user)
            return jsonify({'resCode': 'ok', 'msg': '密码更改成功'})
        return jsonify({'resCode': 'err', 'msg': '发生错误!密码更改失败！'})
    return jsonify({'resCode': 'err', 'msg': 'em.........'})


@api.route('/choice-course', methods=["PUT"])
@user_required
def choice_course():
    data = request.get_json()
    if data:
        u_id = data.get('u_id')
        c_id = data.get('c_id')
        if u_id and c_id:
            user = User.query.get_or_404(u_id)
            course = Course.query.get_or_404(c_id)
            ch = Choice(user=user, course=course)
            for video in course.videos:
                uv = UserVideo.create(user, video)
                db.session.add(uv)
            ch.update_nums()
            return jsonify({'resCode': 'ok', 'msg': '选课成功！'})
    return jsonify({'resCode': 'err', 'msg': '选课失败！无数据或数据错误！'})


@api.route('/update-last-choice', methods=['PUT'])
@user_required
def update_last_choice():
    data = request.get_json()
    if data:
        u_id = data.get('u_id')
        c_id = data.get('c_id')
        if u_id and c_id:
            ch = Choice.query.filter(
                Choice.user_id == u_id, Choice.course_id == c_id).first()
            ch.update_seen()
            return jsonify({'resCode': 'ok', 'msg': '更新完毕！'})
    return jsonify({'resCode': 'err', 'msg': '更新失败！无数据或数据错误！'})


@api.route('/can-exam')
@user_required
def can_exam():
    u_id = request.args.get('u_id')
    c_id = request.args.get('c_id')
    if u_id and c_id:
        ch = Choice.query.filter(
            Choice.user_id == u_id, Choice.course_id == c_id).first()
        if ch.can_exam():
            return jsonify({'resCode': 'ok', 'msg': 'pass'})
        else:
            return jsonify({'resCode': 'err', 'msg': '请先学习完毕后再进行考试！'})
    return jsonify({'resCode': 'err', 'msg': '出现错误！无数据或数据错误！'})


@api.route('/update-learn-time', methods=['PUT'])
@user_required
def update_learn_time():
    data = request.get_json()
    if data:
        u_id = data.get('u_id')
        c_id = data.get('c_id')
        v_id = data.get('v_id')
        ch = Choice.query.filter(
            Choice.user_id == u_id, Choice.course_id == c_id).first()
        uv = UserVideo.query.filter(
            UserVideo.user_id == u_id, UserVideo.video_id == v_id).first()
        video_rate = 0
        learn_rate = 0
        if uv and ch:
            status = uv.learn_status
            if status:
                return jsonify({
                    'resCode': 'ok',
                    'msg': '该视频已经学习完毕！'
                })
            uv.update_learn_time()
            if uv.learn_status != status:
                ch.finish_nums += 1
            video_rate = uv.get_percent()
            learn_rate = ch.learn_rate()
        return jsonify({
            'resCode': 'ok',
            'msg': '更新完毕！',
            'rate': {
                'video_rate': video_rate,
                'learn_rate': learn_rate
            }
        })
    return jsonify({'resCode': 'err', 'msg': '出现错误！无数据或数据错误！'})




