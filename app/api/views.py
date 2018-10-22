
from flask import jsonify

from . import api


@api.route('/')
def main():
    return jsonify({'test': '测试成功'})



