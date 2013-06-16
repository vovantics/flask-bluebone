# -*- coding: utf-8 -*-

import json
import datetime

from flask import current_app
from flask.ext.testing import (TestCase as Base, Twill)

from app import create_app
from app.user import User, UserDetail, ADMIN, USER, ACTIVE
from config import TestConfig
from app.extensions import db, mail


class TestCase(Base):
    """Base TestClass for your application."""

    ENVIRON_BASE = {
        'HTTP_USER_AGENT': 'Chrome',
        'REMOTE_ADDR': '127.0.0.1',
        'HTTP_ORIGIN': 'http://localhost:9000'
    }

    def create_app(self):
        """Create and return a testing flask app."""

        app = create_app(TestConfig)
        self.twill = Twill(app, port=3000)
        return app

    def init_data(self):

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
                dob=datetime.date(1985, 01, 17),
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
                dob=datetime.date(1985, 01, 17),
                phone=1234567890,
                bio=u'Admin dude is the administrator.',
                url=u'http://www.example.com/admin',
                ),
            )

        db.session.add(demo)
        db.session.add(admin)
        db.session.commit()
        assert demo.id is not None
        assert admin.id is not None
        #self.user = user TODO

    def setUp(self):
        """Reset all tables before testing."""

        db.create_all()
        self.init_data()

    def tearDown(self):
        """Clean db session and drop all tables."""

        db.session.remove()
        db.drop_all()

    def login(self, email, password, remember=False):
        """Helper function to login"""
        rv = self.client.post('/session/',
                              data={
                                  'email': email,
                                  'password': password,
                                  'remember': remember
                              },
                              follow_redirects=True,
                              environ_base=self.ENVIRON_BASE
                              )
        self.assert_200(rv)
        assert 'success' in rv.data
        return rv

    def logout(self):
        """Helper function to logout"""
        rv = self.client.delete('/session/', follow_redirects=True,
                                environ_base=self.ENVIRON_BASE)
        self.assert_200(rv)
        assert 'success' in rv.data
        return rv

    def _test_get_request(self, endpoint, template=None):
        rv = self.client.get(endpoint)
        self.assert_200(rv)
        return rv


