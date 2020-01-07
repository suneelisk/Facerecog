from django.shortcuts import render

# Create your views here.
# accounts/views.py
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic

import face_recognition
import cv2
import numpy as np
import pandas as pd
import time
import threading
from datetime import datetime
from datetime import date
import openpyxl
import smtplib
import os

class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


def facerecog(request):
    video_capture = cv2.VideoCapture(0)


    scope = [r'https://spreadsheets.google.com/feeds', r'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(r'C:\Users\System2\Downloads\Nokia Employee Access\client_secret.json', scope)
    client = gspread.authorize(creds)

    sheett = client.open("data").sheet1
    cellss = sheett.get_all_values()
    row = len(cellss)
    data = pd.DataFrame(cellss)

    asa = []

    for img in data[0]:
        img = filename+'\\'+img
        image = face_recognition.load_image_file(img)
        img1 = img.replace('.','')
        locals()["Name_" + str(img1)] = face_recognition.face_encodings(image)[0]
        asa.append(locals()["Name_" + str(img1)])

    # Create arrays of known face encodings and their name
    known_face_encodings =  asa
    known_face_names = list(data["Details"])

    main_loop_running = True
    def capture():
        global frame
        while (main_loop_running):
            ret, frame = video_capture.read()
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = small_frame[:, :, ::-1]

            if main_loop_running:
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []

            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"


                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)
                now = datetime.now()
                dates = datetime.today().strftime("%Y-%m-%d %H:%M:%S")

                print(name, "Loggedin", now)


                sheet = client.open("loginlogout").sheet1
                cells = sheet.get_all_values()
                row = len(cells)
                NAME = name
                DATE = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                Arow = [NAME, DATE]
                index = row + 1
                #print(index)
                sheet.insert_row(Arow, index)

                df = pd.DataFrame(cells)
                #print(df)
                df["DATEin"] = df.groupby([0])[1].shift(1)
                df["Rank"]=df.groupby([0]).cumcount()+1
                df1 = df[df.Rank%2==0]
                df1['working_hours']= (pd.to_datetime(df1[1]) -
                                                 pd.to_datetime(df1['DATEin']))
                data11 = df1.drop(['Rank'], axis = 1)
                data11=data11.groupby([0,'DATEin'])['working_hours'].sum().reset_index()
                print(data11)

                def check(list1, val):
                    for x in list1:
                        if val == x:
                            return True
                    else:
                        return False

                if check(data[1], name):
                    #print(i)
                    root = Tk()
                    root.title("Faec Recognition")
                    root.geometry('300x200')
                    root.configure(background="black")

                    message = "Successfully Logged in"+str(' ')+str(name)

                    messagevar = Message(root, text = message, width = 250)
                    messagevar.config(bg = 'white',font=("Courier", 10), fg = 'green')
                    messagevar.pack(side="top", padx = 25, pady = 50)
                    root.after(2500, lambda:root.destroy())
                    root.mainloop()
                else:
                    gmail_user = "suneel17021995@gmail.com"
                    gmail_pwd = "nagaganta"
                    TO = 'suneel19951702@gmail.com'
                    SUBJECT = "Testing sending using gmail"
                    TEXT = "Unknown person tried to access your Machine"
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.ehlo()
                    server.starttls()
                    server.login(gmail_user, gmail_pwd)
                    BODY = '\r\n'.join(['To: %s' % TO,
                            'From: %s' % gmail_user,
                            'Subject: %s' % SUBJECT,
                            '', TEXT])

                    server.sendmail(gmail_user, [TO], BODY)

                    root1 = Tk()
                    root1.title('Face Not Recognized')
                    root1.geometry('300x200')
                    root1.configure(background = 'black')

                    message1 = "Your face was not recognized please wait"

                    messagevar1 = Message(root1, text = message1, width = 250)
                    messagevar1.config(bg = 'white', font = ("Courier", 10), fg = 'red')
                    messagevar1.pack(side = 'top', padx = 25, pady = 50)
                    root1.after(2500, lambda: root1.destroy())
                    root1.mainloop()

            time.sleep(5)
    ret, frame = video_capture.read()
    cv2.imshow('Webcam', frame)
    child_t = threading.Thread(target=capture)
    child_t.setDaemon(True)
    child_t.start()

    while(1):
        ret, frame = video_capture.read()
        cv2.imshow('Webcam', frame)

        # here I want to call capture() function every 3 seconds

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    main_loop_running = False
    child_t.join()

    video_capture.release()
    cv2.destroyAllWindows()
