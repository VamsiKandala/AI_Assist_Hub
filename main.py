from flask import Flask, request, redirect,render_template,url_for,flash,session
from playsound import playsound
import datetime,time
import cx_Oracle
import smtplib
import random
import math
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from gtts import gTTS
import speech_recognition as sr
from time import ctime
import uuid
import webbrowser
import os,re #to read files from your local system


con = cx_Oracle.connect('vamsi/vamsi@localhost:1521/xe')
cursor=con.cursor()

app = Flask(__name__)
app.secret_key = "super secret key"

msg=''
OtP=''
@app.route('/')
def home():
    return render_template('Home.html')

@app.route('/topbar')
def topbar():
    return render_template('topbar.html')

@app.route('/leftmenu')
def leftmenu():
    return render_template('leftmenu.html')

@app.route('/centerbox')
def centerbox():
    return render_template('centerbox.html')

@app.route('/rightmenu')
def rightmenu():
    return render_template('rightmenu.html')

@app.route('/sendemail')
def sendemail():
    return render_template('sendemail.html')


@app.route('/otpverification',methods=['GET','POST'])
def otpverification():
    if request.method == 'POST':
        oTp=request.form['otp']
        result=cursor.execute("select * from oTp ")
        record=result.fetchone()
        ab=record[0]
        con.commit()
        if (oTp==ab):
            return render_template('sendemail.html',message='Valid OTP')
        else:
            return render_template('otpverification.html',message='Invalid OTP')
    return render_template('otpverification.html')

@app.route('/virtualassistant')
def virtualassistant():
    while True:
        global print
        def listen():
            """Listening function to respond what we speak"""
            r = sr.Recognizer()
            with sr.Microphone() as source:
                print("Start talking now...") #own statement
                audio = r.listen(source,phrase_time_limit=10) #time limit is user interest
                data="" #whatever we speak it will be stored in it
            try:
                data = r.recognize_google(audio,language='en-US')
                print("You said:"+data)
            except sr.UnknownValueError:
                print("I cannot hear you speak louder")
            except sr.RequestError as e:
                print("Microphone is not working")
            return data
        #tts = gTTS(text=data)
        #tts.save("audio.mp3")
        #playsound.playsound("audio.mp3")
        #listen()

        #another function to respond back
        def respond(speech):
            """Function for responding back"""
            tts = gTTS(text=speech)
            tts.save("Speech.mp3")
            filename = "Speech%s.mp3"%str(uuid.uuid4())
            tts.save(filename)
            playsound(filename)
            os.remove(filename)
    
        #we will give actionsto our virtual assistant

        def virtual_asstnt(data):
            if "how are you" in data:
                listening = True
                respond("I am good hope you are doing well")
                data = listen()
                listening = virtual_asstnt(data)
            elif "name" in data:
                listening = True
                respond("My name is Tessa. I am developed by Mr.Vamsi Krishna")
                data = listen()
                listening = virtual_asstnt(data)
            elif "time" in data:
                listening = True
                respond(ctime())
                data = listen()
                listening = virtual_asstnt(data)
            elif "i love you" in data:
                listening = True
                respond("Awww !! So Sweet to listen that you love mee!! I love You Too!!")
                data = listen()
                listening = virtual_asstnt(data)
            elif "open google" in data.lower():
                listening = True
                url = "https://www.google.com/"
                webbrowser.open(url)
                respond("Success")
                data = listen()
                listening = virtual_asstnt(data)
            elif "locate" in data:
                listening = True
                webbrowser.open('https://www.google.com/maps/search/'+
                        data.replace("locate",""))
                result = "Located"
                respond("Located {}".format(data.replace(
                "locate","")))
                data = listen()
                listening = virtual_asstnt(data)
            elif "play music" in data:
                listening = True
                respond("Playing")
                playsound("Apna Bana Le Piya - Bhediya - Lofi ! Hindi.mp3")
                while playsound:
                    data = listen()
                    listening = virtual_asstnt(data)
            elif "word" in data.casefold(): #same you can link for other shortcuts
                listening = True
                os.startfile(r'C:/Program Files/Microsoft Office/root/Office16/WINWORD.EXE')
                respond("Success")
                data = listen()
                listening = virtual_asstnt(data)
            elif "stop talking" in data:
                listening = False
                respond("Okay bye take care")
            try:
                return listening
            except:
                print("Timed out")
        respond("Hey Vamsi Good to talk with again.How can I Help you") #frst greeting
        listening=True
        while listening==True:
            data = listen()
            listening = virtual_asstnt(data)
            return render_template('virtualassistant.html')