class TestUser(TestCase):

    def test_delete_activate(self):
        # User logs in and deactivates account
        self.login(email='demo@example.com', password='default')
        active_user = User.query.filter_by(email='demo@example.com').first()
        assert active_user.is_active() is True
        rv = self.client.delete('/users/%d/' % 1,
                                environ_base=self.ENVIRON_BASE)
        self.assert_200(rv)
        deactivated_user = User.query.filter_by(email='demo@example.com').first()
        assert deactivated_user.is_active() is False
        self.logout()

        # User logs in, initiating an activation
        self.login(email='demo@example.com', password='default')
        deactivated_user = User.query.filter_by(email='demo@example.com').first()

        # User enters new password
        data = {'status': 'active'}
        rv = self.client.put(
            '/users/activate/%s/%s/' % (deactivated_user.email, deactivated_user.activation_key),
            data=json.dumps(data), content_type='application/json',
            environ_base=self.ENVIRON_BASE)
        self.assert_200(rv)
        assert 'success' in rv.data
        active_user = User.query.filter_by(email='demo@example.com').first()
        assert active_user.is_active() is True
        #self.assert_405(rv)

    def test_get(self):
        self.login(email='demo@example.com', password='default')
        # Get a user.
        rv = self.client.get('/users/%d/' % 1, environ_base=self.ENVIRON_BASE)
        self.assert_200(rv)
        # Get list of users.
        rv = self.client.get('/users/', environ_base=self.ENVIRON_BASE)
        self.assert_200(rv)
        assert 'success' in rv.data
        self.logout()

    def test_register(self):
        data = {
            'username': 'member',
            'email': 'member@example.com',
            'password': 'default',
            'password_again': 'default'
        }
        rv = self.client.post('/users/', data=json.dumps(data),
                              content_type='application/json',
                              environ_base=self.ENVIRON_BASE)
        self.assert_200(rv)
        assert 'success' in rv.data
        new_user = User.query.filter_by(email=data['email']).first()
        assert new_user is not None

    def test_update_profile(self):
        self.login(email='demo@example.com', password='default')
        data = {
            'email': 'demo@example.com',
        }
        user = User.query.filter_by(email=data.get('email')).first()
        assert user is not None
        data = {
            'first_name': 'Bilbo',
            'last_name': 'Baggins',
            'username': user.username,
            'email': user.email,
            'gender': user.user_detail.gender,
            'dob': user.get_dob(),
            'phone': user.user_detail.phone,
            'bio': user.user_detail.bio,
            'url': user.user_detail.url
        }
        rv = self.client.put('/users/%d/' % user.id,
                             data=json.dumps(data),
                             content_type='application/json',
                             environ_base=self.ENVIRON_BASE)

        self.assert_200(rv)
        assert 'success' in rv.data
        user = User.query.filter_by(email=data.get('email')).first()
        assert user.user_detail.first_name == 'Bilbo'
        assert user.user_detail.last_name == 'Baggins'
        self.logout()

    def test_password_reset(self):
        # User enters email for account that DNE
        data = {'email': 'missing@example.com'}
        response = self.client.post('/users/password/reset/',
                                    data=json.dumps(data),
                                    content_type='application/json',
                                    environ_base=self.ENVIRON_BASE)
        assert 'Sorry, no user found for that email address.' in response.data
        self.assert_200(response)

        # User enters email and clicks 'Send instructions'
        data = {'email': 'demo@example.com'}
        user = User.query.filter_by(email=data.get('email')).first()
        assert user is not None
        assert user.activation_key is None
        with mail.record_messages() as outbox:
            # Application sends password reset email
            response = self.client.post('/users/password/reset/',
                                        data=json.dumps(data),
                                        content_type='application/json',
                                        environ_base=self.ENVIRON_BASE)
            assert len(outbox) == 1
            assert outbox[0].subject == "Recover your password"
        user = User.query.filter_by(email=data.get('email')).first()
        assert user.activation_key is not None

        # User enters new password
        data = {
            'password': 'new password',
            'password_again': 'new password',
        }
        user = User.query.filter_by(activation_key=user.activation_key) \
                         .filter_by(email=user.email).first()
        assert user is not None
        rv = self.client.put(
            '/users/password/%s/%s/' % (user.email, user.activation_key),
            data=json.dumps(data), content_type='application/json',
            environ_base=self.ENVIRON_BASE)
        self.assert_200(rv)
        assert 'success' in rv.data
        user = User.query.filter_by(email='demo@example.com').first()
        assert user is not None
        assert user.activation_key is None
        assert user.check_password(data.get('password')) is True

    def test_password_change(self):
        # User logs in
        self.login(email='demo@example.com', password='default')
        # User enters new password
        data = {
            'password': 'new password',
            'password_again': 'new password',
        }
        user = User.query.filter_by(email='demo@example.com').first()
        assert user is not None
        rv = self.client.put('/users/%d/' % user.id, data=json.dumps(data),
                             content_type='application/json',
                             environ_base=self.ENVIRON_BASE)
        self.assert_200(rv)
        assert 'success' in rv.data
        user = User.query.filter_by(email='demo@example.com').first()
        assert user is not None
        assert user.check_password(data.get('password')) is True


class TestMeta(TestCase):

    def test_contact(self):
        # User fills in form and clicks 'Send Message'
        data = {
            'full_name': 'Troubled User',
            'email': 'troubled.user@example.com',
            'subject': 'Help me!',
            'message': 'I have the blue screen of death! Call the doctor!',
        }
        with mail.record_messages() as outbox:
            # Application sends email to admin
            response = self.client.post('/mail/', data=json.dumps(data),
                                        content_type='application/json',
                                        environ_base=self.ENVIRON_BASE)
            assert len(outbox) == 1
            subject = '[%s] Message from %s: %s' % (current_app.config['APP_NAME'], data.get('full_name'), data.get('subject'))
            assert outbox[0].subject == subject
            self.assert_200(response)
            # TODO assert "Thanks for your message. We'll get back to you shortly." in response.data


class TestErrors(TestCase):

    def test_401(self):
        response = self.client.get('/users/1/',
                                   environ_base=self.ENVIRON_BASE)
        self.assert_401(response)

    def test_403(self):
        response = self.client.get('/session/',
                                   environ_base={
                                   'HTTP_ORIGIN': 'http://malicious.com'
                                   })
        self.assert_403(response)

    def test_404(self):
        response = self.client.get('/i-am-not-found/',
                                   environ_base=self.ENVIRON_BASE)
        self.assert_404(response)

    def test_405(self):
        response = self.client.post('/', data={},
                                    content_type='application/json',
                                    environ_base=self.ENVIRON_BASE)
        self.assert_405(response)

    def test_400(self):
        response = self.client.get('/session/',
                                   environ_base={
                                   'HTTP_ORIGINS': 'http://localhost:6666'
                                   })
        self.assert_400(response)

    def test_static_text_file_request(self):
        response = self.client.get('/robots.txt')
        self.assert_200(response)
