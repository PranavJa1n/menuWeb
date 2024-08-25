from flask import Flask, request, send_file, redirect, url_for, render_template_string, render_template, Response
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage
from geopy.geocoders import Nominatim
from googlesearch import search
from gtts import gTTS
import os
import uuid
import smtplib
import schedule
import time
from threading import Thread
from twilio.rest import Client
import geocoder
import cv2

app = Flask(__name__)

@app.route('/sendemails', methods=['POST'])
def send_emails():
    data = request.get_json()
    emails = data['emails']
    subject = data['subject']
    message = data['message']
    sender_email = "pranav.avlok@gmail.com"
    sender_password = "qtzi vtbd wgyu ynei"
    for email in emails:
        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, email, text)
            server.quit()
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    return jsonify({"status": "success", "message": "Emails sent successfully!"})

@app.route("/email", methods=["POST"])
def send_email():
    sender_email = request.form.get('sender_email')
    sender_password = request.form.get('sender_password')
    recipient_email = request.form.get('recipient_email')
    subject = request.form.get('subject')
    body = request.form.get('body')
    msg = EmailMessage()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.set_content(body)
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()
    return "Email sent successfully"

@app.route('/geo', methods=['GET'])
def geo():
    location_name = request.args.get('location')
    if location_name:
        geolocator = Nominatim(user_agent="my_geocoder")
        location = geolocator.geocode(location_name)
        if location:
            return {"latitude": location.latitude, "longitude": location.longitude}
        else:
            return {"error": "Location not found"}
        
@app.route("/gsearch", methods=["POST"])
def gsearch():
    query = request.form.get("query")
    r = []
    if query:
        count = 0
        for j in search(query, num_results=5):
            r.append(j)
            count += 1
            if count == 5:
                break
    return render_template("gsearch.html", results=r)

@app.route('/convert', methods=['POST'])
def convert_text_to_speech():
    text = request.form.get('text', '')
    if not text:
        return {'error': 'No text provided'}, 400
    language = 'en'
    filename = f"audio_{uuid.uuid4().hex}.mp3"
    # Generate audio file from text
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save(os.path.join('static', filename))  # Save in 'static' folder
    # Redirect to the audio playback page
    return redirect(url_for('play_audio', filename=filename))
@app.route('/play/<filename>')
def play_audio(filename):
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Playing Audio</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #2C3E50;
                    color: #ECF0F1;
                    margin: 0;
                    padding: 20px;
                    text-align: center;
                }
                audio {
                    margin-top: 20px;
                }
            </style>
        </head>
        <body>
            <h1>Playing Audio</h1>
            <audio controls autoplay>
                <source src="{{ url_for('static', filename=filename) }}" type="audio/mpeg">
                Your browser does not support the audio element.
            </audio>
        </body>
        </html>
    """)

def send_email(sender_email, sender_password, recipient_email, message):
    try:
        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        s.login(sender_email, sender_password)
        s.sendmail(sender_email, recipient_email, message)
        s.quit()
        return "Email sent successfully."
    except Exception as e:
        return f"Failed to send email: {str(e)}"
def schedule_email(timeinput, sender_email, sender_password, recipient_email, message):
    schedule.every().day.at(timeinput).do(lambda: send_email(sender_email, sender_password, recipient_email, message))
    while True:
        schedule.run_pending()
        time.sleep(1)
@app.route("/schedule_email", methods=["GET"])
def schedule_email_endpoint():
    sender_email = request.args.get("sender_email")
    sender_password = request.args.get("sender_password")
    recipient_email = request.args.get("recipient_email")
    message = request.args.get("message")
    timeinput = request.args.get("timeinput")
    if not all([sender_email, sender_password, recipient_email, message, timeinput]):
        return "Missing one or more required fields."
    thread = Thread(target=schedule_email, args=(timeinput, sender_email, sender_password, recipient_email, message))
    thread.start()
    return f"Email scheduled to be sent to {recipient_email} at {timeinput}."

@app.route("/sms", methods=["POST"])
def sms_():
    # Get the Twilio credentials and form data from the request
    accountsid = request.form['accountsid']
    authtoken = request.form['authtoken']
    msgbody = request.form['msgbody']
    from_phno = request.form['from_phno']
    to_phno = request.form['to_phno']
    # Initialize the Twilio client
    client = Client(accountsid, authtoken)
    # Send the SMS
    message = client.messages.create(body=msgbody, from_=from_phno, to=to_phno)
    return "Message sent successfully!"

@app.route('/geolocation')
def geolocation():
    # Get geolocation information
    g = geocoder.ip('me')
    latitude = g.latlng[0] if g.latlng else 'Not Available'
    longitude = g.latlng[1] if g.latlng else 'Not Available'
    address = g.address if g.address else 'Not Available'
    return render_template('geonew.html', latitude=latitude, longitude=longitude, address=address)

@app.route('/camglasses')
def camglasses():
    return render_template('camglasses.html')
def gen_frames():
    cap = cv2.VideoCapture(0)
    # Load the sunglasses image with transparency channel
    glasses_img = cv2.imread("deal-with-it-glasses-png-41918.png", cv2.IMREAD_UNCHANGED)
    # Original dimensions of the sunglasses image
    original_width, original_height = 370, 267
    # Desired width for the sunglasses image
    desired_width = 200  # Adjust as needed
    # Calculate the new height to maintain aspect ratio
    aspect_ratio = original_width / original_height
    desired_height = int(desired_width / aspect_ratio)
    # Resize the sunglasses image
    glasses_img = cv2.resize(glasses_img, (desired_width, desired_height))
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # Get the frame dimensions
            frame_height, frame_width = frame.shape[:2]
            # Calculate the placement coordinates to center the sunglasses
            x = (frame_width - desired_width) // 2
            # Position the sunglasses half screen above the center
            y = (frame_height // 2) - (desired_height // 2) - (frame_height // 4)  # Move up half screen
            # Define region of interest (ROI) where the glasses will be placed
            if x + desired_width <= frame_width and y + desired_height <= frame_height:
                # Create an overlay mask for transparency handling
                for c in range(0, 3):  # For RGB channels
                    frame[y:y+desired_height, x:x+desired_width, c] = glasses_img[:, :, c] * (glasses_img[:, :, 3] / 255.0) + frame[y:y+desired_height, x:x+desired_width, c] * (1.0 - glasses_img[:, :, 3] / 255.0)
            # Convert frame to JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
