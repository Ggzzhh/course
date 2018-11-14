#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# 作者: Ggzzhh
# 创建时间: 2018/11/5
# 用于存放各种装饰器

from functools import wraps

from flask import abort, redirect, url_for
from flask_login import current_user, login_required, login_manager

from app.models import Permission


def permission_required(permission):
    def decorator(fun):
        @wraps(fun)
        @login_required
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return fun(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(fun):
    @wraps(fun)
    def decorator_function(*args, **kwargs):
        if not current_user.can(Permission.ADMINISTRATOR):
            return redirect(url_for('admin.login'))
        return fun(*args, **kwargs)
    return decorator_function


def user_required(fun):
    return permission_required(Permission.LEARN)(fun)