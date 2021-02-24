from flask import Blueprint

bp = Blueprint('errors', __name__)

from phileTag.errors import handlers