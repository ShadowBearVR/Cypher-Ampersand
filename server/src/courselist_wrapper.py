import firebase_admin
from firebase_admin import credentials, firestore
import time
import requests

from helper_functions import *

# Setup DB credentials.
cred = credentials.Certificate("env/cypher-ampersand-firebase-adminsdk-2694w-0d791d1fab.json")
firebase_admin.initialize_app(cred)

auth_headers = {}

def open_api_get_access_token():
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
        set_auth_headers(open_api_get_access_token())
        return False
    return True

def open_api_get_active_terms(second_attempt = False):
    response = requests.get("https://openapi.it.wm.edu/courses/development/v1/activeterms", headers = auth_headers)
    
    if not is_valid_auth(response) and not second_attempt:
       print('Attempting to get active terms again with updated token')
       response = open_api_get_active_terms(True)

    return response

def open_api_get_subjects(second_attempt = False):
    response = requests.get("https://openapi.it.wm.edu/courses/development/v1/subjectlist", headers = auth_headers)

    if not is_valid_auth(response) and not second_attempt:
       print('Attempting to get subjects again with updated token')
       response = open_api_get_subjects(True)

    return response

def open_api_get_open_courses(subject, term, second_attempt = False):
    response = requests.get(f"https://openapi.it.wm.edu/courses/development/v1/opencourses/{subject}/{term}", headers = auth_headers)
    
    if not is_valid_auth(response) and not second_attempt:
        print('Attempting to get open courses again with updated token')
        response = open_api_get_open_courses(subject, term, True)

    return response

def open_api_get_course_details(term, crn, second_attempt = False):
    response = requests.get(f"https://openapi.it.wm.edu/courses/development/v2/coursesections/{term}/{crn}", headers = auth_headers)
    
    if not is_valid_auth(response) and not second_attempt:
        print('Attempting to get open course details again with updated token')
        response = open_api_get_course_details(term, crn, True)

    return response

## UPDATE TABLE FUNCTIONS ##

def update_courselist_db(recreate_perm_tables=True):
    db = firestore.client() 
    set_auth_headers(open_api_get_access_token())

    # HARD CODED

    term = "202320"

    # FAST (NO DATA LOSS)
    create_terms_table(db)
    create_subjects_table(db)

    # VERY SLOW (NO DATA LOSS)

    # term_dicts = get_all_terms()

    # for term_dict in term_dicts:

    #     term = term_dict['TERM_CODE']

    #     print("STARTED UPDATE OF", term)
        
    #     update_courses_table(db, term)
    #     print("ENDED UPDATE OF", term)

    #     print("STARTED SLEEP OF", term)
    #     time.sleep(60)
    #     print("ENDED SLEEP OF", term)

    # FAST (DATA LOSS)

    if recreate_perm_tables:
        print("did recreate perm tables")

        recreate_attributes_table(db)
        recreate_levels_table(db)
        recreate_part_of_term_codes_table(db)
    else:
        print("did not recreate perm tables")

## CREATE TABLE FUNCTIONS ##

def create_terms_table(db):
    print('create_terms_table')

    # Clear Terms
    terms_collection = db.collection('terms')
    delete_collection(terms_collection)

    # Repopulate Terms
    active_terms = open_api_get_active_terms().json()
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

def create_subjects_table(db):
    print('create_subjects_table')

    # Clear Subjects
    subjects_collection = db.collection('subjects')
    delete_collection(subjects_collection)

    # Repopulate Subjects
    subjects = open_api_get_subjects().json()
    for subject in subjects:
        subj_code = subject['STVSUBJ_CODE']
        subj_desc = subject['STVSUBJ_DESC']
        doc_name = f'subject-{subj_code}'

        subjects_collection.document(doc_name).set({
            'SUBJ_CODE': f'{subj_code}',
            'SUBJ_DESC': f'{subj_desc}'
        })

def create_courses_table(db, term):
    print('create_courses_table')

    courses_table_name = f'courses-{term}'

    # Clear Courses
    courses_collection = db.collection(courses_table_name)
    delete_collection(courses_collection)

    # Repopulate Courses
    for subject in get_all_subjects():
        courses = open_api_get_open_courses(subject['SUBJ_CODE'], term).json()
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

## RECREATE TABLE FUNCTIONS ##

def recreate_attributes_table(db):
    print('recreate_attributes_table')

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

def recreate_levels_table(db):
    print('recreate_levels_table')

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

def recreate_part_of_term_codes_table(db):
    print('recreate_part_of_term_codes_table')

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

## PER QUERY FUNCTIONS ##

