from config import *
#import os
#import pathlib
#from datetime import datetime
import time
#import sys
import openai
import tiktoken
import database
import re
#import speech_recognition as sr
from openai import OpenAI, APIError, APITimeoutError,RateLimitError, APIConnectionError, APIStatusError
client = OpenAI()

system_instruction={"role": "system", "content": INSTRUCTION}

# function to remove item from a list
def remove_items(test_list, item):
    res = [i for i in test_list if i != item]
    return res

# truncate message if too long; drop old messages in conversation
def trimmed(messages, token_buffer = TOKEN_BUFFER, max_token = MAX_TOKEN, model_engine=MODEL_ENGINE):
    while num_tokens_from_messages(messages, model=model_engine) > max_token - token_buffer :
        messages=messages[1:]
    return messages


def marvin(user_message):
    waid = user_message["waid"]
    content = user_message["content"]

    # Query the database for recent messages
    messages = database.get_recent_messages(waid=waid, days=MAX_DAYS)

 
    #add system instruction
    messages.append(system_instruction) # add new instruction

    # Add the user message to the message list and database
    messages.append({"role":"user","content":content})
    database.add_message(waid=waid, role='user', content=content)

    print(str(messages))
    print("\n\n")
    # trim message if too many tokens
    messages = trimmed(messages) 
    print(str(messages))
    print("\n\n")
    # generate response and write into database
    response = chat_response(messages)
    database.add_message(waid=waid, role='assistant', content=response)
    return response

# Chat Response Function
def chat_response(messages):
    try:
        completion = client.chat.completions.create(
            model = MODEL_ENGINE,
            frequency_penalty = 2 - REPEAT_FACTOR / 25,
            temperature = RANDOMNESS/50,
            messages = messages
        )
        response = completion.choices[0].message.content.strip()
    except openai.error.RateLimitError:
        time.sleep(60)
        completion = client.chat.completions.create(
            model = MODEL_ENGINE,
            frequency_penalty = 2 - REPEAT_FACTOR / 25,
            temperature = RANDOMNESS/50,
            messages = messages
        )       
        response = completion.choices[0].message.content.strip()
    return response


