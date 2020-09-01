from flask import Flask
#from flask_restful import Api
from flask_restplus import Api
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask import Blueprint
# for authentification
#from security import authenticate, identity
# for api documentation

app = Flask(__name__)


app.config['SECRET_KEY'] = "rango"

login = LoginManager()
login.init_app(app)
Bootstrap(app)

api = Api(app, version='1.0', title='@elab_servive  API',
    description='API Documentation',doc='/webapi/v1/documentation')
api.namespaces.clear()
#app.register_blueprint(blueprint)



from aelab import views
from aelab import models
from aelab import forms
