from flask import Flask, render_template, make_response, request
import os
import time
from datetime import datetime

import firebase_admin
from firebase_admin import credentials, firestore

# Initiate Flask app.
app = Flask(__name__)

# Setup DB credentials.
cred = credentials.Certificate("env/cypher-ampersand-firebase-adminsdk-2694w-0d791d1fab.json")
firebase_admin.initialize_app(cred)

# Get Courselist Secret.

update_courselist_secret = ''

with open('env/.env', 'r') as env_file:
    for line in env_file:
        update_courselist_secret = line.split('=')[1]

# Functions

def format_server_time():
    server_time = time.localtime()
    return time.strftime("%I:%M:%S %p", server_time)

def update_courselist_database():

    db = firestore.client()  # this connects to our Firestore database
    collection = db.collection('terms')  # opens 'places' collection

    creation_result = collection.document('TEST-TERM-3').set({
        'TERM_CODE': '202410',
        'TERM_DESC': 'Fall 2023',
        'TERM_END_DATE': '2023-12-31T00:00:00'
    })


# URL Routes

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

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST' and len(dict(request.form)) > 0:
        userdata = dict(request.form)
        name = userdata["name"][0]
        return f"Thank you! {name}"
    else:
        return "Sorry, there was an error."

@app.route('/update-courselist', methods=['POST'])
def update_courselist():
    if request.method == 'POST':
        secret_input = request.get_data(as_text=True)

        if update_courselist_secret == secret_input:
            update_courselist_database()
            return "Updated Database"
        else:
            return "Did Not Update Database"
    else:
        return "Invalid Request Method"

    

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