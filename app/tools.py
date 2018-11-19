#!/usr/bin/env python
# -*- coding:utf-8 -*- 
# 作者: Ggzzhh
# 创建时间: 2018/11/19

import os
from werkzeug.datastructures import FileStorage


def save_to_static(file, filename):
    if isinstance(file, FileStorage):
        upload_path = os.path.join(os.getcwd(), "app", "static", "images")
        if not os.path.exists(upload_path):
            os.mkdir(upload_path)
        try:
            path = os.path.join(upload_path, filename)
            file.save(path)
            return "/static/images/" + filename
        except Exception as e:
            print(e)
    return

