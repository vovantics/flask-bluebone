# -*- coding: utf-8 -*-

# http://docs.fabfile.org/en/1.5/tutorial.html

import os
from fabric.api import env, local, require, lcd

env.project_root = os.path.abspath(os.path.dirname(__file__))
env.project_name = 'flask-bluebone'

""" Environments """


def production():
    """ Work on production environment. """
    env.settings = 'production'
    env.hosts = ['0.0.0.0']
    with lcd(env.project_root):
        local("heroku git:remote -a powerful-lowlands-4262")


def staging():
    """
    Work on staging environment
    """
    env.settings = 'staging'
    env.hosts = ['127.0.0.1']


"""
Commands - setup
"""


def setup():
    _install_requirements()
    initdb()
    lang('extract')
    lang('compile')


def _install_requirements():
    with lcd(env.project_root):
        local("git remote add heroku git@heroku.com:%s.git" % env.project_name)
        local("python setup.py install")


def lang(mode='extract', lang_code=None):
    if mode == 'compile':
        # Compile catalog
        local('pybabel compile -d app/translations')
    elif mode == 'add':
        # Init catalog
        local('pybabel init -i app/translations/messages.pot -d app/translations -l %s' % lang_code)
    else:
        # Extract messages and update catalog(s)
        local('pybabel extract -F app/babel.cfg -o app/translations/messages.pot app')
        local('pybabel update -i app/translations/messages.pot -d app/translations')

"""
Commands - deployment
"""


def run():
    """ Start with the default server. """
    local('python manage.py run')


def grun():
    """ Start with gunicorn server. """
    local('gunicorn -c gunicorn.conf runserver:app')


def test():
    """ Run test suite. """
    local('nosetests --with-coverage --cover-erase --cover-package=app')
    local('cloc app')


def deploy():
    """
    Deploy the latest version of the site to the server and restart Apache2.
    Does not perform the functions of load_new_data().
    """
    require('settings', provided_by=[production, staging])

    lang('compile')
    _deploy_to_heroku()


def _deploy_to_heroku():
    """ Deploy to heroku. """
    with lcd(env.project_root):
        local('git push heroku master')

"""
Commands - data
"""


def initdb():
    local('python manage.py initdb')

"""
Commands - miscellaneous
"""


def clear_pyc():
    '''Remove compiled .pyc files.'''
    local("find . -iname '*.pyc' -exec rm -v {} \;", capture=False)
