#!/usr/bin/env python

import os
import datetime

from flaskext.script import Manager, Shell, Server, prompt_bool

from app.extensions import db
from app import create_app
from config import DevConfig, ProdConfig
from app.user import User, UserDetail, ADMIN, USER, ACTIVE


#env = os.environ.get('APP_ENV', 'prod')  # {dev, prod}
#app = create_app(eval('%sConfig' % env.capitalize()))
#manager = Manager(app)

app = create_app()
manager = Manager(app)

#manager = Manager(create_app())
#app = create_app()
manager.add_command("run", Server(host=app.config['HOST'], port=app.config['PORT']))
manager.add_command("shell", Shell())


@manager.command
def initdb():
    """Init/reset database."""

    if not prompt_bool("Are you sure? You will lose all your data!"):
        return

    db.drop_all()
    db.create_all()

    demo = User(
            username=u'demo',
            email='demo@example.com',
            password='default',
            role_id=USER,
            status_id=ACTIVE,
            user_detail=UserDetail(
                first_name=u'Demo',
                last_name=u'Dude',
                gender=u'female',
                dob=datetime.date(1985, 02, 17),
                phone=1234567890,
                bio=u'Demo dude is pretty sweet.',
                url=u'http://www.example.com/demo',
                ),
            )

    admin = User(
            username=u'admin',
            email='admin@example.com',
            password='default',
            role_id=ADMIN,
            status_id=ACTIVE,
            user_detail=UserDetail(
                first_name=u'Admin',
                last_name=u'Dude',
                gender=u'male',
                dob=datetime.date(1980, 02, 17),
                phone=1234567890,
                bio=u'Admin dude is the administrator.',
                url=u'http://www.example.com/admin',
                ),
            )
    db.session.add(demo)
    db.session.add(admin)
    db.session.commit()


manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()
