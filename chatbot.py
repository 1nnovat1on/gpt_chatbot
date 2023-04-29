# 4-14-2023

import warnings
import os
import openai
import pyttsx3
import speech_recognition as sr 
import os 
import tkinter as tk
from tkinter.ttk import Label
from datetime import datetime
from tkinter import *
import time
from datetime import datetime
import pinecone
import json

warnings.filterwarnings("ignore")

def clear_terminal():
  os.system('cls')

clear_terminal()

USER_ID = 1

global engine
global APIKEY

global memory
global counter

r = sr.Recognizer()

global windowII
global textForWindowII

AWAKE = True

# Pinecone setup
ENVIRONMENT = 'us-east1-gcp'
pinecone.init(api_key=os.getenv('PINECONEKEY'), environment=ENVIRONMENT)
INDEX_NAME = 'imalive'

NUMBER_OF_RELEVANT_THINGS_TO_RETURN_FROM_PINECONE = 5

# OpenAI Setup
embed_model = "text-embedding-ada-002"

# Main running piece of code
def main():

   
    global memory
    memory = os.path.abspath(os.path.dirname(os.path.abspath(__file__))) + "\\" + "memory.txt"
    
    pinecone.init(api_key=os.getenv('PINECONEKEY'), environment='us-east1-gcp')

    global longTermMemory
    longTermMemory = pinecone.Index(INDEX_NAME)
    
    global counter
    counter = 0

    # Store your keys on your machine!
    global APIKEY
    APIKEY = os.getenv('OPENAI_API_KEY')

    # Tkinter Setup

    root = tk.Tk()
    root.geometry('400x500')
    root.resizable(False, False)
    root.title('Prometheus v2.0')
    
    label = Label(root, text='Click Button or Press Spacebar to Wake')
    label.pack(ipadx=10, ipady=10)
    lab = Label(root, text="")
    inputLabel = Label(root, text = "You: ", wraplength = 300)
    outputLabel = Label(root, text = "Response: ", wraplength = 300)


    # Fenster 2

    # Definition und Festlegung neues Fenster

    toplevel = Toplevel()
    toplevel.title('result')
    toplevel.geometry('400x500')

    # Create widgets in the new window

    label = tk.Label(toplevel, text="Subconscious", fg='blue')
    
    w = Text(toplevel, height=10, borderwidth=2)
    w.insert(1.0, "Waiting to wake... ")
    
    w.configure(inactiveselectbackground=w.cget("selectbackground"))

    label.pack()
    w.pack()


    root.focus_set()

    global windowII
    windowII = toplevel
    global textForWindowII
    textForWindowII = w


    def mic():

        while AWAKE:
            lab.config(text='Listening...')
            printII('Listening...')
            root.update()

            #input
            text = microphone2()

            if text is None:
                #printII('I thought I heard something but it was nothing.')
                continue

            elif text == '' or text == '...' or text == ' ':
                #printII('I thought I heard something but it was nothing.')
                continue
            


            inputLabel.config(text = "You: \n\n{}".format(text))
            
            lab.config(text='Responding...')
            printII('responding')
            root.update()


            #response = speak(text)
            response = queryOpenAITemplate3(text)
            
            # ----- ElevenLabs
            #voiceTest.speak(response)

            # ----- Windows TTS
            talk(response)


            uploadToMemory(text, response)


            outputLabel.config(text = "Response: {}".format(response))
            root.update()


            lab.config(text='...')
            root.update()


    button = tk.Button(root, text="Click Me", command=mic)
    button.pack(ipadx=10, ipady=10)

    def createNew():
        global counter
        global memory
        
        counter = 0
        f = open(memory, 'w')
    
        f.write("")
        f.close()


    def Sleep():
        dream()
        clear_terminal()

    sleep_button = tk.Button(root, text="Sleep", command=Sleep)
    sleep_button.pack(ipadx=10, ipady=10)

    button2 = tk.Button(root, text="Restart Prometheus", command=createNew)
    button2.pack(ipadx=10, ipady=10)



    lab.pack(ipadx=10, ipady=10)
    inputLabel.pack(ipadx=10, ipady=10)
    outputLabel.pack(ipadx=10, ipady=10)

    # Binds the spacebar to the microphone method
    root.bind('<space>',lambda event:mic())
    root.mainloop()

