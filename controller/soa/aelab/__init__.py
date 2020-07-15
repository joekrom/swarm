from flask import Flask
from flask_restplus import Api
from flask import Blueprint



app = Flask(__name__)

app.config['SECRET_KEY'] = "rango"
from flask_mail import Mail ,Message

#app.config['APPLICATION_ROOT'] = '/abc/123'
"""configuration of the mail server"""
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'aelabuser1@gmail.com'
#app.config['MAIL_DEFAULT_SENDER']=""
app.config['MAIL_PASSWORD'] = 'aelab_test_V1'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


mail = Mail(app)

api = Api(app, version='1.0', title='@elab_servive  API',
    description='API Documentation',doc='/serverapi/v1/documentation')

#api.namespaces.clear()


from aelab import views
from aelab import models
from aelab import forms
from aelab import controller


#This sample of code is to change the toot url for all the views
# it is also used to create a way to change the route using the Blueprint object
# Register blueprint at URL
# (URL must match the one given to factory function above)
#app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