@app.route('/SendSMS')
def SendSMS():
    return render_template('SendSMS.html')

@app.route('/alarm',methods=['GET','POST'])
def alarm():
    if request.method == 'POST':
        alarm_time = request.form['alarm_time']
        alarm_message = request.form['alarm_message']
        # convert alarm time to datetime object
        alarm_datetime = datetime.datetime.strptime(alarm_time, '%Y-%m-%dT%H:%M')
        # calculate time difference between now and alarm time
        time_diff = (alarm_datetime - datetime.datetime.now()).total_seconds()
        # play sound after time difference elapses
        while True:
            #print(time_diff)
            time.sleep(time_diff)
            playsound('Alarm Clock Alarm.mp3')
            return render_template('index.html', success_message='Alarm set for {} with message  "{}"'.format(alarm_time, alarm_message))
        '''if(time_diff == '0'):
            playsound('alarm.wav')
            return render_template('index.html', success_message='Alarm set for {} with print "{}"'.format(alarm_time, alarm_message))'''
        
        
        

    return render_template('Alarm.html') 
@app.route('/gmailregistration',methods=['GET','POST'])
def gmailregistration():
    if request.method == 'POST':
        uname=request.form['username']
        uappcode=request.form['AppPasscode']
        upass=request.form['Password']
        result=cursor.execute("insert into greg values(:s,:s,:s)",(uname,uappcode,upass))
        con.commit()
        return redirect(url_for('gmaillogin'))
    return render_template('gmailformregistration.html')
    
@app.route('/gmaillogin',methods=['GET','POST'])
def gmaillogin():
    if request.method == 'POST':
        un=request.form['username']
        up=request.form['Password']
        result=cursor.execute("select * from greg where username=:s and password=:s",(un,up))
        record=result.fetchone()
        if record:
            session['loggedin']=True
            session['username']=record[0]
            return redirect(url_for('sendemail'))
        con.commit()
    return render_template('gmaillogin.html')

@app.route('/mailwithotpgeneration',methods=['GET','POST'])
def mailwithotpgeneration():
    if request.method == 'POST':
        Sender=request.form['sender']
        password=request.form['password']
        Receiver=request.form['receiver']
        result=cursor.execute("select * from greg where username=:s and password=:s" ,(Sender,password))
        record=result.fetchone()
        appcode=record[1]
        print=(appcode)
        if record:
            sender = Sender  #give your email id
            receiver = Receiver #give receiver gmailid or take user input
            subject="Otp Generation"
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = receiver
            msg['Subject'] = subject
            text = msg.as_string()
            #Email Automation using Python -->smtplib,email packages
            #smptlib -->Simple Mail Transfer Protocol

            #connect to the server
            server = smtplib.SMTP('smtp.gmail.com',587) #give gmail outgoing smtp address
            #along with TLS port number
            #start the server
            server.starttls()
            #login to gmail
            server.login(Sender,appcode) #give your gmail address and
            #gmail app passcode
            #write your desired print
            #msg = "Hey hai this is first mail using Python"
            #we can include random number to it
            msg = "OTP is "+str(random.randint(1000,9999)) 
            receiver_mail = Receiver
            #send the mail
            server.sendmail("krishkandala143@gmail.com",receiver_mail,msg)
            return render_template('sendemail.html',message='Mail Sent!!!!')


    return render_template('mailwithotpgeneration.html')