# count number of tokens in message
def num_tokens_from_messages(messages, model=MODEL_ENGINE):
  """Returns the number of tokens used by a list of messages."""
  try:
      encoding = tiktoken.encoding_for_model(model)
  except KeyError:
      encoding = tiktoken.get_encoding("cl100k_base")
  if model == MODEL_ENGINE:  # note: future models may deviate from this
      num_tokens = 0
      for message in messages:
          num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
          for key, value in message.items():
              num_tokens += len(encoding.encode(value))
              if key == "name":  # if there's a name, the role is omitted
                  num_tokens += -1  # role is always required and always 1 token
      num_tokens += 2  # every reply is primed with <im_start>assistant
      return num_tokens
  else:
      raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}""")


def split_paragraph_into_sentences(paragraph):
    sentences = re.split(r'(?<=[.!?]) +', paragraph)
    return sentences
def split_sentence_into_words(sentence):
    return sentence.split(' ')

def split_message(message, chunk_size=MAX_CHAR_LIMIT):
    paragraphs = message.split('\n')
    chunks = []
    current_chunk = ''
    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            sentences = split_paragraph_into_sentences(paragraph)
            for sentence in sentences:
                if len(sentence) > chunk_size:
                    words = split_sentence_into_words(sentence)
                    for word in words:
                        if len(current_chunk) + len(word) + 1 > chunk_size:
                            if current_chunk:
                                chunks.append(current_chunk)
                                current_chunk = word
                            else:
                                while len(word) > chunk_size:
                                    chunks.append(word[:chunk_size])
                                    word = word[chunk_size:]
                                current_chunk = word
                        else:
                            if current_chunk:
                                current_chunk += ' ' + word
                            else:
                                current_chunk = word
                else:
                    if len(current_chunk) + len(sentence) + 1 > chunk_size:
                        if current_chunk:
                            chunks.append(current_chunk)
                            current_chunk = sentence
                        else:
                            chunks.append(sentence[:chunk_size])
                            current_chunk = sentence[chunk_size:]
                    else:
                        if current_chunk:
                            current_chunk += ' ' + sentence
                        else:
                            current_chunk = sentence
        else:
            if len(current_chunk) + len(paragraph) + 1 > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = paragraph
                else:
                    chunks.append(paragraph[:chunk_size])
                    current_chunk = paragraph[chunk_size:]
            else:
                if current_chunk:
                    current_chunk += '\n' + paragraph
                else:
                    current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

'''
# listen to speech input from microphone and record on to a wav file
def listen_to_user() :
    r = sr.Recognizer()
    r.energy_threshold = 4000
    with sr.Microphone() as source:
        print("speak now")
        audio = r.listen(source=None, phrase_time_limit=None)

    pathlib.Path(audio_prompts_folder).mkdir(parents=True, exist_ok=True) 
    now = datetime.now()
    audio_filename = audio_prompts_folder + "/ap_"+ now.strftime("%Y_%m_%d_%H%M") + ".wav"
    with open(audio_filename, 'wb') as audio_file:
        audio_file.write(audio.get_wav_data())
    return audio_filename

# take speech input in any language
def speech_input(lang):
    if lang == 'en':
        return speech_input_en()
    elif lang == 'or':
        return speech_input_or()
    else: return speech_input_lang(lang)

# function to get speech input in English
def speech_input_en():
    audio_filename = listen_to_user()
    try:
        with open(audio_filename,'rb') as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file, language='en')["text"]
    except (APIError,RateLimitError ):
        time.sleep(60)
        with open(audio_filename,'rb') as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file, language='en')["text"]
    print("You: " + transcript)
    return transcript

# function to get speech input in Odia
def speech_input_or():
    audio_filename = listen_to_user()
    try:
        with open(audio_filename,'rb') as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)["text"]
    except (APIError,RateLimitError):
        time.sleep(60)
        with open(audio_filename,'rb') as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)["text"]
    print("You: " + transcript)
    return transcript

# function to get speech input in non-English language
def speech_input_lang(lang):
    audio_filename = listen_to_user()
    try:
        with open(audio_filename,'rb') as audio_file:
            audio_ts = openai.Audio.translate("whisper-1", audio_file)
    except (APIError,RateLimitError):
        time.sleep(60)
        with open(audio_filename,'rb') as audio_file:
            audio_ts = openai.Audio.translate("whisper-1", audio_file)
    try:
        with open(audio_filename,'rb') as audio_file:
            transcript_orig = openai.Audio.transcribe("whisper-1", audio_file, language=lang)["text"]
    except (APIError,RateLimitError):
        time.sleep(60)
        with open(audio_filename,'rb') as audio_file:
            transcript_orig = openai.Audio.transcribe("whisper-1", audio_file, language=lang)["text"]
    transcript = audio_ts["text"]
    print("You: " + transcript_orig)
    print("("+transcript+")")
    return transcript



# print text on screen one character at a time
def print_response(text):
    for char in text: 
        print(char, end='') 
        sys.stdout.flush() 
        time.sleep(0.03) 

'''





'''
# stream chat Response Function
def chat_response_stream(question_message):
    try:
        response = openai.ChatCompletion.create(model=model_engine,messages=question_message, frequency_penalty=2-REPEAT_FACTOR/25, temperature=randomness/50, stream=True)
    except openai.error.RateLimitError:
        time.sleep(60)
        response = openai.ChatCompletion.create(model=model_engine,messages=question_message, frequency_penalty=2-REPEAT_FACTOR/25, temperature=randomness/50, stream=True)
    return response
'''



'''  
# define our clear function
def clear(): 
    # for windows
    if os.name == 'nt':
        _ = os.system('cls')
 
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = os.system('clear')

# run listen in background and wait for wake phrase 
def listen_in_background():
    r = sr.Recognizer()
    source = sr.Microphone()
    r.listen_in_background(source, wake_up_phrase)
    time.sleep(1000000)

# check if the text listened to in backgroud contains wakeup phrase
'''
