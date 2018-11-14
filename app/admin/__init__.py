#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# 作者: Ggzzhh
# 创建时间: 2018/11/14

from flask import Blueprint

admin = Blueprint('admin', __name__)

from . import views