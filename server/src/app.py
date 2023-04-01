from flask import Flask, render_template, make_response, request
import os
import time
from datetime import datetime

from courselist_wrapper import *
from helper_functions import *

# Initiate Flask app.
app = Flask(__name__)

# Get Courselist Secret.

set_env_vars()
update_courselist_secret = get_env_var('UPDATE_COURSELIST_SECRET')

# URL Routes

@app.route('/index')
@app.route('/')
def index():

    server_time = format_server_time()

    terms_list = get_all_terms()
    subjects_list = get_all_subjects()

    context = { 
        'server_time': server_time,
        'terms_list': terms_list,
        'subjects_list': subjects_list
    }

    return render_template('index.html', context=context)

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST' and len(dict(request.form)) > 0:
        form_data = dict(request.form)

        term_selection = form_data['term-selection']
        subject_selection = form_data['subject-selection']

        return f'Search for {subject_selection} subject during {term_selection} term.'
    else:
        return 'Sorry, there was an error.'

@app.route('/update-courselist', methods=['POST'])
def update_courselist():
    if request.method == 'POST':
        secret_input = request.get_data(as_text=True)

        if update_courselist_secret == secret_input:
            update_courselist_db()
            return 'Updated Database'
        else:
            return 'Did Not Update Database'
    else:
        return 'Invalid Request Method'

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors-pages/403.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error-pages/404.html')

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error-pages/500.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True,host='0.0.0.0',port=port)