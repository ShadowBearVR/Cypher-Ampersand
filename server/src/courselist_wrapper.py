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

def test_courselist_db():

	print('test_courselist_db')

	# db = firestore.client()  # this connects to our Firestore database
    # collection = db.collection('terms')  # opens 'places' collection
    
    # docs = collection.get()

    # for doc_raw in docs:
    #     doc = doc_raw.to_dict()

    #     results = f'{doc["TERM_CODE"]} {doc["TERM_DESC"]} {doc["TERM_END_DATE"]}'


    # creation_result = collection.document('TEST-TERM-2').set({
    #     'TERM_CODE': '202410',
    #     'TERM_DESC': 'Fall 2023',
    #     'TERM_END_DATE': '2023-12-31T00:00:00'
    # })

    # context = { 
    #     'server_time': server_time,
    #     'results': results,
    #     'creation_result': creation_result
    # }