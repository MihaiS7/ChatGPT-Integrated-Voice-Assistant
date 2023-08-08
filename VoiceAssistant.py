
'''                 -------------------
                    Imports
                    -------------------
'''
import speech_recognition as sr
from gtts import gTTS
import playsound
import os
import openai
from pydub import AudioSegment
from dotenv import load_dotenv
import sys
import threading
'''                 ----------------
                    Voice Assistant Coding Section
                    ----------------
'''          

load_dotenv()

class New_Siri:
    def __init__(self):
        self.r = sr.Recognizer()
        self.m = sr.Microphone.list_microphone_names().index('MacBook Pro Microphone')
        self.keyWord = "stop"
        self.is_running = True
        self.text = ""
        self.background_text = ""
        self.keyword_detected = False
        self.r.energy_threshold = 1000



    # OpenAI - ChatGpt3 API
    openai.api_key = os.getenv("OPENAI_API_KEY")

    def main_microphone(self):
        with sr.Microphone(device_index=self.m) as source:
            print("Say something..\n")
            self.r.adjust_for_ambient_noise(source)
            audio = self.r.listen(source)
            try:
                print("Recognizing...\n")
                self.text = self.r.recognize_google(audio)
                print(f"You said: {self.text}\n")
                return self.text
            except sr.UnknownValueError:
                print("Sorry I couldn't understand what you said. Can you repeat?\n")
                self.alina_talk("Sorry I couldn't understand what you said. Can you repeat?")
                pass


    def callback(self, recognizer, audio):
        try:
            self.background_text = recognizer.recognize_google(audio)
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
    def alina_talk(self, text):
        # create audio data
        file_name = "audio_data.mp3"

        #convert text to speech
        tts = gTTS(text, lang="en", tld='us')

        # save the file
        tts.save(file_name)
        
        # Set the playback speed at (1.5)
        audio = AudioSegment.from_file(file_name)
        fast_audio = audio.speedup(playback_speed=1.3)
        fast_audio.export("output.mp3", format='mp3')

        # play file
        playsound.playsound("output.mp3")
        # remove files
        try:
            os.remove(file_name)
            os.remove("output.mp3")
        except OSError:
            pass

    # create a function which will give a reply based the input speech/text
    def alina_reply(self, text):
        conversation = [
            {"role": "user", "content": text}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation,
        )

        alina_response = response['choices'][0]['message']['content']
        print(f"The response for your message is: {alina_response}\n")
        return alina_response


    '''             ----------------
                    OPENAI API Usage
                    ----------------
    '''

    def openai_api_usage(self):
        request = openai.api_requestor.APIRequestor()
        response = request.request("GET", "/usage?date=2023-08-01")[0];
        price = response.data['current_usage_usd']
        print(f"This is the currently cost for OpenAi API: {price}")


    '''                 ----------------
                        Voice Assistant Execution Section
                        ------------- 
    '''


main_listener = New_Siri()
background_microphone = New_Siri()

main_listener.alina_talk("Can you please tell me your name?")
t1 = threading.Thread(target=main_listener.main_microphone(), args=[])

if t1 is not None:
    main_listener.alina_talk(f"Hi {t1} what can I do for you?")
else:
    sys.exit()

t2 = threading.Thread(target=background_microphone.background_listener(), args=[])
background_microphone.background_listener()

while True:
    user_text = main_listener.main_microphone()
    alina_response = main_listener.alina_reply(main_listener.text)
    
    if user_text is not None:
        main_listener.alina_talk(alina_response)
        playsound.playsound("receive_sound.wav")

    main_listener.openai_api_usage()

    if background_microphone.keyword_detected:
        break

