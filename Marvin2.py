import pathlib
from datetime import datetime
from utils import *
from config import *

# Create transcript folder and file
pathlib.Path(transcripts_folder).mkdir(parents=True, exist_ok=True) 
now = datetime.now()
ts_filename = transcripts_folder + "/ts_"+ now.strftime("%Y_%m_%d_%H%M") + ".txt"

# initiallise 
prompt_count=0
messages =list()
system_instruction={"role": "system", "content": instruction}

#initial greeting
print(initial_greeting)
input()
user_prompt=speech_input()

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

        # generate response and write into transcript
        response_message = chat_response(messages)
        response_text = "\nMarvin: " + response_message['content']+'\n'
        print_response(response_text)
        messages.append(response_message)
        with open(ts_filename, 'a') as ts:
            ts.write('\n\n' + response_text)
        prompt_count = (prompt_count + 1) 

        # ask for next prompt
        input()
        user_prompt=speech_input()
        with open(ts_filename, 'a') as ts:
            ts.write('\n\n' + "Me: "+ user_prompt)

# say goodbye and exit
print('\n'+goodbye_msg)
with open(ts_filename, 'a') as ts:
    ts.write('\n\n\n' + goodbye_msg)