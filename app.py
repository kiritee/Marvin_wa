from flask import Flask, request, render_template
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from openai import OpenAI
from dotenv import find_dotenv, load_dotenv
import os
from utils import marvin, split_message
from config import MAX_CHAR_LIMIT
import requests

# Load all keys from .env
_ = load_dotenv(find_dotenv())
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

app = Flask(__name__)

# app.secret_key = os.getenv('SECRET_KEY', 'mysecret')


# Initialize OpenAI API key
# openai.api_key = 'YOUR_OPENAI_API_KEY'

client = OpenAI()
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/")
def hello():
  return "Hello World!"

# Response when a message is received
@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    #get user's message
    user_message = {
        'waid' : request.values.get('WaId', '').strip(),
        'content':request.values.get('Body', '').strip(),
    }

    user_number = request.values.get('From', '')
    marvin_number = request.values.get('To', '')

    # Check if there is media (voice message)
    num_media = int(request.values.get('NumMedia', 0))
    if num_media > 0:
        media_url = request.values.get('MediaUrl0')
        media_type = request.values.get('MediaContentType0')
        # Download the media file
        media_response = requests.get(media_url)
        media_file_path = f"temp_media.{media_type.split('/')[1]}"
        with open(media_file_path, 'wb') as media_file:
            media_file.write(media_response.content)
        user_message['media'] = media_file_path


    # Pass it to Marvin and get response back
    reply = marvin(user_message)

    # Split the reply if it's longer than MAX_CHAR_LIMIT at paragraph, sentence, and word boundaries
    reply_chunks = split_message(reply, MAX_CHAR_LIMIT)

    # Send each chunk in the correct order
    for chunk in reply_chunks:
        message = client.messages.create(
            from_=marvin_number,  # Your Twilio WhatsApp number
            body=chunk,
            to=user_number
        )

    # Return the reply (or some acknowledgment if preferred)
    return reply
    
# display all messages
@app.route('/all')
def display_all_messages():
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    messages = client.messages.list(limit=20)
    return render_template('all.html', messages=reversed(messages))


'''
def process_message(incoming_msg):
    # Example: Simple response using GPT

    # return "uh oh! I am still not intelligent enough"

    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Talk like you are Marvin from Hitchhikers Guide to the Galaxy. Do not repeat any phrase you have said verbatim in the same conversation"},
                {"role": "user", "content": incoming_msg}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error: {str(e)}"
'''


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