# Queries OpenAI
def queryOpenAITemplate3(prompt):

    global counter
    global memory
    global APIKEY
    global overallSentiment_human

    

    f = open(memory, 'r')
    
    lines = f.read()
    
    f.close()

    if len(lines) > 10000:
        dream()
        lines = ""
    
    # Step 1: Retrieve relevant contexts for the prompt
    contexts = retrieve_relevant_metadata(prompt)

    contexts_as_strings = [json.dumps({**x, "metadata": json.dumps(x["metadata"], indent=2)}) for x in contexts]


    # build our prompt with the retrieved contexts included
    prompt_start = (
        "This info from your longterm memory might be relevant to the convo.\n\n"
    )

    prompt_end = (
        lines + "\n\n Human:\n\n{}\n\nme:".format(prompt)
    )
    
    new_prompt = (
        prompt_start +
        "\\n\\n---\\n\\n".join(contexts_as_strings) +
        prompt_end
    )

    APIKEY = os.getenv('OPENAI_API_KEY')

    openai.api_key = APIKEY

    messages = [
        {"role": "system", "content": "This is a conversation between Prometheus, a genius scientist and inventor. Speak from his POV. Do not ever break character. You have a long term memory which feeds you info when relevant."},
        {"role": "user", "content": new_prompt}
    ]

    printII("I think")

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    
    AI_response = response.choices[0].message['content'].strip()

    if "Human: " in AI_response:
        AI_response = AI_response.split("Human:")[0]

    # removes everything after the last occuring period    
    def remove_post_period(string):
        if string[-1] == ".":
            return string
        else:
            index = string.rfind(".")
            return string[:index+1]
    
    AI_response = remove_post_period(AI_response)

    print("{}\n".format(AI_response))
    printII('I speak')


    new_prompt = lines + "\n\nHuman:{}\n\nMe:{}".format(prompt, AI_response)

    f = open(memory,'w')
    f.write(new_prompt)
    f.close()
    
    
    return str(AI_response)

# Queries Pinecone
def retrieve_relevant_metadata(query):

    
    global APIKEY
    openai.api_key = APIKEY

    global longTermMemory

    res = openai.Embedding.create(
        input=[query],
        engine=embed_model
    )

    # retrieve from Pinecone
    xq = res['data'][0]['embedding']
    
    # get relevant contexts
    res = longTermMemory.query(xq, top_k=NUMBER_OF_RELEVANT_THINGS_TO_RETURN_FROM_PINECONE, include_metadata=True)


    score_threshold = 0  # Set your desired threshold here

    filtered_results = [
        {"id": x.id, "score": x.score, "metadata": x.metadata}
        for x in res['matches']
        if x.get('score', 0) > score_threshold
]

    
# returns a list    
    return filtered_results

# Condenses the short term memory into a summary
def dream():

    global memory
    global APIKEY
    
    f = open(memory, 'r')
    
    memories = f.read()
    #print(memories)
    
    f.close()
    global APIKEY

    openai.api_key = APIKEY
    
    new_prompt = "I am a summarizer for a chatbot named Prometheus. I am designed to remember names, dialogue, and other important information. I need to summarize text for better storage and return ONLY the summary:"

    # Step 2: Generate the initial Python script using the refined prompt
    messages = [
        {"role": "system", "content": new_prompt},
        {"role": "user", "content": memories}
    ]

    printII("I dream")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
    )
    
    dream = response.choices[0].message['content'].strip()
    
    f = open(memory,'w')
    now = datetime.now()
    
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

    f.write("Summary of last conversation:\n {}\n Continue from here.".format(dream))
    f.close()

    global counter
    counter = 0

    return

# Speaks with Windows TTS
def talk(text = None):
    
    global counter
    global engine
    
    if counter == 0:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[1].id)
        counter = counter + 1
    
    engine.say(text)
    engine.runAndWait()

