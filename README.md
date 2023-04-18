# gpt_chatbot
This chatbot allows you to use your microphone to communicate with GPT-4. --Formerly GPT-3  

It features the Pinecone API to create a longterm memory... it will loop in bits of conversation you've had, best it can.  

Accounts and API keys for OpenAI and Pinecone required. You will also need to create an index in Pinecone.  

It uses Windows TTS to respond, which might require some intial setup in your control panel/settings.  

To start:  


Install Python  
Install git  
Copy this directory to your computer (preferably with git clone https://github.com/1nnovat1on/gpt_chatbot.git)  
Open your terminal (CMD on Windows)  
Set environment variables called OPENAI_API_KEY and PINECONEKEY (use the setx OPENAI_API_KEY urkeygoeshere command)    
Navigate to the directory you downloaded the code to with cd. For me that means cd C:\Documents\gpt_chatbot  
Run pip install -r requirements.txt in your terminal  
Run python chatbot.py  
Click "Click Me"  

Talk away...  






4-4-23  
It also uses ElevenLabs API to respond with a realistic voice.  --Disabled for speed  
