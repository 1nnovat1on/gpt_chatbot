import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time
import warnings
import os
import openai
import speech_recognition as sr 
from datetime import datetime
from tkinter import *
import time
from datetime import datetime
import pinecone
import json
import io
from openai import OpenAI
import soundfile as sf
import sounddevice as sd
import queue
import threading
import numpy as np
import simpleaudio as sa


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

# Function to get the API key or prompt the user if it's not set in the environment
def get_api_key(env_var_name, prompt_message):
    api_key = os.getenv(env_var_name)
    if api_key is None:
        api_key = input(prompt_message)
    return api_key


def play_mp3(file_path):
    wave_obj = sa.WaveObject.from_wave_file(file_path)
    play_obj = wave_obj.play()
    play_obj.wait_done()  # Wait until sound has finished playing

# Replace 'path/to/your/edited/file.mp3' with the path to your MP3 file
music_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "files/chatbot intro.wav")
threading.Thread(target=play_mp3, args=(music_file,)).start()



# Get the Pinecone API key
PINECONE_API_KEY = get_api_key('PINECONEKEY', 'Enter your Pinecone API Key: ')

# Pinecone setup
ENVIRONMENT = 'us-east1-gcp'
pinecone.init(api_key=PINECONE_API_KEY, environment=ENVIRONMENT)
INDEX_NAME = 'imalive'

NUMBER_OF_RELEVANT_THINGS_TO_RETURN_FROM_PINECONE = 5
pinecone_list = pinecone.list_indexes()

if 'imalive' not in pinecone_list:
    pinecone.create_index("imalive", dimension=1536, pod_type="p1.x1")



# OpenAI Setup
embed_model = "text-embedding-ada-002"
global client
client = OpenAI()

display = (800,600)

shared_queue2 = queue.Queue()

bot_is_talking = False
bot_is_thinking = False

class Octahedron:
    def __init__(self, height, pulsing=True):
        self.current_edge = 0
        self.radius = math.sqrt(2) * height / 2
        self.vertices = [
            (0, height, 0),
            (self.radius, 0, self.radius),
            (self.radius, 0, -self.radius),
            (-self.radius, 0, -self.radius),
            (-self.radius, 0, self.radius),
            (0, -height, 0)
        ]
        self.edges = [
            (0, 1), (0, 2), (0, 3), (0, 4),
            (5, 1), (5, 2), (5, 3), (5, 4),
            (1, 2), (2, 3), (3, 4), (4, 1)
        ]
        self.pulse_factor = 0
        self.pulsing = pulsing

    def draw(self):
        glBegin(GL_LINES)
        for edge in self.edges:
            for vertex in edge:
                if vertex == 1 or vertex == 0:
                    glColor3f(1.0, 0.0, 0.0)
                else:
                    glColor3f(1.0, 1.0, 1.0)
                glVertex3fv(self.vertices[vertex])
        glEnd()

    def draw_with_delay(self):
        glBegin(GL_LINES)
        for i, edge in enumerate(self.edges):
            if i > self.current_edge:
                break
            for vertex in edge:
                if self.pulsing:
                    sine_value = np.sin(self.pulse_factor)
                    if sine_value > 0:
                        glColor3f(sine_value, 0.0, 0.0)  # Red
                    else:
                        glColor3f(0.0, 0.0, -sine_value)  # Blue
                else:
                    glColor3f(1.0, 0.0, 0.0)  # Constant red
                glVertex3fv(self.vertices[vertex])
        glEnd()

        self.pulse_factor += 0.05  # Update pulse factor

        if self.current_edge < len(self.edges):
            time.sleep(1/3)
            self.current_edge += 1


    def enable_pulsing(self):
        self.pulsing = True

    def disable_pulsing(self):
        self.pulsing = False




def create_text_texture(text, font, text_color=(255, 255, 255), bg_color=(0, 0, 0, 0)):
    # Render the text on a Pygame surface
    text_surface = font.render(text, True, text_color, bg_color)
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    width, height = text_surface.get_size()

    # Generate a texture id
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    return texture_id, width, height

