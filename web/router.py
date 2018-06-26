from flask import Flask, request, send_from_directory, render_template, jsonify, request, Blueprint
import json

query_js = Blueprint('query_js', __name__, template_folder='templates')
query_styles = Blueprint('query_styles', __name__, template_folder='templates')
view_index = Blueprint('view_index', __name__, template_folder='templates')
edp_is_alive = Blueprint('edp_is_alive', __name__, template_folder='templates')
edp_confirm_adopt = Blueprint('edp_confirm_adopt', __name__, template_folder='templates')
view_access_management = Blueprint('view_access_management', __name__, template_folder='templates')

""" Ressources """
#Javascript directory
@query_js.route('/js/<path:path>')
def send_js(path):
	return send_from_directory('./templates/static/js', path)

#CSS directory
@query_styles.route('/styles/<path:path>')
def send_css(path):
	return send_from_directory('./templates/static/styles', path)

""" Views """
#View index
@view_index.route("/")
def index():
	return render_template('./server/index.html')

#View index
@view_access_management.route("/accessManagementView")
def index():
	return render_template('./server/accessManagement/accessManagementView.html')

""" Communication endpoints """
@edp_is_alive.route("/isAlive")
def is_alive():
	return json.dumps({'success':True}), 200, {'ContentType':'application/json'}

@edp_confirm_adopt.route("/confirmAdopt/<clientId>")
def confirm_adopt(clientId):
	return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
