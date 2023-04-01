import firebase_admin
from firebase_admin import credentials, firestore
import time
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
    return access_token

def set_auth_headers(access_token):
    global auth_headers
    auth_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

def is_valid_auth(response):
    if response.status_code == 401:
        set_auth_headers(get_access_token())
        return False
    return True

def get_active_terms(second_attempt = False):
    response = requests.get("https://openapi.it.wm.edu/courses/development/v1/activeterms", headers = auth_headers)
    
    if not is_valid_auth(response) and not second_attempt:
       print('Attempting to get active terms again with updated token')
       response = get_active_terms(True)

    return response

def get_subjects(second_attempt = False):
    response = requests.get("https://openapi.it.wm.edu/courses/development/v1/subjectlist", headers = auth_headers)

    if not is_valid_auth(response) and not second_attempt:
       print('Attempting to get subjects again with updated token')
       response = get_subjects(True)

    return response

def get_open_courses(subject, term, second_attempt = False):
    response = requests.get(f"https://openapi.it.wm.edu/courses/development/v1/opencourses/{subject}/{term}", headers = auth_headers)
    
    if not is_valid_auth(response) and not second_attempt:
        print('Attempting to get open courses again with updated token')
        response = get_open_courses(subject, term, True)

    return response

## UPDATE TABLE FUNCTIONS ##

def update_courselist_db(full_reset=False):
    db = firestore.client() 
    set_auth_headers(get_access_token())

    # FAST
    update_terms_table(db)
    update_subjects_table(db)

    # FAST (BUT CAN CAUSE DATA LOSS!)
    if full_reset:
        reset_attributes_table(db)
        reset_levels_table(db)
        reset_part_of_term_codes_table(db)

    # VERY SLOW

    # term_dicts = get_all_terms()

    # for term_dict in term_dicts:

    #     term = term_dict['TERM_CODE']

    #     print("STARTED UPDATE OF", term)
        
    #     update_courses_table(db, term)
    #     print("ENDED UPDATE OF", term)

    #     print("STARTED SLEEP OF", term)
    #     time.sleep(60)
    #     print("ENDED SLEEP OF", term)

def update_terms_table(db):
    # Clear Terms
    terms_collection = db.collection('terms')
    delete_collection(terms_collection)

    # Repopulate Terms
    active_terms = get_active_terms().json()
    for term in active_terms:
        term_code = term['TERM_CODE']
        term_desc = term['TERM_DESC']
        term_end_date = term['TERM_END_DATE']
        doc_name = f'term-{term_code}'

        terms_collection.document(doc_name).set({
            'TERM_CODE': f'{term_code}',
            'TERM_DESC': f'{term_desc}',
            'TERM_END_DATE': f'{term_end_date}'
        })

def update_subjects_table(db):
    # Clear Subjects
    subjects_collection = db.collection('subjects')
    delete_collection(subjects_collection)

    # Repopulate Subjects
    subjects = get_subjects().json()
    for subject in subjects:
        subj_code = subject['STVSUBJ_CODE']
        subj_desc = subject['STVSUBJ_DESC']
        doc_name = f'subject-{subj_code}'

        subjects_collection.document(doc_name).set({
            'SUBJ_CODE': f'{subj_code}',
            'SUBJ_DESC': f'{subj_desc}'
        })

def update_courses_table(db, term):

    courses_table_name = f'courses-{term}'

    # Clear Courses
    courses_collection = db.collection(courses_table_name)
    delete_collection(courses_collection)

    # Repopulate Courses
    for subject in get_all_subjects():
        courses = get_open_courses(subject['SUBJ_CODE'], term).json()
        for course in courses:

            if (course['COURSE_ATTR'] == 'Not Available'):
                course_attr = []
            else:
                course_attr = course['COURSE_ATTR'].replace('/','').split(', ')

            course_id = course['COURSE_ID']
            part_of_term = course['COURSE_PTRM']
            credit_hrs = course['CREDIT_HRS']
            crn_id = course['CRN_ID']

            if (course['CRS_DAYTIME'] == 'Not Available'):
                course_days = ''
                course_time = ''
            else:
                course_days = course['CRS_DAYTIME'].split(':')[0]
                course_time = course['CRS_DAYTIME'].split(':')[1]

            if (course['CRS_LEVL'] is None):
                course_level = []
            else:
                course_level = course['CRS_LEVL'].split(',')

            current_enr = course['CURRENT_ENR']
            instructor = course['INSTRUCTOR']

            if (course['OPEN_CLOSED'] == 'OPEN'):
                is_open = True
            else:
                is_open = False

            proj_enr = course['PROJ_ENR']

            seats_avail = course['SEATS_AVAIL']
            is_crosslisted = '*' in seats_avail

            subject_code = course['SUBJECT_CODE']
            term_code = course['TERM_CODE']
            term_desc = course ['TERM_DESC']
            title = course['TITLE']

            doc_name = f'course-{crn_id}'

            courses_collection.document(doc_name).set({
                'COURSE_ATTR': course_attr,
                'COURSE_ID': f'{course_id}',
                'PART_OF_TERM': f'{part_of_term}',
                'CREDIT_HRS': f'{credit_hrs}',
                'CRN_ID': f'{crn_id}',
                'COURSE_DAYS': f'{course_days}',
                'COURSE_TIME': f'{course_time}',
                'COURSE_LEVEL': course_level,
                'CURRENT_ENR': f'{current_enr}',
                'INSTRUCTOR': f'{instructor}',
                'IS_OPEN': is_open,
                'PROJ_ENR': f'{proj_enr}',
                'SEATS_AVAIL': f'{seats_avail}',
                'IS_CROSSLISTED': is_crosslisted,
                'SUBJECT_CODE': f'{subject_code}',
                'TERM_CODE': f'{term_code}',
                'TERM_DESC': f'{term_desc}',
                'TITLE': f'{title}'
            })

