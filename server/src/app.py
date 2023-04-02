from flask import Flask, render_template, make_response, request, redirect, url_for
import os
import time
from datetime import datetime
import json

from courselist_wrapper import *
from helper_functions import *
from map_functions import *



# Initiate Flask app.
app = Flask(__name__)

# Get Courselist Secret.

set_env_vars()
update_courselist_secret = get_env_var('UPDATE_COURSELIST_SECRET')

academic_buildings_list = []

with open('data/academic_buildings.json', 'r') as academics_buildings_file:
    academic_buildings_list = json.load(academics_buildings_file)

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

@app.route('/results', methods=['GET', 'POST'])
def results():
    print('URL Reached - /results')

    if (request.method == 'GET'):
        return redirect(url_for('index'))
    else:

        if len(dict(request.form)) > 0:

            print(request.form)

            term_selection = request.form.get('term_selection')

            subject_selections = request.form.getlist('subject_selections')
            attr_selections = request.form.getlist('attr_selections')
            level_selections = request.form.getlist('level_selections')
            status_selections = request.form.getlist('status_selections')
            part_of_term_selections = request.form.getlist('part_of_term_selections')
            instructor_selections = request.form.getlist('instructor_selections')
            credit_hours_selections = request.form.getlist('credit_hours_selections')

            print('attr_selections', attr_selections)
            print('level_selections', level_selections)

            if (not attr_selections):
                attr_selections = ['ALL']

            if (not level_selections):
                level_selections = ['ALL']

            # If 'ALL' is included in a multi select dropdown,
            # the multi select is ignored as a potential filter.

            if ('ALL' not in attr_selections and 'ALL' not in level_selections):
                context = {
                    'error_title': 'Incompatible Selection',
                    'error_message': 'Either Attribute or Course Level must be ALL'
                }
                return render_template('error.html', context=context)

            if (not subject_selections or 'ALL' in subject_selections):
                subject_selections = []

            if (not attr_selections or 'ALL' in attr_selections):
                attr_selections = []

            if (not level_selections or 'ALL' in level_selections):
                level_selections = []

            if (not status_selections or 'ALL' in status_selections):
                status_selections = []

            if (not part_of_term_selections or 'ALL' in part_of_term_selections):
                part_of_term_selections = []

            if (not instructor_selections or 'ALL' in instructor_selections):
                instructor_selections = []

            if (not credit_hours_selections or 'ALL' in credit_hours_selections):
                credit_hours_selections = []

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

            print('inputs', inputs)

            results = get_results_for_query(inputs)

            output = {
                'results': results
            }

            context = {
                'inputs': inputs,
                'output': output
            }

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
    course = get_course(term, crn)

    if course_details.get('START_DATE') is not None:
        date_str = course_details['START_DATE']
        # Convert date string to datetime object
        datetime_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        # Convert datetime object to formatted string
        formatted_date_str = datetime_obj.strftime("%A, %B %d, %Y")
        course_details['START_DATE'] = formatted_date_str

    if course_details.get('END_DATE') is not None:
        date_str = course_details['END_DATE']
        # Convert date string to datetime object
        datetime_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
        # Convert datetime object to formatted string
        formatted_date_str = datetime_obj.strftime("%A, %B %d, %Y")
        course_details['END_DATE'] = formatted_date_str

    if course.get('COURSE_DAYS') is not None:
        day_dict = {
            "M": "Monday",
            "T": "Tuesday",
            "W": "Wednesday",
            "R": "Thursday",
            "F": "Friday"
        }
        input_str = course['COURSE_DAYS']
        output_str = ", ".join([day_dict[day] for day in input_str])
        course['COURSE_DAYS'] = output_str

    if course.get('COURSE_TIME') is not None:
        input_str = course['COURSE_TIME']
        start_time_str, end_time_str = input_str.split("-")

        start_time = datetime.strptime(start_time_str, "%H%M").strftime("%-I:%M%P").lower()
        end_time = datetime.strptime(end_time_str, "%H%M").strftime("%-I:%M%P").lower()

        output_str = f"{start_time} - {end_time}"
        course['COURSE_TIME'] = output_str



    context = {
        'course_details': course_details,
        'course': course
    }

    return render_template('course-details.html', context=context)

@app.route('/campus-routing', methods=['GET', 'POST'])
def campus_routing():
    print('URL Reached - /campus_routing')

    if (request.method == 'GET'):

        context = {
            'academic_buildings_list': academic_buildings_list
        }

        return render_template('campus-routing.html', context=context)

    else:
        if (len(dict(request.form)) > 0):

            building_1_selection = request.form.get('building_1_selection')
            building_2_selection = request.form.get('building_2_selection')
            
            inputs = {
                'building_1_selection': building_1_selection,
                'building_2_selection': building_2_selection,
            }

            results = get_travel_estimates('walking', building_1_selection, building_2_selection)

            output = {
                'results': results
            }

            context = {
                'inputs': inputs,
                'output': output
            }

            return render_template('campus-routing-results.html', context=context)
        
        else:
            context = {
                'error_title': 'Unknown Error',
                'error_message': 'Something went wrong submitting your request. Please try again later.'
            }
            return render_template('error.html', context=context)

@app.route('/fun-stats')
def fun_stats():
    print(f'URL Reached - /fun-stats')

    results = get_fun_stats_data()

    context = {
        'results': results
    }

    return render_template('fun-stats.html', context=context)

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