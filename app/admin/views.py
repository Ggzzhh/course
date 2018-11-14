#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# 作者: Ggzzhh
# 创建时间: 2018/11/14

from flask import url_for, render_template
from flask_login import login_manager

from . import admin
from app.decorators import admin_required

login_manager.login_view = 'admin.login'


@admin.route('/')
# @admin_required
def index():
    return render_template('admin/index.html')


@admin.route('/login')
def login():
    return 'LOGIN'
