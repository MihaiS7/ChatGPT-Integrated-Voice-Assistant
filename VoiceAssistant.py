
'''                 -------------------
                    Imports
                    -------------------
'''
import speech_recognition as sr
from gtts import gTTS
import playsound
import os
from openai import OpenAI

from pydub import AudioSegment
from dotenv import load_dotenv
import sys
import threading

'''                 ----------------
                    Voice Assistant Coding Section
                    ----------------
'''          

load_dotenv()

# OpenAI - ChatGpt3 API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# You should set your OPENAI API key in your env

class New_Siri:
    def __init__(self):
        self.r = sr.Recognizer()
        self.m = sr.Microphone.list_microphone_names().index('MacBook Pro Microphone') # You can use a specific microphone, or just delete the line and
                                                                                       # and left only the sr.Microphone()
        self.keyWord = "stop"
        self.is_running = True
        self.text = ""
        self.background_text = ""
        self.keyword_detected = False
        self.r.energy_threshold = 1000


    def main_microphone(self):
        with sr.Microphone(device_index=self.m) as source: # If you don't want a specific microphone, use self.m
            print("Say something..\n")
            self.r.adjust_for_ambient_noise(source)
            audio = self.r.listen(source)
            try:
                print("Recognizing...\n")
                self.text = self.r.recognize_google(audio) # Using google default API recognition
                print(f"You said: {self.text}\n")
                return self.text
            except sr.UnknownValueError:
                print("Sorry I couldn't understand what you said. Can you repeat?\n")
                self.siri_talk("Sorry I couldn't understand what you said. Can you repeat?")
                pass


    def callback(self, recognizer, audio):
        try:
            self.background_text = recognizer.recognize_google(audio) # Using same google recognition for background
            print(f"Background listener heard: {self.background_text}\n")
            if self.keyWord.lower() in self.background_text.lower():
                print("Keyword detected in the speech.\n")
                self.keyword_detected = True
                return
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

    def background_listener(self):
        print("Background listener is on...\n")
        stop_listening = self.r.listen_in_background(sr.Microphone(device_index=self.m), self.callback)
        return stop_listening
        
        
    # convert text to speech
    def siri_talk(self, text):
        # create audio data
        file_name = "audio_data.mp3"

        #convert text to speech
        tts = gTTS(text, lang="en", tld='us')

        # save the file
        tts.save(file_name)
        
        # Set the playback speed at (1.5)
        audio = AudioSegment.from_file(file_name)
        fast_audio = audio.speedup(playback_speed=1.3) # Changing the speed of speech as you would like
        fast_audio.export("output.mp3", format='mp3')

        # play file
        playsound.playsound("output.mp3")
        # remove files
        try:
            os.remove(file_name)
            os.remove("output.mp3")
        except OSError:
            pass

    
    def siri_reply(self, text):
        conversation = [
            {"role": "user", "content": text}
        ]

        response = client.chat.completions.create(model="gpt-3.5-turbo",
        messages=conversation)

        siri_response = response.choices[0].message.content
        print(f"The response for your message is: {siri_response}\n")
        return siri_response


    '''             ----------------
                    OPENAI API Usage
                    ----------------
    '''

    def openai_api_usage(self):
        request = OpenAI.api_requestor.APIRequestor()
        response = request.request("GET", "/usage?date=2023-08-01")[0];
        price = response.data.current_usage_usd
        print(f"This is the currently cost for OpenAi API: {price}")


    '''                 ----------------
                        Voice Assistant Execution Section
                        ------------- 
    '''


main_listener = New_Siri()
background_microphone = New_Siri()

main_listener.siri_talk("Can you please tell me your name?")
t1 = threading.Thread(target=main_listener.main_microphone(), args=[]) # Using first thread for the main microphone

if t1 is not None:
    main_listener.siri_talk(f"Hi {t1} what can I do for you?")
else:
    sys.exit()

# t2 = threading.Thread(target=                                               # Using the second microphone to work in                                                       
#                       background_microphone.background_listener(), args=[]) # parallel with the main one

while True:
    user_text = main_listener.main_microphone()
    siri_response = main_listener.siri_reply(main_listener.text)
    
    if user_text is not None:
        main_listener.siri_talk(siri_response)
        playsound.playsound("receive_sound.wav")

    main_listener.openai_api_usage()

    if background_microphone.keyword_detected:
        break


