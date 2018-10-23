
from flask import jsonify, request
from flask_login import logout_user

from . import api


@api.route('/')
def main():
    return jsonify({'resCode': '200', 'msg': 'ok'})






