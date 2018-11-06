#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from app import create_app, db
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand

from app.models import Role, User, Choice, Course, Video, Classify


app = create_app('development')
manager = Manager(app)
migrate = Migrate(app, db)


@manager.shell
def make_shell_context():
    return dict(app=app, db=db, role=Role, user=User, choice=Choice,
                course=Course, video=Video, cls=Classify)


@manager.command
def c_test_data():
    from app.test import CreateCourse, CreateVideo
    cc = CreateCourse()
    cv = CreateVideo()
    # for i in range(20):
    #     cc.create_course()
    cv.run(20)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


if __name__ == "__main__":
    manager.run()
