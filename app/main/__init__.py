#!/usr/bin/env python
# -*- coding:utf-8 -*-
# 作者: Ggzzhh
# 创建时间: 2018/10/22

from flask import Blueprint

main = Blueprint('main', __name__)

from . import views