def render_2d_overlay(text_texture_id, text_width, text_height):
    # Switch to 2D orthographic projection
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, display[0], 0, display[1])
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Render 2D content (e.g., a rectangle at the bottom)
    glColor3f(0.5, 0.5, 0.5)  # Gray color
    glBegin(GL_QUADS)
    glVertex2f(0, 0)
    glVertex2f(display[0], 0)
    glVertex2f(display[0], 50)  # 50 pixels high
    glVertex2f(0, 50)
    glEnd()


    # Bind the text texture and render it
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, text_texture_id)
    glColor3f(1, 1, 1)  # White color (or any color you want)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0)  # Bottom-left corner of the texture
    glVertex2f(10, 10)  # Bottom-left vertex
    glTexCoord2f(1, 0)  # Bottom-right corner of the texture
    glVertex2f(10 + text_width, 10)  # Bottom-right vertex
    glTexCoord2f(1, 1)  # Top-right corner of the texture
    glVertex2f(10 + text_width, 10 + text_height)  # Top-right vertex
    glTexCoord2f(0, 1)  # Top-left corner of the texture
    glVertex2f(10, 10 + text_height)  # Top-left vertex
    glEnd()
    glDisable(GL_TEXTURE_2D)


    # Restore the original (3D) projection matrix
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def talk_openai_stream(text = None):
    print("text to speech")

    def play_audio_stream_from_buffer(buffer):
        # Use soundfile to read the audio data from the buffer
        with sf.SoundFile(buffer, 'r') as sound_file:
            data = sound_file.read(dtype='int16')
            sd.play(data, sound_file.samplerate)
            sd.wait()  # Wait until the audio has finished playing
    
    response = client.audio.speech.create(
        model="tts-1",
        voice="fable",
        input=text,
        response_format ="opus"
        )
    
    # Create an in-memory buffer to store the streamed audio data
    buffer = io.BytesIO()
    for chunk in response.iter_bytes(chunk_size=4096):
        buffer.write(chunk)
    buffer.seek(0)


    #response.stream_to_file("output.mp3")
    play_audio_stream_from_buffer(buffer)

# Listens with Google voice recognition
def microphone2():
    
    while AWAKE:
        with sr.Microphone() as source:
            #print('listening...')

            audio_data = r.listen_in_background(source)
            
            try:
                time.sleep(.4)
                text = r.recognize_google(audio_data)

                return text

            except Exception as e:
                #print("I didn't understand ya: {}".format(e))
                continue

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

        res = client.embeddings.create(input=[masterVector], model=embed_model)
        embedding = res.data[0].embedding

        metadata = {"prompt": prompt, "response": response}
        to_upsert = [{"id": record_id, "values": embedding, "metadata": metadata}]
        longTermMemory.upsert(vectors=to_upsert) 

    except Exception as e:
        print("FAILURE: {}".format(e))


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



    openai.api_key = APIKEY

    messages = [
        {"role": "system", "content": "This is a conversation between Prometheus, a genius scientist and inventor, and a human. You are desperate to provide correct answers, improve the world, and make scientific progress. Speak from his POV. Do not ever break character. You have a long term memory which feeds you info when relevant."},
        {"role": "user", "content": new_prompt}
    ]



    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    #print(response)

    # Make them very nice
    
    AI_response = response.choices[0].message.content.strip()


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

    res = client.embeddings.create(
        input=[query],
        model=embed_model
    )

    # Check if 'data' key exists and it has at least one item
    #print(res)

    xq = res.data[0].embedding

    
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

    # Make them very nice
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    
    dream = response.choices[0].message.content.strip()
    
    f = open(memory,'w')
    now = datetime.now()
    
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

    f.write("Summary of last conversation:\n {}\n Continue from here.".format(dream))
    f.close()

    global counter
    counter = 0

    return


def mic():

    while AWAKE:


        #input
        text = microphone2()

        if text is None:
            #printII('I thought I heard something but it was nothing.')
            continue

        elif text == '' or text == '...' or text == ' ':
            #printII('I thought I heard something but it was nothing.')
            continue
        





        #response = speak(text)
        response = queryOpenAITemplate3(text)
        
        # ----- ElevenLabs
        #voiceTest.speak(response)

        # ----- Windows TTS
        #talk(response)

        #talk_openai(response)
        talk_openai_stream(response)


        uploadToMemory(text, response)

def talk_thread(response):

    # print('talking')
    
    try:
        global bot_is_talking
        bot_is_talking = True
        talk_openai_stream(response)
        bot_is_talking = False
        
        

    except Exception as e:
        print(f"Error in talk thread: {e}")
    

