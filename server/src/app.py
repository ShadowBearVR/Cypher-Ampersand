from flask import Flask, render_template, make_response, request, redirect, url_for
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
    print('URL Reached - /index')

    server_time = format_server_time()

    terms_list = get_all_terms()
    subjects_list = get_all_subjects()
    attr_list = get_all_atrributes()
    levels_list = get_all_levels()
    part_of_term_codes_list = get_all_part_of_term_codes()

    instructors_list = get_all_instructors()
    credit_hours_list = get_all_credit_hours()

    context = { 
        'server_time': server_time,
        'terms_list': terms_list,
        'subjects_list': subjects_list,
        'attr_list': attr_list,
        'levels_list': levels_list,
        'part_of_term_codes_list': part_of_term_codes_list,
        'instructors_list': instructors_list,
        'credit_hours_list': credit_hours_list,
    }

    return render_template('index.html', context=context)

@app.route('/results', methods=['POST'])
def results():
    print('URL Reached - /results')

    if len(dict(request.form)) > 0:

        term_selection = request.form.get('term_selection')
        subject_selections = request.form.getlist('subject_selections')
        attr_selections = request.form.getlist('attr_selections')
        level_selections = request.form.getlist('level_selections')
        status_selections = request.form.getlist('status_selections')
        part_of_term_selections = request.form.getlist('part_of_term_selections')
        instructor_selections = request.form.getlist('instructor_selections')
        credit_hours_selections = request.form.getlist('credit_hours_selections')

        inputs = {
            'term_selection': term_selection,
            'subject_selections': subject_selections,
            'attr_selections': attr_selections,
            'level_selections': level_selections,
            'status_selections': status_selections,
            'part_of_term_selections': part_of_term_selections,
            'instructor_selections': instructor_selections,
            'credit_hours_selections': credit_hours_selections,
        }

        outputs = {
            'test': "Hello World!"
        }

        context = {
            'inputs': inputs,
            'outputs': outputs
        }

        ## DO COMPLICATED LOGIC HERE

        return render_template('results.html', context=context)
    
    else:
        context = {
            'error_title': 'Unknown Error',
            'error_message': 'Something went wrong submitting your request. Please try again later.'
        }
        return render_template('error.html', context=context)

@app.route('/course-details/<term>/<crn>')
def course_details(term, crn):
    print(f'URL Reached - /course-details/{term}/{crn}')

    course_details = get_course_details(term, crn)

    context = {
        'course_details': course_details
    }

    return render_template('course-details.html', context=context)



## ERROR HANDLING ##

@app.errorhandler(403)
def forbidden(e):
    context = {
        'error_title': '403',
        'error_message': 'Forbidden'
    }
    return render_template('error.html', context=context)

@app.errorhandler(404)
def page_not_found(e):
    context = {
        'error_title': '404',
        'error_message': 'Page Not Found'
    }
    return render_template('error.html', context=context)

@app.errorhandler(405)
def method_not_allowed(e):
    context = {
        'error_title': '405',
        'error_message': 'Method Not Allowed'
    }
    return render_template('error.html', context=context)

@app.errorhandler(500)
def internal_server_error(e):
    context = {
        'error_title': '500',
        'error_message': 'Internal Server Error'
    }
    return render_template('error.html', context=context)

## API METHODS ##

@app.route('/api/update-courselist', methods=['POST'])
def api_update_courselist():

    secret_input = request.get_data(as_text=True)

    if update_courselist_secret == secret_input:
        update_courselist_db(recreate_perm_tables=False)
        print('SECRET VALID - Updated Database')
        return 'Updated Database'
    else:
        print('SECRET INVALID - Did Not Update Database')
        return 'Did Not Update Database'

## START UP ##

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=True,host='0.0.0.0',port=port)