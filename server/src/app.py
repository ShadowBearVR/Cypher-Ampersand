from flask import Flask, render_template, make_response
import os
import time
from datetime import datetime

app = Flask(__name__)

def format_server_time():
	server_time = time.localtime()
	return time.strftime("%I:%M:%S %p", server_time)

@app.route('/index')
@app.route('/')
def index():

	server_time = format_server_time()

	context = { 'server_time': server_time }
	return render_template('index.html', context=context)

@app.errorhandler(403)
def forbidden(e):
	return render_template("errors-pages/403.html")

@app.errorhandler(404)
def page_not_found(e):
	return render_template("error-pages/404.html")

@app.errorhandler(500)
def internal_server_error(e):
	return render_template("error-pages/500.html")

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 8080))
	app.run(debug=True,host='0.0.0.0',port=port)