## RESET TABLE FUNCTIONS ##

def reset_attributes_table(db):

    # Clear Attributes
    attr_collection = db.collection('attributes')
    delete_collection(attr_collection)

    # Repopulate Attributes
    attr_list = get_all_atrributes_from_courses()
    for attr in attr_list:
        attr_code = attr
        attr_desc = ''
        doc_name = f'attr-{attr_code}'

        attr_collection.document(doc_name).set({
            'ATTR_CODE': f'{attr_code}',
            'ATTR_DESC': f'{attr_desc}'
        })

def reset_levels_table(db):

    # Clear Levels
    level_collection = db.collection('levels')
    delete_collection(level_collection)

    # Repopulate Levels
    level_list = get_all_levels_from_courses()
    for level in level_list:
        level_code = level
        level_desc = ''
        doc_name = f'level-{level_code}'

        level_collection.document(doc_name).set({
            'LEVEL_CODE': f'{level_code}',
            'LEVEL_DESC': f'{level_desc}'
        })

def reset_part_of_term_codes_table(db):

    # Clear Part of Term Codes
    part_of_term_codes_collection = db.collection('part-of-term-codes')
    delete_collection(part_of_term_codes_collection)

    # Repopulate Part of Term Codes
    part_of_term_codes_list = get_all_part_of_term_codes_from_courses()
    for part_of_term_code in part_of_term_codes_list:
        part_term_code = part_of_term_code
        part_term_desc = ''
        doc_name = f'part-of-term-code-{part_term_code}'

        part_of_term_codes_collection.document(doc_name).set({
            'PART_TERM_CODE': f'{part_term_code}',
            'PART_TERM_DESC': f'{part_term_desc}'
        })

def delete_collection(coll_ref, batch_size=500):
    docs = coll_ref.list_documents(page_size=batch_size)
    deleted = 0

    for doc in docs:
        #print(f'Deleting doc {doc.id} => {doc.get().to_dict()}')
        doc.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)

## INTERNAL FUNCTIONS ##

def get_all_atrributes_from_courses():

    db = firestore.client()
    collection = db.collection('courses')

    courses_docs = collection.get()

    attr_list = []

    for course_doc in courses_docs:
        course_attrs = course_doc.to_dict()["COURSE_ATTR"]
        attr_list.extend(course_attrs)

    attr_set = set(attr_list)
    attr_list = list(attr_set)

    attr_list.sort()

    return attr_list

def get_all_levels_from_courses():

    db = firestore.client()
    collection = db.collection('courses')

    courses_docs = collection.get()

    levels_list = []

    for course_doc in courses_docs:
        course_levels = course_doc.to_dict()["COURSE_LEVEL"]
        levels_list.extend(course_levels)

    levels_set = set(levels_list)
    levels_list = list(levels_set)

    levels_list.sort()

    return levels_list

def get_all_part_of_term_codes_from_courses():

    db = firestore.client()
    collection = db.collection('courses')

    courses_docs = collection.get()

    part_of_term_codes_list = []

    for course_doc in courses_docs:
        course_part_of_term_code = course_doc.to_dict()["PART_OF_TERM"]
        part_of_term_codes_list.extend(course_part_of_term_code)

    part_of_term_codes_set = set(part_of_term_codes_list)
    part_of_term_codes_list = list(part_of_term_codes_set)

    part_of_term_codes_list.sort()

    return part_of_term_codes_list

## EXTERNAL FUNCTIONS ##

def get_all_terms():
    db = firestore.client()
    collection = db.collection('terms')

    terms_docs = collection.get()

    term_dicts = []

    for term_doc in terms_docs:
        term_dict = term_doc.to_dict()
        term_dicts.append(term_dict)

    return term_dicts

def get_all_subjects():

    db = firestore.client()
    collection = db.collection('subjects')

    subjects_docs = collection.get()

    subjects_dicts = []

    for subject_doc in subjects_docs:
        subject_dict = subject_doc.to_dict()
        subjects_dicts.append(subject_dict)

    return subjects_dicts

def get_all_courses(term):

    courses_table_name = f'courses-{term}'

    db = firestore.client()
    collection = db.collection(courses_table_name)

    courses_docs = collection.get()

    courses_dicts = []

    for course_doc in courses_docs:
        course_dict = course_doc.to_dict()
        courses_dicts.append(course_dict)

    return courses_dicts

def get_all_atrributes():

    db = firestore.client()
    collection = db.collection('attributes')

    attr_docs = collection.get()

    attr_dicts = []

    for attr_doc in attr_docs:
        attr_dict = attr_doc.to_dict()
        attr_dicts.append(attr_dict)

    return attr_dicts

def get_all_levels():

    db = firestore.client()
    collection = db.collection('levels')

    levels_docs = collection.get()

    levels_dict = []

    for level_doc in levels_docs:
        level_dict = level_doc.to_dict()
        levels_dict.append(level_dict)

    return levels_dict

def get_all_part_of_term_codes():

    db = firestore.client()
    collection = db.collection('part-of-term-codes')

    part_of_term_codes_docs = collection.get()

    part_of_term_codes_dicts = []

    for part_of_term_codes_doc in part_of_term_codes_docs:
        part_of_term_codes_dict = part_of_term_codes_doc.to_dict()
        part_of_term_codes_dicts.append(part_of_term_codes_dict)

    return part_of_term_codes_dicts