@app.route('/mailwithotpverification',methods=['GET','POST'])
def mailwithotpverification():
    if request.method == 'POST':
        Sender=request.form['sender']
        Password=request.form['password']
        Receiver=request.form['receiver']
        result=cursor.execute("select * from greg where username=:s and password=:s" ,(Sender,Password))
        record=result.fetchone()
        appcode=record[1]
        if record:
            sender = Sender  #give your email id
            receiver = Receiver #give receiver gmailid or take user input
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = receiver
            msg['Subject'] = 'Otp Generation and Verification'
            #OTP Verification to Email
            #OTP Creation -->math  module and random module
            #we will generate 6digit otp using base digits
            digits = "0123456789"
            OTP=''
            #now we will use math module along with module to generate a customized
            #6 digit otp
            for i in range(6):
                OTP = OTP + digits[math.floor(random.random()*10)]
            #print=(OTP)
            message = OTP + " is your OTP"
            #print=(msg)


            #link the above otp to our email and then we will go for verification
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(Sender,appcode) #gmail and app passcode
            user=Sender
            receiver = Receiver
            s.sendmail(user,receiver,message)
            aa=1
            otdt=cursor.execute("update oTp set oTp=:s where sno=:s",(OTP,aa))
            con.commit()

            if s.sendmail:
                return redirect(url_for('otpverification'))
                           
            #otp verification  -->include your time module
            
    return render_template('mailwithotpverification.html')



@app.route('/mailwithattach',methods=['GET','POST'])
def mailwithattach():
    if request.method == 'POST':
        Sender=request.form['sender']
        Password=request.form['password']
        Receiver=request.form['receiver']
        Subject=request.form['subject']
        Body=request.form['body']
        attach=request.files['myfile']
        result=cursor.execute("select * from greg where username=:s and password=:s" ,(Sender,Password))
        record=result.fetchone()
        appcode=record[1]
        print=(attach)
        if record:
            sender = Sender  #give your email id
            receiver = Receiver #give receiver gmailid or take user input
            subject = Subject #give your own subject
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = receiver
            msg['Subject'] = subject

            body = Body
            filename=attach.filename
            attach.save(filename)
            msg.attach(MIMEText(body))

            #we will make our attachment to be encoded and added to our mail
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(open(filename,'rb').read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {filename}')
            msg.attach(part)
            text = msg.as_string() #include this as final msg in sendmail

            #same include your base email code -->smtplib
            server= smtplib.SMTP('smtp.gmail.com',587)
            server.starttls()
            #login to the gmail
            server.login(sender,appcode)  #give your app passcode
            server.sendmail(sender,receiver,text)
            if server.sendmail:
                return render_template('sendemail.html',message="Mail Sent !!")

    return render_template('mailwithattach.html')

@app.route('/mailwithsubject',methods=['GET','POST'])
def mailwithsubject():
    if request.method == 'POST':
        Sender=request.form['sender']
        Password=request.form['password']
        Receiver=request.form['receiver']
        Subject=request.form['subject']
        Body=request.form['body']
        result=cursor.execute("select * from greg where username=:s and password=:s" ,(Sender,Password))
        record=result.fetchone()
        appcode=record[1]
        if record:
            sender = Sender  #give your email id
            receiver = Receiver #give receiver gmailid or take user input
            subject = Subject #give your own subject
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = receiver
            msg['Subject'] = subject
   
            body = Body
            msg.attach(MIMEText(body,'plain'))
            text = msg.as_string() #include this as final msg in sendmail

            #same include your base email code -->smtplib
            server= smtplib.SMTP('smtp.gmail.com',587)
            #login to the gmail
            server.starttls()
            server.login(sender,appcode)  #give your app passcode
            server.sendmail(sender,receiver,text)
            if server.sendmail:
                return render_template('sendemail.html',message='Mail Sent !!')
    return render_template('mailwithsubject.html')

@app.route('/resetappcode',methods=['GET','POST'])
def resetappcode():
    if request.method == 'POST':
        uname=request.form['username']
        uappcode=request.form['AppPasscode']
        upass=request.form['Password']
        result=cursor.execute("update  greg set appcode=:s where username=:s and password=:s",(uappcode,uname,upass))
        con.commit()
        return redirect(url_for('gmaillogin'))

    return render_template('resetappcode.html')



if __name__ == '__main__':
    app.run(debug=True)