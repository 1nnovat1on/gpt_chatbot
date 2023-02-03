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
import voiceTest
from datetime import datetime

warnings.filterwarnings("ignore")

def clear_terminal():
  os.system('cls')

clear_terminal()


global engine
global APIKEY

global memory
global counter
global LongTermMemory

global commands

r = sr.Recognizer()

global windowII
global textForWindowII

AWAKE = True


sentimentScore = []
global overallSentiment_human

# Main running piece of code
def main():
    global overallSentiment_human   
    overallSentiment_human = ''
    
    global memory
    memory = os.path.abspath(os.path.dirname(os.path.abspath(__file__))) + "\\" + "memory.txt"
    
    global counter
    counter = 0

    #store your keys on your machine!
    global APIKEY
    APIKEY = os.getenv('OPEN_API_KEY')

    root = tk.Tk()
    root.geometry('400x500')
    root.resizable(False, False)
    root.title('Prometheus v0.1')
    
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


            response = speak(text)

            voiceTest.speak(response)


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

#Queries Open AI for the current state of Prometheus
def speak(prompt = None):


    global counter
    global memory
    global APIKEY
    global overallSentiment_human

    f = open(memory, 'r')
    
    lines = f.read()
    
    f.close()
    global APIKEY

    APIKEY = os.getenv('OPEN_API_KEY')

    openai.api_key = APIKEY


    if len(lines) > 2000:
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

def dream():

    global memory
    global APIKEY
    
    f = open(memory, 'r')
    
    memories = f.read()
    #print(memories)
    
    f.close()
    global APIKEY

    openai.api_key = APIKEY
    
    new_prompt = "I am the memory module for Prometheus, the God of Knowledge. I am designed to remember names, dialogue, and other information. I need to summarize the following for better storage: \n\n \"{}\" Here's the short version: ".format(memories)

    response = openai.Completion.create(
    engine="text-davinci-003",
    prompt=new_prompt,
    temperature=0.7,
    max_tokens=1000,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,

    )

    dream = response['choices'][0]['text']
    

    f = open(memory,'w')
    now = datetime.now()
    
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

    f.write("Summary of last conversation:\n {}\n Continue from here.".format(dream))
    f.close()

    global counter
    counter = 0

    return

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


def microphone():

    with sr.Microphone() as source:
    # read the audio data from the default microphone
        audio_data = r.record(source, duration=7)
        print("Recognizing...")
        # convert speech to text
        try:
            text = r.recognize_google(audio_data)
        except Exception as e:
            text = "..."
            return text
            
        #print(text)


        return text

def microphone2():
    
    while AWAKE:
        with sr.Microphone() as source:
            #print('listening...')

            audio_data = r.listen(source)
            
            try:
                time.sleep(1)
                text = r.recognize_google(audio_data)
                #print(text)

                return text

            except Exception as e:
                #print("I didn't understand ya: {}".format(e))
                continue


def printII(text = None):
    global windowII
    global textForWindowII
    nowString = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    textForWindowII.insert(1.0, '{} - {}\n'.format(nowString, text))
    windowII.update()

#Queries Open AI for the current state of Prometheus
def queryOpenAITemplate(prompt = None):


    global APIKEY

    APIKEY = os.getenv('OPEN_API_KEY')

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


# Function which returns last word
def lastWord(string):

    if string == None:
        return ''

    #splitting the string
    words = string.split()
    #slicing the list (negative index means index from the end)
    #-1 means the last element of the list
    #print(words[-1])

    output = words[-1]

    return output.replace(".", "")


if __name__ == "__main__":
    main()



