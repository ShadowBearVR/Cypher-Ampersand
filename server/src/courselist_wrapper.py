import firebase_admin
from firebase_admin import credentials, firestore

import requests

from helper_functions import *

# Setup DB credentials.
cred = credentials.Certificate("env/cypher-ampersand-firebase-adminsdk-2694w-0d791d1fab.json")
firebase_admin.initialize_app(cred)

auth_headers = {}

def get_access_token():
    headers = {
        "accept": "application/json", 
        "Content-Type": "application/json"
    }

    data = {
        "client_id": f"{get_env_var('WM_CLIENT_ID')}",
        "secret_id": f"{get_env_var('WM_SECRET_ID')}"
    }

    response = requests.post("https://openapi.it.wm.edu/auth/v1/login", headers = headers, json = data)
    access_token = response.json()['access_token']
    print('Access token is', access_token)
    return access_token

def set_auth_headers(access_token):
    global auth_headers
    auth_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

def is_valid_auth(response):
    if response.status_code == 401:
        set_auth_headers(get_access_token)
        return False
    return True

def get_active_terms(second_attempt = False):
    response = requests.get("https://openapi.it.wm.edu/courses/development/v1/activeterms", headers = auth_headers)
    
    if not is_valid_auth(response) and not second_attempt:
       print('Attempting to get active terms again with updated token')
       response = get_active_terms(True)

    return response

def update_courselist_db():
    db = firestore.client()  # this connects to our Firestore database
    collection = db.collection('terms')  # opens 'terms' collection

    creation_result = collection.document('TEST-TERM-3').set({
        'TERM_CODE': '202410',
        'TERM_DESC': 'Fall 2023',
        'TERM_END_DATE': '2023-12-31T00:00:00'
    })

    # Clear Terms

    set_auth_headers(get_access_token())

    # Update Terms
    active_terms = get_active_terms().json()
    print(active_terms)
    for term in active_terms:
        print(term)
        doc_name = f'term-{term["TERM_CODE"]}'
        collection.document(doc_name).set({
            'TERM_CODE': f'{term["TERM_CODE"]}',
            'TERM_DESC': f'{term["TERM_DESC"]}',
            'TERM_END_DATE': f'{term["TERM_END_DATE"]}'
        })



    # Clear Subjects

    # Update Subjects

    

    # Clear Courses

    # Update Courses



def get_all_terms():
    db = firestore.client()
    collection = db.collection('terms')

    terms_docs = collection.get()

    terms_dicts = []

    for term_doc in terms_docs:
        term_dict = term_doc.to_dict()
        terms_dicts.append(term_dict)

    return terms_dicts

def get_all_subjects():

    db = firestore.client()
    collection = db.collection('subjects')

    subjects_docs = collection.get()

    subjects_dicts = []

    for subject_doc in subjects_docs:
        subject_dict = subject_doc.to_dict()
        subjects_dicts.append(subject_dict)

    return subjects_dicts

def get_all_courses():

    db = firestore.client()
    collection = db.collection('courses')

    courses_docs = collection.get()

    courses_dicts = []

    for course_doc in courses_docs:
        course_dict = course_doc.to_dict()
        courses_dicts.append(course_dict)

    return courses_dicts