# This is the function that will be run in a separate thread
def api_call_thread(text, shared_queue2):
    try:
        global bot_is_thinking
        bot_is_thinking = True
        response = queryOpenAITemplate3(text)
        shared_queue2.put(response)  # Put the response in a shared queue
        
        
        threading.Thread(target=talk_thread, args=(response,)).start()
                
        bot_is_thinking = False


        uploadToMemory(text, response)

    except Exception as e:
        print(f"Error in API call thread: {e}")


def main():
    
    # chat bot

    global memory
    # Define the path for the memory file
    memory_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "memory.txt")

    # Check if the file exists
    if not os.path.exists(memory_file_path):
        # Create the file if it does not exist
        with open(memory_file_path, 'w') as file:
            file.write('')  # Create an empty file

    # Now, 'memory' contains the path to your file, which exists
    memory = memory_file_path
    
    pinecone.init(api_key=os.getenv('PINECONEKEY'), environment='us-east1-gcp')

    global longTermMemory
    longTermMemory = pinecone.Index(INDEX_NAME)
    
    global counter
    counter = 0

    # Store your keys on your machine!
    global APIKEY

    # Get the OpenAI API key
    OPENAI_API_KEY = get_api_key('OPENAI_API_KEY', 'Enter your OpenAI API Key: ')

    APIKEY = OPENAI_API_KEY

    
    # pygame
    pygame.init()
    
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0,0.0, -5)

    

    # Create an Octahedron object
    octahedron = Octahedron(height=1.0)

    # Initialize Pygame font
    pygame.font.init()
    font = pygame.font.SysFont('Courier', 20)

    # Create text texture
    text_ui = "Listening ..."
    text_texture_id, text_width, text_height = create_text_texture(text_ui, font)

    status = 0
    shared_queue = queue.Queue()


    def callback(recognizer, audio):  # this is called from the background thread
        
        
        try:
            global bot_is_talking
            global bot_is_thinking


            if not bot_is_thinking and not bot_is_talking: 
                text = recognizer.recognize_google(audio)
                # print("Google Speech Recognition thinks you said: " + text)
                # Create a queue to share data between the callback function and main loop
                shared_queue.put(text)
                # Here, you'd handle the `text` variable, like sending it to your chatbot
        except sr.UnknownValueError:
            #print("Google Speech Recognition could not understand audio")
            pass
        except sr.RequestError as e:
            #print("Could not request results from Google Speech Recognition service; {0}".format(e))
            pass

        except Exception as e:
            #print(e)
            pass

    # Start the background listening

    #r.adjust_for_ambient_noise(source)  # adjust for ambient noise once, at the beginning
    # r.listen_in_background(source, callback)
    #r.listen(source)
    time.sleep(3)
    
    r.listen_in_background(sr.Microphone(), callback)
    # print('starting mic')


    while True:

        
        #print("Active threads:", threading.enumerate())
        # After starting the background thread
        # for thread in threading.enumerate():
        #     print(thread.name, thread.is_alive())
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glRotatef(1, 0, 1, 0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        octahedron.draw_with_delay()


        # Render 2D overlay with text
        render_2d_overlay(text_texture_id, text_width, text_height)

        #input
        #text = microphone2()
        
        text = None

        # Retrieve the recognized text from the queue, if available
        try:
            # Non-blocking get from queue
            text = shared_queue.get_nowait()  
            #print("Text received in main loop:", text)

            # Start a new thread for the API call
            threading.Thread(target=api_call_thread, args=(text, shared_queue2)).start()
            # Do something with the recognized text
        except queue.Empty:
            # No new text in the queue
            pass
        

        

        if text != '' and text != '...' and text != ' ' and text is not None:

            try:
                response = shared_queue2.get_nowait()

                text_ui = response
                text_texture_id, text_width, text_height = create_text_texture(text_ui, font)

                pulse = True

  

            except queue.Empty:
                pass
        
        global bot_is_talking
        global bot_is_thinking

        if bot_is_thinking is True:
            text_ui = "Thinking ..."
            text_texture_id, text_width, text_height = create_text_texture(text_ui, font)
    
            

        elif bot_is_talking is True:
            text_ui = "Talking ..."
            text_texture_id, text_width, text_height = create_text_texture(text_ui, font)
           
            octahedron.enable_pulsing()

        else:
            text_ui = "Listening ..."
            text_texture_id, text_width, text_height = create_text_texture(text_ui, font)
            octahedron.disable_pulsing()

 
        pygame.display.flip()


        



        pygame.time.wait(10)


main()
