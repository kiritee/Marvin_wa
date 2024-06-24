# Imports
from openai import OpenAI

# Update with your API key
client = OpenAI(api_key="YOUR_API_KEY_HERE")

# Open the CSV file in "read binary" (rb) mode, with the "assistants" purpose
file = client.files.create(
  file=open("TravelPreferences.csv", "rb"),
  purpose='assistants'
)

# Create and configure the assistant
# Add the CSV file from above (using tool type "retrieval")
assistant = client.beta.assistants.create(
    name="Terrific Travels",
    instructions="You are a travel agent who specializes in world travel, on all seven continents.  You'll be provided with data indicating travel background and preferences.  Your job is to suggest itineraries for travel, and give me tips about things like best time to travel, what to pack, etc.",
    model="gpt-4-1106-preview",
    tools=[{"type": "retrieval"}],
    file_ids=[file.id]
)

# Create a thread where the conversation will happen
thread = client.beta.threads.create()

# Create the user message and add it to the thread
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="I'd like help planning a new trip based on criteria for Amber. I'd prefer to visit a country I haven't been to yet. What would you suggest?",
)

# Create the Run, passing in the thread and the assistant
run = client.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id
)

# Periodically retrieve the Run to check status and see if it has completed
# Should print "in_progress" several times before completing
while run.status != "completed":
    keep_retrieving_run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
    print(f"Run status: {keep_retrieving_run.status}")

    if keep_retrieving_run.status == "completed":
        print("\n")
        break

# Retrieve messages added by the Assistant to the thread
all_messages = client.beta.threads.messages.list(
    thread_id=thread.id
)

# Print the messages from the user and the assistant
print("###################################################### \n")
print(f"USER: {message.content[0].text.value}")
print(f"ASSISTANT: {all_messages.data[0].content[0].text.value}") 