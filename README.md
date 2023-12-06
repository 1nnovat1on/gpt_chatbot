# gpt_chatbot
This chatbot allows you to use your microphone to communicate with GPT-4. --Formerly GPT-3  

It features the Pinecone API to create a longterm memory... it will loop in bits of conversation you've had, best it can.  

Accounts and API keys for OpenAI GPT-4 and Pinecone required. It will automatically create an index once you link your Pinecone API key

It uses the OpenAI text to speech to respond.


![Example Image](/files/new_ui.png)


To start:  


Install Python  
Install git  
Copy this directory to your computer (preferably with git clone https://github.com/1nnovat1on/gpt_chatbot.git)  
Open your terminal (CMD on Windows)  
Either:  
  &emsp;input API keys on start up  
  &emsp;or Set environment variables called OPENAI_API_KEY and PINECONEKEY (use the setx OPENAI_API_KEY urkeygoeshere command)    
Navigate to the directory you downloaded the code to with cd. For me that means cd C:\Documents\gpt_chatbot  
Run pip install -r requirements.txt in your terminal  
Run python chatbot.py  

Talk away...  


How to create a Pinecone index:

By default, your index Pinecone index should be named 'imalive' but you can name it something else if you change the variable in the code.

The index should have these attributes: [metric: cosine; Pod Type:p1x1; Dimensions: 1536]

Also, make note of what environment you use and change the code in the Pinecone section with the correct environment (e.g us-east1-gcp)
