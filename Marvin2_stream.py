import pathlib
import sys
from datetime import datetime
from playsound import playsound
from utils import *
from config import *

if __name__ == '__main__':
    if len(sys.argv)==1:
          lang='en'
    else: lang=sys.argv[1]

# Create transcript folder and file
pathlib.Path(transcripts_folder).mkdir(parents=True, exist_ok=True) 
now = datetime.now()
ts_filename = transcripts_folder + "/ts_"+ now.strftime("%Y_%m_%d_%H%M") + ".txt"

# initiallise 
prompt_count=0
messages =list()
system_instruction={"role": "system", "content": instruction}

#initial greeting
clear()
print(initial_greeting)
input()
user_prompt =speech_input(lang)

# write to transcript
with open(ts_filename, 'w+') as ts:
      ts.write(initial_greeting +'\n\n' + "Me: "+ user_prompt)

# keep chatting till user sets goodbye prompt
while ((user_prompt.rstrip('.').upper()) not in goodbye_prompts ):
        if prompt_count % instruction_frequency == 0: # re-issue instruction every now and then
            messages = remove_items(messages, system_instruction) # first remove all previouis occurence of system instruction to shorten message
            messages.append(system_instruction) # add new instruction
       
        messages.append({"role": "user", "content": user_prompt}) # keep the whole conversation together

        messages = trimmed(messages) # trim message if too many tokens

        # stream response

        response_text=""
        type_freq=0;

        response_stream = chat_response_stream(messages)
        print("\nMarvin: ", end='')
        sys.stdout.flush()
        for chunk in response_stream:
            if 'content' in chunk['choices'][0]['delta']:
                next_token=chunk['choices'][0]['delta']['content']
                print(next_token, end='') 

                type_freq = type_freq +1 
                if type_freq %2 ==0:
                    playsound('media/kbd1_1.m4a',True)
                sys.stdout.flush() 
                time.sleep(0.2-typing_speed/500) 
                response_text = response_text + next_token
        print('\n')

        # add response to transcript
        with open(ts_filename, 'a') as ts:
            ts.write('\n\nMarvin:' + response_text)
        prompt_count = (prompt_count + 1) 

        # add response to next message
        messages.append({"role": "assistant", "content": response_text})

        # ask for next prompt
        input()
        user_prompt = speech_input(lang)
        while user_prompt=='': #ignore accidental 'enter's pressed by user
            user_prompt =speech_input(lang)
        with open(ts_filename, 'a') as ts:
            ts.write('\n\n' + "Me: "+ user_prompt)

# say goodbye and exit
print('\n'+goodbye_msg)
with open(ts_filename, 'a') as ts:
    ts.write('\n\n\n' + goodbye_msg)