def get_and_update_course_details_table(db, term, crn):

    print('get_and_update_course_details_table', term, crn)

    course_details_table_name = f'course-details-{term}'

    course_details_collection = db.collection(course_details_table_name)

    course_details_doc_name = f'course-details-{crn}'

    # Delete document if it already exists
    course_details_collection.document(course_details_doc_name).delete()

    # Get new course details JSON
    course_details = open_api_get_course_details(term, crn).json()

    co_req = course_details['COREQ']
    course_desc = course_details['COURSEDESC']

    course_meet_building = course_details['CRSMEET']['building']
    course_meet_days = course_details['CRSMEET']['days']
    course_meet_room = course_details['CRSMEET']['room']
    course_meet_time = course_details['CRSMEET']['time']

    if (course_details['MAJOR']['Exclude'] is None):
        major_exclude = []
    else:
        major_exclude = course_details['MAJOR']['Exclude'].split(', ')
    
    if (course_details['MAJOR']['Include'] is None):
        major_include = []
    else:
        major_include = course_details['MAJOR']['Include'].split(', ')

    pre_req = course_details['PREREQ']

    if (course_details['SCPROG']['Exclude'] is None):
        sc_prog_exclude = []
    else:
        sc_prog_exclude = course_details['SCPROG']['Exclude'].split(', ')
    
    if (course_details['SCPROG']['Include'] is None):
        sc_prog_include = []
    else:
        sc_prog_include = course_details['SCPROG']['Include'].split(', ')


    crn_id = course_details['SSBSECT_CRN']
    course_id = course_details['SSBSECT_CRSE_NUMB']
    end_date = course_details['SSBSECT_PTRM_END_DATE']
    start_date = course_details['SSBSECT_PTRM_START_DATE']
    subject_code = course_details['SSBSECT_SUBJ_CODE']
    term_code = course_details['SSBSECT_TERM_CODE']
    wait_avail = course_details['SSBSECT_WAIT_AVAIL']
    wait_capacity = course_details['SSBSECT_WAIT_CAPACITY']

    course_details_doc_dict = {
        'CO_REQ': f'{co_req}',
        'COURSE_DESC': f'{course_desc}',
        'MEET_BUILDING': f'{course_meet_building}',
        'MEET_DAYS': f'{course_meet_days}',
        'MEET_ROOM': f'{course_meet_room}',
        'MEET_TIME': f'{course_meet_time}',
        'MAJOR_EXCLUDE': major_exclude,
        'MAJOR_INCLUDE': major_include,
        'PRE_REQ': f'{pre_req}',
        'SC_PROG_EXCLUDE': sc_prog_exclude,
        'SC_PROG_INCLUDE': sc_prog_include,
        'CRN_ID': f'{crn_id}',
        'COURSE_ID': f'{course_id}',
        'END_DATE': f'{end_date}',
        'START_DATE': f'{start_date}',
        'SUBJECT_CODE': f'{subject_code}',
        'TERM_CODE': f'{term_code}',
        'WAIT_AVAIL': f'{wait_avail}',
        'WAIT_CAPACITY': f'{wait_capacity}',
    }

    course_details_collection.document(course_details_doc_name).set(course_details_doc_dict)

    return course_details_doc_dict

## DELETE FUNCTIONS ##

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
    term_dicts = get_all_terms()

    attr_list = []

    for term_dict in term_dicts:
        term = term_dict['TERM_CODE']
        courses_table_name = f'courses-{term}'
        
        collection = db.collection(courses_table_name)
        courses_docs = collection.get()

        for course_doc in courses_docs:
            course_attrs = course_doc.to_dict()["COURSE_ATTR"]
            attr_list.extend(course_attrs)

    attr_set = set(attr_list)
    attr_list = list(attr_set)

    attr_list.sort()

    return attr_list

def get_all_levels_from_courses():

    db = firestore.client()
    term_dicts = get_all_terms()

    levels_list = []

    for term_dict in term_dicts:
        term = term_dict['TERM_CODE']
        courses_table_name = f'courses-{term}'
        
        collection = db.collection(courses_table_name)
        courses_docs = collection.get()

        for course_doc in courses_docs:
            course_attrs = course_doc.to_dict()["COURSE_LEVEL"]
            levels_list.extend(course_attrs)

    levels_set = set(levels_list)
    levels_list = list(levels_set)

    levels_list.sort()

    return levels_list

def get_all_part_of_term_codes_from_courses():

    db = firestore.client()
    term_dicts = get_all_terms()

    part_of_codes_list = []

    for term_dict in term_dicts:
        term = term_dict['TERM_CODE']
        courses_table_name = f'courses-{term}'
        
        collection = db.collection(courses_table_name)
        courses_docs = collection.get()

        for course_doc in courses_docs:
            course_attrs = course_doc.to_dict()["PART_OF_TERM"]
            part_of_codes_list.append(course_attrs)

    part_of_codes_set = set(part_of_codes_list)
    part_of_codes_list = list(part_of_codes_set)

    part_of_codes_list.sort()

    return part_of_codes_list

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

def get_course_details(term, crn):

    db = firestore.client()

    course_details_dict = get_and_update_course_details_table(db, term, crn)

    return course_details_dict
        