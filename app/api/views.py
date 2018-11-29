
from flask import jsonify, request, current_app, url_for
from flask_login import current_user

from . import api
from app.models import db, User, Course, Choice, Video, UserVideo
from app.decorators import admin_required, user_required
from app.tools import delete_file


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
            if uv.learn_status != status and ch.finish_nums != ch.video_nums:
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


@api.route('/get-learn-card')
@user_required
def get_learn_card():
    page = request.args.get('page', 1, type=int)
    _type = request.args.get('type', 'all')
    query = current_user.choices
    if _type == 'learning':
        query = query.filter(Choice.is_pass == 0)
    if _type == 'pass':
        query = query.filter(Choice.is_pass == 1)
    pagination = query.order_by(Choice.last_seen.desc()) \
        .paginate(page, per_page=6, error_out=False)
    choices = [course.to_json() for course in pagination.items]
    data = {
        'choices': choices,
        'total': pagination.total,
        'pages': pagination.pages,
        'next_num': pagination.next_num,
        'prev_num': pagination.prev_num
    }
    return jsonify({'resCode': 'ok', 'msg': '', 'data': data})


@api.route('/choice/<int:c_id>/<int:u_id>', methods=["DELETE"])
@user_required
def delete_choice(c_id, u_id):
    try:
        ch = Choice.query.filter_by(course_id=c_id, user_id=u_id).first()
        db.session.delete(ch)
        return jsonify({'resCode': 'ok', 'msg': '课程已移除！'})
    except Exception as e:
        return jsonify({'resCode': 'err', 'msg': '课程移除失败！'})


@api.route('/admin/password', methods=['UPDATE'])
@admin_required
def update_admin_pwd():
    data = request.get_json()
    pwd = None
    if data:
        pwd = data.get('password')
    else:
        return jsonify({
            'resCode': 'err',
            'msg': '数据传输错误！'
        })
    if pwd and pwd != '':
        current_user.password = pwd
        db.session.add(current_user)
    else:
        return jsonify({
            'resCode': 'err',
            'msg': '新密码不能为空！'
        })
    return jsonify({
        'resCode': 'ok',
        'msg': '密码更改成功！下次登录请使用新密码！'
    })


@api.route('/admin/course/<int:_id>', methods=['DELETE'])
@admin_required
def admin_course(_id):
    course = Course.query.get_or_404(_id)
    db.session.delete(course)
    return jsonify({
        'resCode': 'ok',
        'msg': '删除完毕！所有该课程相关资料将会一同删除！'
    })


@api.route('/upload/video', methods=["POST", "UPDATE"])
@admin_required
def upload_video():
    if request.method == "UPDATE":
        duration = request.values.get('duration')
        v_id = request.values.get('v_id')
        video = Video.query.get(v_id)
        if video:
            video.duration = duration
            db.session.add(video)
            db.session.commit()
            for uv in video.u_videos:
                uv.update_duration()
            return jsonify({
                'resCode': 'ok',
                'msg': '时长更新完毕！'
            })
    file = request.files.get('file')
    c_id = request.values.get('c_id')
    course = Course.query.get_or_404(c_id)
    filename = file.filename
    title = filename.split('.')[0] if isinstance(filename, str) else 'None'
    video = Video(title=title)
    video.course = course
    db.session.add(video)
    db.session.commit()
    v_id = video.id
    base_path = 'app/static/videos/'
    base_name = 'course{}-{}'.format(c_id, v_id)
    _filename = '{}.{}'.format(base_name, filename.split('.')[1])
    path = '/static/videos/' + _filename
    try:
        file.save(base_path + _filename)
        video.video_src = path
        db.session.add(video)

        choices = course.choices.all()
        users = [choice.user for choice in choices]
        for user in users:
            uv = UserVideo.create(user, video)

    except Exception as e:
        print(e)
        db.session.delete(video)

    return jsonify({
        'id': v_id,
        'duration': video.duration or '-',
        'order': video.order,
        'resCode': 'ok',
        'msg': 'ok',
        'filename': video.get_filename()
    })


@api.route('/video', methods=['UPDATE'])
@admin_required
def update_video():
    json = request.get_json()
    if json is None:
        return jsonify({
            'resCode': 'error',
            'msg': '出现错误! 数据为空！'
        })
    v_id = json.get('id')
    title = json.get('title')
    order = json.get('order')
    video = Video.query.get_or_404(v_id)
    try:
        order = int(order)
        video.order = order
    except:
        pass
    video.title = title
    db.session.add(video)
    return jsonify({
        'resCode': 'ok',
        'msg': '修改成功!'
    })


@api.route('/video', methods=['DELETE'])
@admin_required
def delete_video():
    v_id = request.args.get('v_id')
    video = Video.query.get_or_404(v_id)
    db.session.delete(video)
    delete_file(video.video_src)
    return jsonify({
        'resCode': 'ok',
        'msg': '视频已删除!'
    })