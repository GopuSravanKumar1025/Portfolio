import speech_recognition as sr
import pyttsx3
import datetime
import psutil
import random
import requests
import os


engine = pyttsx3.init()
engine.setProperty('rate', 200) 

def speak(text):
    print(f"🗣️ Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎙️ Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        print(f"👂 You said: {command}")
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError:
        speak("Sorry, there was an error with the speech service.")
        return ""

def check_system_health():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    battery = psutil.sensors_battery()
    battery_status = f"{battery.percent}%" if battery else "not available"
    processes = len(psutil.pids())

    status = (
        f"CPU usage is {cpu} percent. "
        f"Memory usage is {memory} percent. "
        f"Disk usage is {disk} percent. "
        f"Battery level is {battery_status}. "
        f"There are currently {processes} processes running."
    )
    speak(status)

def find_auth_log():
    possible_paths = [
        "/var/log/auth.log",
        "/var/log/secure",
        "/var/log/messages"
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    return None

def check_attacks():
    log_file_path = find_auth_log()
    if not log_file_path:
        speak("Authentication log file not found on this system.")
        return

    speak(f"Using log file at {log_file_path} for attack detection.")
    
    with open(log_file_path, 'r') as log_file:
        suspicious_count = 0
        for line in log_file:
            if 'Failed password' in line or 'authentication failure' in line:
                suspicious_count += 1

        if suspicious_count > 10:
            speak(f"Multiple failed authentication attempts detected: {suspicious_count} failures.")
            speak("Initiating countermeasures.")
        else:
            speak("No significant threats detected in the authentication logs.")

def open_notebook():
    speak("What should I make a note for today, sir?")
    note = listen_command()
    if note:
        with open("notes.txt", "a") as f:
            f.write(f"{datetime.datetime.now()}: {note}\n")
        speak("Note saved.")
    else:
        speak("No note was recorded.")

def get_weather_forecast():
    speak("Please tell me the city name.")
    city = listen_command()
    if not city:
        speak("I didn't catch the city name.")
        return
    
    geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    response = requests.get(geocoding_url)
    data = response.json()

    if 'results' in data and len(data['results']) > 0:
        latitude = data['results'][0]['latitude']
        longitude = data['results'][0]['longitude']
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()
        if 'current_weather' in weather_data:
            temperature = weather_data['current_weather']['temperature']
            windspeed = weather_data['current_weather']['windspeed']
            weather_code = weather_data['current_weather']['weathercode']
            speak(f"The current temperature in {city} is {temperature}°C with a wind speed of {windspeed} km/h.")
        else:
            speak("I'm sorry, I couldn't retrieve the weather information.")
    else:
        speak("I'm sorry, I couldn't find the location.")

def run_assistant():
    speak("Hello, I'm your system monitor assistant. How can I help you?")
    while True:
        command = listen_command()

        if "cpu speed" in command or "cpu usage" in command:
            cpu = psutil.cpu_percent(interval=1)
            speak(f"Current CPU usage is {cpu} percent.")

        elif "system status" in command or "health" in command:
            check_system_health()

        elif "programs running" in command or "processes" in command:
            processes = [p.info['name'] for p in psutil.process_iter(['name'])]
            speak(f"There are {len(processes)} processes running. Some of them are: {', '.join(processes[:5])}")

        elif "attack" in command or "threats" in command:
            check_attacks()

        elif "open notebook" in command:
            open_notebook()

        elif "weather forecast" in command:
            get_weather_forecast()

        elif "time" in command:
            time = datetime.datetime.now().strftime('%I:%M %p')
            speak(f"The current time is {time}")

        elif "date" in command:
            date = datetime.datetime.now().strftime('%B %d, %Y')
            speak(f"Today's date is {date}")

        elif "stop" in command or "exit" in command:
            speak("Goodbye! Stay safe!")
            break

        else:
            speak("Sorry, I didn't understand that command. Please try again.")

if __name__ == "__main__":
    run_assistant()
