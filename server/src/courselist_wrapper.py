
def update_courselist_database():

    db = firestore.client()  # this connects to our Firestore database
    collection = db.collection('terms')  # opens 'places' collection

    creation_result = collection.document('TEST-TERM-3').set({
        'TERM_CODE': '202410',
        'TERM_DESC': 'Fall 2023',
        'TERM_END_DATE': '2023-12-31T00:00:00'
    })