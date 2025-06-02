import speech_recognition as sr
from gtts import gTTS
import os
import time
import re
import pygame
from deep_translator import GoogleTranslator

current_language = 'en'

def speak(text):
    global current_language
    try:
        if current_language != 'en':
            text = GoogleTranslator(source='auto', target=current_language).translate(text)
    except:
        pass 

    tts = gTTS(text=text, lang=current_language)
    filename = "voice.mp3"
    tts.save(filename)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        continue

    pygame.mixer.quit()
    os.remove(filename)

def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        print(f"👂 You said: {command}")
        return command.lower()
    except:
        speak("Sorry, I didn't catch that.")
        return ""

def set_language(command):
    global current_language
    if "english" in command:
        current_language = 'en'
        speak("Language set to English.")
    elif "spanish" in command:
        current_language = 'es'
        speak("Idioma cambiado a español.")
    elif "hindi" in command:
        current_language = 'hi'
        speak("भाषा हिंदी में बदल गई है।")
    elif "telugu" in command:
        current_language = 'te'
        speak("భాష తెలుగు లోకి మార్చబడింది.")
    else:
        speak("Language not supported yet.")

def analyze_and_speak(data):
    glucose_match = re.search(r'glucose:\s*(\d+)', data, re.IGNORECASE)
    if glucose_match:
        glucose = int(glucose_match.group(1))
        if glucose < 70:
            speak("Warning: Low blood sugar detected. Please consume fast-acting carbs.")
        elif glucose > 180:
            speak("Warning: High blood sugar detected. Consider insulin adjustment or dietary changes.")
        else:
            speak("Your glucose level is within the normal range. Good job!")

    bp_match = re.search(r'blood pressure:\s*(\d+)/(\d+)', data, re.IGNORECASE)
    if bp_match:
        systolic = int(bp_match.group(1))
        diastolic = int(bp_match.group(2))
        if systolic < 90 or diastolic < 60:
            speak("Warning: Low blood pressure detected. Stay hydrated and rest.")
        elif systolic > 140 or diastolic > 90:
            speak("Warning: High blood pressure detected. Monitor your salt intake and consult your doctor.")
        else:
            speak("Your blood pressure is within the normal range. Keep up the good work.")

def read_medical_file():
    try:
        with open("medical_report.txt", "r") as file:
            data = file.read()
        speak("Reading your medical report.")
        time.sleep(1)
        analyze_and_speak(data)
    except FileNotFoundError:
        speak("Medical report not found.")

def run_jarvis():
    speak("Jarvis is online. How can I help you?")
    while True:
        command = listen_command()

        if "start blood analysis" in command:
            speak("Starting blood analysis.")
            read_medical_file()

        elif "speak in" in command:
            set_language(command)

        elif "stop" in command or "exit" in command:
            speak("Goodbye, sir.")
            break

        else:
            speak("Please repeat the command.")

if __name__ == "__main__":
    run_jarvis()