# Listens with Google voice recognition
def microphone2():
    
    while AWAKE:
        with sr.Microphone() as source:
            #print('listening...')

            audio_data = r.listen(source)
            
            try:
                time.sleep(1)
                text = r.recognize_google(audio_data)
                #text = openai.Audio.transcribe("whisper-1", audio_data)
                # Extract the text from the transcript
                #text = transcript["choices"][0]["text"]
                return text
                #print(text)

                return text

            except Exception as e:
                #print("I didn't understand ya: {}".format(e))
                continue

# Displays to Tkinter
def printII(text = None):
    global windowII
    global textForWindowII
    nowString = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    textForWindowII.insert(1.0, '{} - {}\n'.format(nowString, text))
    windowII.update()

# Function which returns last word
def lastWord(string):

    if string == None:
        return ''

    #splitting the string
    words = string.split()

    output = words[-1]

    return output.replace(".", "")

# Create an ID for the record in Pinecone
def generate_record_id(USER_ID):
    timestamp = int(time.time())
    record_id = f"{USER_ID}_{timestamp}"
    return record_id

# 'Upsert' to Pinecone
def uploadToMemory(prompt=None, response=None):
    global longTermMemory

    record_id = generate_record_id(USER_ID)

    try:
        # Concatenate file name and content
        masterVector = f"prompt: {prompt}\nresponse: {response}"

        res = openai.Embedding.create(input=[masterVector], engine=embed_model)
        embedding = res['data'][0]['embedding']

        metadata = {"prompt": prompt, "response": response}
        to_upsert = [{"id": record_id, "values": embedding, "metadata": metadata}]
        longTermMemory.upsert(vectors=to_upsert) 

    except Exception as e:
        print("FAILURE: {}".format(e))

#General query
def queryOpenAITemplate(prompt = None):


    global APIKEY

    APIKEY = os.getenv('OPENAI_API_KEY')

    openai.api_key = APIKEY

    response = openai.Completion.create(
    engine="text-davinci-003",
    prompt=prompt,
    temperature=0.7,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    )


    AI_response = response['choices'][0]['text']


    return str(AI_response)

#--OLD:
def queryOpenAITemplate2(prompt = None):


    global APIKEY

    APIKEY = os.getenv('OPENAI_API_KEY')

    openai.api_key = APIKEY

    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    prompt=prompt,
    temperature=0.7,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    )


    AI_response = response['choices'][0]['text']


    return str(AI_response)
#--OLD: Queries Open AI for the current state of Prometheus
def speak(prompt = None):


    global counter
    global memory
    global APIKEY
    global overallSentiment_human

    f = open(memory, 'r')
    
    lines = f.read()
    
    f.close()
    global APIKEY

    APIKEY = os.getenv('OPENAI_API_KEY')

    openai.api_key = APIKEY


    if len(lines) > 7000:
        dream()
        lines = ""

    new_prompt = lines + "\n\n Human: \n\n{}\n\nme: ".format(prompt)

    if counter == 0:
        new_prompt =  lines + "\n\nMy name is Prometheus. I am a genius-level entity dedicated to science and invention. I hear my creator speak to me. I hear: " + "\n\n \n\n{}\n\n My reply to this is: ".format(prompt)

    response = openai.Completion.create(
    engine="text-davinci-003",
    prompt=new_prompt,
    temperature=0.7,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    )


    AI_response = response['choices'][0]['text']

    if "Human: " in AI_response:
        AI_response = AI_response.split("Human:")[0]

    # removes everything after the last occuring period    
    def remove_post_period(string):
        if string[-1] == ".":
            return string
        else:
            index = string.rfind(".")
            return string[:index+1]
    
    AI_response = remove_post_period(AI_response)

    print(AI_response)
    printII('I speak')


    new_prompt = new_prompt + AI_response

    f = open(memory,'w')
    f.write(new_prompt)
    f.close()
    
    
    return str(AI_response)


if __name__ == "__main__":
    main()


