from flask import Flask
#from flask_restful import Api
from flask_restplus import Api
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask import Blueprint
# for authentification
from flask_jwt import JWT
#from security import authenticate, identity
# for api documentation

app = Flask(__name__)
#blueprint = Blueprint('api', __name__,url_prefix='/webapi/v1')


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
from aelab import controller


# This sample of code is to change the toot url for all the views
# it is also used to create a way to change the route using the Blueprint object
from aelab.views  import bp
#app.register_blueprint(bp, url_prefix="/webapp/v1")
