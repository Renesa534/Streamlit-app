######### LIBRARIES ##############
import streamlit as st          #GUI
from utils import initialize    #CONNECT WITH firebase
import re   
import os                       #Operating System 
import face_recognition         # For Face Recognition
import cv2                      #Image Manipulation
import numpy as np              #Numerical Mnipulation
import dlib                     #Detect Eyes
from tensorflow import keras    #Machine leanring
import pandas as pd             #Creating Tablular Data
import playsound
# Load All models
detector = dlib.get_frontal_face_detector() 
# https://github.com/italojs/facial-landmarks-recognition/blob/master/shape_predictor_68_face_landmarks.dat
predictor=dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
model =   keras.models.load_model("model.h5")
#HR-0619850034761

status = st.empty() 
st.title('Drowsy')
nav = st.sidebar.selectbox("Navigate",['Login','Sign Up'])
auth ,db= initialize()

if nav == 'Sign Up':
    checks = st.sidebar.empty()
    fname,lname,dob =st.text_input('First Name'),st.text_input('Last Name'),st.date_input("Date of Birth")
    lno = st.text_input("Licence Number")
    # HR-0619850034761
    m = st.text_input('Email')
    p = st.text_input('Password',type='password')
    p2 = st.text_input('Re-enterPassword',type='password')
    
    start_cam = st.checkbox("Start Camera")
    click= st.button("Capture Face")
    face_cap = st.empty()
    regex = ("^(([A-Z]{2}[0-9]{2})" +
             "( )|([A-Z]{2}-[0-9]" +
             "{2}))((19|20)[0-9]" +
             "[0-9])[0-9]{7}$")
    comp= re.compile(regex)
    
    if re.search(comp,lno):
        if re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$' ,m):
            checks.success('Correct mail')
    
            if (p == p2) and p!='' and p2!='':
                checks.success('Password Match')
                en={}
                path = f"face_enc/{fname}-{lname}-0.jpg"
                    
                if start_cam:
                    cam = cv2.VideoCapture(0)
                    
                    while(1):
                        ret,frame = cam.read()
                        face_cap.image(frame)
                        if click:
                            cv2.imwrite(path,frame)
                            cam.release()
                            break
                    
                submit = st.checkbox('Sign Up')
                if submit:
                    fenc = face_recognition.load_image_file(path)
                    fenc=face_recognition.face_encodings(fenc)[0]
                            
                    for i in range(128):
                        en[f'{i}']=fenc[i]
                    print(en)
            

                    user=auth.create_user_with_email_and_password(m,p)
                    print(en)
                    data = {
                        "fname": fname,
                        "lname":lname,
                        "dob":str(dob),
                        "licence_no":str(lno),
                        'enc':en
                        }
                    results = db.child("users").push(data, user['idToken'])
                    checks.success('Succesfully Created User')
                    
                    status.warning('Go to Login')
                
            else:
                checks.error("Password mismatch")

        else:
            checks.error("Incorrect Mail")
    else:
        checks.error('Wrong Licence Number')    
    #face_f(fname,lname,user['idToken'],db)



elif nav == 'Login':
    m = st.sidebar.text_input('Email')
    p = st.sidebar.text_input('Password',type='password')
    is_same_person=False
    status2 = st.sidebar.text('Verified:')
        
    submit = st.sidebar.checkbox('Login')
    if submit:
     
        user = auth.sign_in_with_email_and_password(m, p)
        idToken=user['idToken']
        encoding = list(dict(db.child('users').get().val()).values())
        encoding=np.array(encoding[0]['enc'])
        check_person = st.sidebar.checkbox('Start')
        
        window = st.empty()
        if check_person:
            cam = cv2.VideoCapture(0)
            while(1):
                r,f = cam.read()
                
                f=cv2.cvtColor(f,cv2.COLOR_BGR2RGB)
                window.image(f)
                currect_enc = face_recognition.face_encodings(f)
                
                if len(list(currect_enc))>0:
                    #print(currect_enc)
                    matches = face_recognition.compare_faces(encoding,face_recognition.face_encodings(f))
                    if matches[0]:
                        is_same_person=True
                        status2.text("Verified :"+str(is_same_person))
                        break
            if is_same_person:
                window=st.empty()
                cam = cv2.VideoCapture(0)
                
                lstatus,rstatus = st.sidebar.empty(),st.sidebar.empty()
                st.sidebar.text('Left Eye')
                leftwindow = st.sidebar.empty()
                st.sidebar.text("Right Eye")
                rightwindow = st.sidebar.empty()
                st.sidebar.text("Left Eye Probality")
                lgraph=st.sidebar.empty()
                st.sidebar.text("Right Eye Probablity")
                rgraph = st.sidebar.empty()


                ldata,rdata = pd.DataFrame(columns=['closed','open']),pd.DataFrame(columns=['closed','open'])
                while(1):
                    r,f = cam.read()
                    f=cv2.cvtColor(f,cv2.COLOR_BGR2RGB)
                    
                    detect=detector(f,1) 
                    if len(detect)>0:
                        shape=predictor(f,detect[0])
                        
                        x1=shape.part(36).x 
                        x2=shape.part(39).x 
                        y1=shape.part(37).y 
                        y2=shape.part(40).y
                        lefteye=f[y1-10:y2+10,x1-10:x2+10]

                        x1=shape.part(42).x
                        x2=shape.part(45).x
                        #43 46 #44 47 
                        y1=shape.part(43).y 
                        y2=shape.part(46).y 
                        righteye=f[y1-10:y2+10,x1-10:x2+10]
                                    
                        le=keras.preprocessing.image.array_to_img(lefteye)
                        re=keras.preprocessing.image.array_to_img(righteye)
                        
                        le=le.resize((244,244))
                        le=keras.preprocessing.image.img_to_array(le)
                        
                        re=re.resize((244,244))
                        re=keras.preprocessing.image.img_to_array(re)
                        
                        le=np.expand_dims(le, axis=0)
                        re = np.expand_dims(re,axis=0)
                                        

                        lprob,rprob =model.predict(le),model.predict(re)
                
                        ldata =ldata.append({"open":lprob[0][1],"closed":lprob[0][0]},ignore_index=True)
                        rdata =rdata.append({"open":rprob[0][1],"closed":rprob[0][0]},ignore_index=True)
                        lgraph.line_chart(ldata)
                        rgraph.line_chart(rdata)        
                        lpred = np.argmax(lprob)
                        rpred = np.argmax(rprob)
                        class_names = {0:"closed",1:"open"}
                        lstatus.text("Left Eye:"+str(class_names[lpred]))
                        rstatus.text("Right Eye:"+str(class_names[rpred]))

                        if lpred==0 or rpred==0:
                            status.error("Dont Sleep")
                            playsound.playsound('buzz.mp3')
                        else:
                            status.success("Driving Safely")                     

                        leftwindow.image(lefteye)
                        rightwindow.image(righteye)
                    window.image(f)
            
                status2.text("Verified :"+str(is_same_person))
        status.success('Logged in succesfully user '+str(user['localId']))
    

        