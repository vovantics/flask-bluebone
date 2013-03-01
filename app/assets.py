from flask.ext.assets import Bundle

# ================================================================
# Email

email_css = Bundle(
    Bundle(
        'css/email/style.less',
        filters='less'
    ),
    filters='cssmin', output='public/css/email.css')

# ================================================================
# Error

error_css = Bundle(
    Bundle(
        'css/error/style.less',
        filters='less'
    ),
    filters='cssmin', output='public/css/error.css')
