import firebase_admin
from firebase_admin import credentials, firestore

# Setup DB credentials.
cred = credentials.Certificate("env/cypher-ampersand-firebase-adminsdk-2694w-0d791d1fab.json")
firebase_admin.initialize_app(cred)

def update_courselist_db():

    db = firestore.client()  # this connects to our Firestore database
    collection = db.collection('terms')  # opens 'places' collection

    creation_result = collection.document('TEST-TERM-3').set({
        'TERM_CODE': '202410',
        'TERM_DESC': 'Fall 2023',
        'TERM_END_DATE': '2023-12-31T00:00:00'
    })

    # Clear Terms

    # Update Terms



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