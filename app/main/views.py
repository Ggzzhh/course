#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# 作者: Ggzzhh
# 创建时间: 2018/10/22

from flask import jsonify, redirect, render_template, url_for, current_app
from flask_login import login_user, logout_user, login_required

from . import main


@main.route('/')
def index():
    return redirect(url_for('main.login'))


@main.route('/login', methods=['POST', 'GET'])
def login():
    return render_template('main/login.html', page_title=current_app.config['SYSTEMNAME'])