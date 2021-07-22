import pyrebase

 
def initialize():
    firebaseConfig = {
    'apiKey': "AIzaSyANUQCqjUVlF0XYjrrb2kpOybz8y5pIl2c",
    'authDomain': "drowsiness-app-33e48.firebaseapp.com",
    'projectId': "drowsiness-app-33e48",
    'storageBucket': "drowsiness-app-33e48.appspot.com",
    'messagingSenderId': "5173025771",
    'appId': "1:5173025771:web:65c2ed3eb827d0ea6297ae",
    'databaseURL':"https://drowsiness-app-33e48-default-rtdb.firebaseio.com/"
    }
    firebase = pyrebase.initialize_app(firebaseConfig)
    auth = firebase.auth()
    db = firebase.database()
    return auth,db
