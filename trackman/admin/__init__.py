from flask import Blueprint

bp = Blueprint('admin', __name__)

from trackman.admin import views
