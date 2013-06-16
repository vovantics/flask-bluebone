# -*- coding: utf-8 -*-

# http://docs.fabfile.org/en/1.5/tutorial.html

import os
from fabric.api import *
from fabric import colors

"""
Base configuration
"""
env.database_password = '$(db_password)'
env.temp_path = 'tmp'
env.vendor_path = 'app/static/vendor'
env.src_img_path = 'app/static/img'
env.public_path = 'app/static/public'
env.project_root = os.path.abspath(os.path.dirname(__file__))

"""
Environments
"""


def production():
    """
    Work on production environment
    """
    env.settings = 'production'
    env.hosts = ['127.0.0.1']
    env.user = 'stevo'
    env.s3_bucket = 'flask-bluebone-assets-prod'


def staging():
    """
    Work on staging environment
    """
    env.settings = 'staging'
    env.hosts = ['127.0.0.1']
    env.user = 'stevo'
    env.s3_bucket = 'flask-bluebone-assets-stag'

"""
Branches
"""


def stable():
    """Work on stable branch."""
    env.branch = 'stable'


def master():
    """Work on development branch."""
    env.branch = 'master'


def branch(branch_name):
    """Work on any specified branch."""
    env.branch = branch_name

"""
Commands - setup
"""


def setup():
    install_requirements()
    initdb()
    #update_vendor_assets()
    lang('extract')
    lang('compile')


def install_requirements():
    local("python setup.py install")


def update_vendor_assets():
    '''Update vendor assets.'''

    # Clean
    local('rm -rf %s' % env.temp_path)
    local('rm -rf bootstrap')
    local('rm -rf app/static/.webassets-cache')

    local('mkdir %s' % env.temp_path)

    # Clone and build Bootstrap.
    print(colors.magenta('\nCloning Bootstrap\n'))
    local('git clone git://github.com/twitter/bootstrap.git')
    with lcd('bootstrap'):
        local('make bootstrap')

    # Copy Bootstrap files into env.temp_path.
    print(colors.magenta('\nCopying Bootstrap files to %s\n' % env.temp_path))
    local('cp -r bootstrap/bootstrap %s' % env.temp_path)

    # Move js/css/img files from env.temp_path into env.vendor_path.
    print(colors.magenta('\nMoving files to %s\n' % env.vendor_path))
    with lcd(env.vendor_path):
        local('rm -rf *')
    local('mv %s/* %s' % (env.temp_path, env.vendor_path))

    # Clean
    local('rm -rf %s' % env.temp_path)
    local('rm -rf bootstrap')
    local('rm -rf app/static/.webassets-cache')
    print(colors.green('\nUpdated! Boom!'))


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


def test():
    """Run test suite."""
    local('nosetests --with-coverage --cover-erase --cover-package=app')
    local('cloc app')


def run():
    local('python manage.py run')


def deploy():
    """
    Deploy the latest version of the site to the server and restart Apache2.
    Does not perform the functions of load_new_data().
    """
    require('settings', provided_by=[production, staging])
    require('branch', provided_by=[stable, master, branch])

    lang('compile')
    build_assets()
    sync_s3()
    _deploy_to_heroku()


def _deploy_to_heroku():
    """Deploy to heroku."""
    with lcd():
        local('git push heroku master')


def sync_s3():
    local('s3cmd -P --guess-mime-type --delete-removed sync %s/ s3://flask-bluebone-assets/' % PUBLIC_PATH)

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


def echo_host():
    """
    Echo the current host to the command line.
    """
    run('echo %(settings)s; echo %(hosts)s' % env)
