import openai
import os
from instructionlib import *
from dotenv import find_dotenv, load_dotenv

_ = load_dotenv(find_dotenv())
openai.api_key = os.getenv('OPENAI_API_KEY')

#to use alternate LLM running locally, uncomment below line
#openai.api_base = < loacal API URL , for instance "http://192.168.1.102:1234/v1">

#transcripts_folder = "./transcripts"
#audio_prompts_folder="./audio_prompts"

# Model Parameters
MODEL_ENGINE = "gpt-4o"
#"gpt-3.5-turbo"


CHATBOT="MARVIN"

INSTRUCTION=instructionlib[CHATBOT]

#tokens reserved for response while trimming long messages
TOKEN_BUFFER=300

#max token limit of the LLM
MAX_TOKEN=4096

# how frequently do you wish to issue instruction?
INSTRCTION_FREQUENCY= 1

# how much repetition is ok (on a scale of 1-100) ?
REPEAT_FACTOR = 5

# how much randomness do you wish in responses (on a scale of 1-100)?
RANDOMNESS = randomnesslib[CHATBOT]

# Response typing speed (on a scale of 1-100)?
#typing_speed = 60

#how many days of conversations to remember
MAX_DAYS = 3

# Text Messages
INITIAL_GREETING= "Marvin: Hi, I am Marvin! How can I help you today?\n"
GOODBYE_PROMPTS=("QUIT","THANK YOU","BYE","GOODBYE")
GOODBYE_MSG="Marvin: Thank You for taking my services. Hope you have a good day, or maybe not!"

#WAKE_UP_PHRASE=('wake up','WAKE UP')

#TWILIO max characters in whatsapp message
MAX_CHAR_LIMIT = 1600