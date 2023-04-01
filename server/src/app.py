from flask import Flask, render_template, make_response
import os
import time
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

cred = credentials.Certificate("env/cypher-ampersand-firebase-adminsdk-2694w-0d791d1fab.json")
firebase_admin.initialize_app(cred)






def format_server_time():
	server_time = time.localtime()
	return time.strftime("%I:%M:%S %p", server_time)

@app.route('/index')
@app.route('/')
def index():

	server_time = format_server_time()


	db = firestore.client()  # this connects to our Firestore database
	collection = db.collection('terms')  # opens 'places' collection
	
	docs = collection.get()

	for doc_raw in docs:
		doc = doc_raw.to_dict()

		results = f'{doc["TERM_CODE"]} {doc["TERM_DESC"]} {doc["TERM_END_DATE"]}'


	creation_result = collection.document('TEST-TERM-2').set({
	    'TERM_CODE': '202410',
	    'TERM_DESC': 'Fall 2023',
	    'TERM_END_DATE': '2023-12-31T00:00:00'
	})

	context = { 
		'server_time': server_time,
		'results': results,
		'creation_result': creation_result
	}

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