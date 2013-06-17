# -*- coding: utf-8 -*-

# http://flask.pocoo.org/docs/patterns/distribute/

from setuptools import setup

setup(
    name='flask-bluebone',
    version='0.1',
    author='Stevo',
    author_email='stephenvovan@gmail.com',
    packages=["app"],
    url='https://github.com/vovantics/flask-bluebone',
    license='LICENSE',
    description='Flask REST-ish API boilerplate.',
    zip_safe=False,
    install_requires=[
        'Flask==0.8',
        'Flask-SQLAlchemy==0.16',
        'Flask-WTF==0.8',
        'Flask-Script==0.3.3',
        'Flask-Babel==0.8',
        'Flask-Testing==0.4',
        'Flask-Mail',
        'Flask-Login==0.1.3',
        'nose',
        'coverage',
        'passlib',
        'cssmin==0.1.4',
        'fabric',
        'premailer',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries'
    ]
)
