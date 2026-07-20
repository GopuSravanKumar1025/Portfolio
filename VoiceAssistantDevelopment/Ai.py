import datetime
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

import psutil
import pyttsx3
import requests
import speech_recognition as sr


# ============================================================
# CONFIGURATION
# ============================================================

VOICE_RATE = 165
VOICE_VOLUME = 100

# Preferred voice order. The first installed match is selected.
PREFERRED_VOICE_KEYWORDS = (
    "heera",
    "zira",
    "aria",
    "hazel",
    "susan",
    "female",
    "english india",
    "english united states",
)

PHRASE_TIME_LIMIT = 10
AMBIENT_NOISE_DURATION = 2.0
HTTP_TIMEOUT = 15

# Leave this as None to use Windows' real default input microphone.
# To force a microphone later, set it to the number shown by
# the "list microphones" command.
MICROPHONE_DEVICE_INDEX = None

# Suggestions are spoken only when they are actually useful.
CPU_WARNING_PERCENT = 90
MEMORY_WARNING_PERCENT = 85
DISK_WARNING_PERCENT = 90
LOW_BATTERY_PERCENT = 15

BASE_DIRECTORY = Path(__file__).resolve().parent
NOTES_FILE = BASE_DIRECTORY / "notes.txt"

recognizer = sr.Recognizer()

engine = None
windows_voice_names = []
selected_voice_name = None
microphone = None
microphone_available = False
microphone_error_reported = False

# Prevents the same unnecessary suggestion from being repeated quickly.
last_suggestion = None
last_suggestion_time = 0.0
SUGGESTION_COOLDOWN_SECONDS = 20


# ============================================================
# TEXT-TO-SPEECH
# ============================================================

def get_windows_voice_names():
    """Return the Windows speech voices installed on this computer."""
    if platform.system() != "Windows":
        return []

    powershell_script = (
        "Add-Type -AssemblyName System.Speech; "
        "$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$speaker.GetInstalledVoices() | ForEach-Object { $_.VoiceInfo.Name }; "
        "$speaker.Dispose()"
    )

    try:
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                powershell_script,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
            check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )

        if result.returncode != 0:
            details = result.stderr.strip() or result.stdout.strip()
            print(f"Could not read Windows voices: {details}")
            return []

        return [
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip()
        ]

    except (OSError, subprocess.TimeoutExpired) as error:
        print(f"Could not read Windows voices: {error}")
        return []


def choose_preferred_voice(voice_names):
    """Choose a more pleasant installed voice instead of voices[0]."""
    if not voice_names:
        return None

    for keyword in PREFERRED_VOICE_KEYWORDS:
        for voice_name in voice_names:
            if keyword in voice_name.lower():
                return voice_name

    return voice_names[0]


def initialize_voice_engine():
    """Initialize Windows SAPI and pyttsx3 fallback speech."""
    global engine
    global windows_voice_names
    global selected_voice_name

    if platform.system() == "Windows":
        windows_voice_names = get_windows_voice_names()
        selected_voice_name = choose_preferred_voice(windows_voice_names)

        if selected_voice_name:
            print(f"Selected voice: {selected_voice_name}")
        else:
            print("No Windows speech voice was detected.")

    try:
        if platform.system() == "Windows":
            engine = pyttsx3.init("sapi5")
        else:
            engine = pyttsx3.init()

        engine.setProperty("rate", VOICE_RATE)
        engine.setProperty("volume", 1.0)

        if selected_voice_name:
            for voice in engine.getProperty("voices"):
                voice_description = f"{voice.name} {voice.id}".lower()

                if selected_voice_name.lower() in voice_description:
                    engine.setProperty("voice", voice.id)
                    break

        print("Voice system initialized successfully.")

    except Exception as error:
        engine = None
        print(f"pyttsx3 fallback initialization failed: {error}")


def speak_with_windows_sapi(message):
    """Speak through the native Windows SpeechSynthesizer."""
    if platform.system() != "Windows":
        return False

    environment = os.environ.copy()
    environment["SYSTEM_MONITOR_SPEECH_TEXT"] = message
    environment["SYSTEM_MONITOR_SPEECH_VOICE"] = selected_voice_name or ""
    environment["SYSTEM_MONITOR_SPEECH_RATE"] = str(
        max(-10, min(10, round((VOICE_RATE - 180) / 15)))
    )
    environment["SYSTEM_MONITOR_SPEECH_VOLUME"] = str(
        max(0, min(100, VOICE_VOLUME))
    )

    powershell_script = "\n".join(
        [
            "Add-Type -AssemblyName System.Speech",
            "$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer",
            "try {",
            "    $speaker.Volume = [int]$env:SYSTEM_MONITOR_SPEECH_VOLUME",
            "    $speaker.Rate = [int]$env:SYSTEM_MONITOR_SPEECH_RATE",
            "    $requestedVoice = $env:SYSTEM_MONITOR_SPEECH_VOICE",
            "    if ($requestedVoice) {",
            "        $availableVoices = @($speaker.GetInstalledVoices() | ForEach-Object { $_.VoiceInfo.Name })",
            "        if ($availableVoices -contains $requestedVoice) {",
            "            $speaker.SelectVoice($requestedVoice)",
            "        }",
            "    }",
            "    $speaker.Speak($env:SYSTEM_MONITOR_SPEECH_TEXT)",
            "}",
            "finally {",
            "    $speaker.Dispose()",
            "}",
        ]
    )

    try:
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-NonInteractive",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                powershell_script,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=environment,
            timeout=120,
            check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )

        if result.returncode == 0:
            return True

        details = result.stderr.strip() or result.stdout.strip()
        print(f"Windows speech error: {details}")
        return False

    except (OSError, subprocess.TimeoutExpired) as error:
        print(f"Windows speech error: {error}")
        return False


def speak_with_pyttsx3(message):
    """Fallback speech for non-Windows systems or SAPI failures."""
    global engine

    if engine is None:
        initialize_voice_engine()

    if engine is None:
        return False

    try:
        engine.stop()
        engine.say(message)
        engine.runAndWait()
        return True

    except Exception as error:
        print(f"pyttsx3 speech error: {error}")
        engine = None
        return False


def speak(text):
    """Always print the response and also speak it aloud."""
    message = str(text).strip()

    if not message:
        return

    print(f"Assistant: {message}")

    spoken = speak_with_windows_sapi(message)

    if not spoken:
        spoken = speak_with_pyttsx3(message)

    if not spoken:
        print("Speech output failed. Check the Windows output device and volume.")

    time.sleep(0.8)


def list_voices():
    """Display the installed voices and announce the selected one."""
    if not windows_voice_names:
        speak("No selectable Windows voices were found.")
        return

    print("\nInstalled voices:")

    for index, voice_name in enumerate(windows_voice_names, start=1):
        marker = " (current)" if voice_name == selected_voice_name else ""
        print(f"  {index}: {voice_name}{marker}")

    print()

    speak(
        f"I found {len(windows_voice_names)} voices. "
        f"The current voice is {selected_voice_name}."
    )


def change_voice():
    """Cycle to the next installed Windows voice."""
    global selected_voice_name

    if not windows_voice_names:
        speak("No additional Windows voices are available.")
        return

    if selected_voice_name not in windows_voice_names:
        selected_voice_name = windows_voice_names[0]
    else:
        current_index = windows_voice_names.index(selected_voice_name)
        next_index = (current_index + 1) % len(windows_voice_names)
        selected_voice_name = windows_voice_names[next_index]

    speak(
        f"Voice changed to {selected_voice_name}. "
        "This is how I will sound now."
    )


def speak_suggestion(message):
    """
    Speak a suggestion only when required and avoid repeating the same
    suggestion within a short period.
    """
    global last_suggestion
    global last_suggestion_time

    current_time = time.time()

    if (
        message == last_suggestion
        and current_time - last_suggestion_time < SUGGESTION_COOLDOWN_SECONDS
    ):
        return

    last_suggestion = message
    last_suggestion_time = current_time

    speak(message)

# ============================================================
# MICROPHONE AND KEYBOARD INPUT
# ============================================================

def check_microphone_support():
    """
    Select Windows' real default input microphone and calibrate it.

    Short commands such as "help" are accepted, and the calibrated
    threshold is kept stable instead of constantly drifting upward.
    """
    global microphone
    global microphone_available

    audio_interface = None

    try:
        import pyaudio

        microphone_names = sr.Microphone.list_microphone_names()

        if not microphone_names:
            microphone = None
            microphone_available = False
            print("No microphone devices were found.")
            return False

        selected_index = MICROPHONE_DEVICE_INDEX
        selected_name = None

        if selected_index is None:
            audio_interface = pyaudio.PyAudio()

            try:
                default_input = audio_interface.get_default_input_device_info()
                selected_index = int(default_input["index"])
                selected_name = str(default_input.get("name", "")).strip()

            except (IOError, OSError, KeyError, TypeError, ValueError):
                selected_index = None

        if selected_index is not None:
            if selected_index < 0 or selected_index >= len(microphone_names):
                raise ValueError(
                    f"Invalid microphone index {selected_index}. "
                    f"Use a value from 0 to {len(microphone_names) - 1}."
                )

            if not selected_name:
                selected_name = microphone_names[selected_index]

        microphone = sr.Microphone(device_index=selected_index)

        recognizer.pause_threshold = 0.7
        recognizer.phrase_threshold = 0.1
        recognizer.non_speaking_duration = 0.35
        recognizer.dynamic_energy_threshold = False

        print("Calibrating the microphone. Please remain quiet for two seconds...")

        with microphone as source:
            recognizer.adjust_for_ambient_noise(
                source,
                duration=AMBIENT_NOISE_DURATION
            )

        recognizer.energy_threshold = max(
            80,
            min(500, recognizer.energy_threshold * 0.65)
        )

        microphone_available = True

        if selected_name:
            print(f"Using microphone: {selected_name}")
        elif selected_index is not None:
            print(f"Using microphone index: {selected_index}")
        else:
            print("Using the system default input microphone.")

        print(
            f"Microphone ready. Sensitivity threshold: "
            f"{recognizer.energy_threshold:.0f}"
        )

        return True

    except (ImportError, AttributeError, OSError, ValueError) as error:
        microphone = None
        microphone_available = False
        print(f"Microphone support unavailable: {error}")
        return False

    finally:
        if audio_interface is not None:
            audio_interface.terminate()

def type_command():
    """Keyboard fallback when microphone input is unavailable."""
    try:
        command = input("Type command: ").strip().lower()

        if command:
            print(f"You typed: {command}")

        return command

    except (EOFError, KeyboardInterrupt):
        print()
        return "exit"


def listen_command():
    """
    Keep listening silently until a clear command is recognized.

    Nothing is printed or spoken for background noise, silence, or unclear
    audio. A response occurs only after a valid phrase is recognized.
    """
    global microphone
    global microphone_available
    global microphone_error_reported

    if not microphone_available or microphone is None:
        if not microphone_error_reported:
            speak(
                "Microphone input is unavailable. "
                "Please type your command."
            )
            microphone_error_reported = True

        return type_command()

    while True:
        try:
            with microphone as source:
                audio = recognizer.listen(
                    source,
                    timeout=None,
                    phrase_time_limit=PHRASE_TIME_LIMIT
                )

            command = recognizer.recognize_google(
                audio,
                language="en-IN"
            ).strip().lower()

            if not command:
                continue

            print(f"You said: {command}")
            return command

        except (sr.UnknownValueError, sr.WaitTimeoutError):
            continue

        except sr.RequestError as error:
            print(f"Speech recognition service error: {error}")

            speak_suggestion(
                "The online speech recognition service is unavailable. "
                "Please type your command."
            )

            return type_command()

        except (AttributeError, OSError) as error:
            microphone_available = False
            print(f"Microphone error: {error}")

            speak_suggestion(
                "The microphone is unavailable now. "
                "Please type your command."
            )

            return type_command()

        except KeyboardInterrupt:
            print()
            return "exit"

        except Exception as error:
            print(f"Temporary microphone error: {error}")
            time.sleep(0.5)
            continue

def list_microphones():
    """Display every available microphone and its device index."""
    try:
        microphone_names = sr.Microphone.list_microphone_names()

        if not microphone_names:
            speak("No microphone devices were detected.")
            return

        print("\nAvailable microphones:")

        for index, microphone_name in enumerate(microphone_names):
            marker = ""

            if MICROPHONE_DEVICE_INDEX == index:
                marker = " (configured)"

            print(f"  {index}: {microphone_name}{marker}")

        print()

        speak(
            f"I found {len(microphone_names)} microphone devices. "
            "Their names and index numbers are displayed on the screen."
        )

    except (AttributeError, OSError) as error:
        speak("I could not list the microphone devices.")
        print(f"Microphone listing error: {error}")

# ============================================================
# SYSTEM MONITORING
# ============================================================

def get_system_drive():
    """Return the current operating system's main disk path."""
    if platform.system() == "Windows":
        return os.environ.get("SystemDrive", "C:") + "\\"

    return "/"


def check_system_health():
    """Report system status and give warnings only when needed."""
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage(get_system_drive()).percent
        battery = psutil.sensors_battery()
        process_count = len(psutil.pids())

        if battery is None:
            battery_status = "not available"
        else:
            charging_status = " and charging" if battery.power_plugged else ""
            battery_status = (
                f"{battery.percent:.0f} percent"
                f"{charging_status}"
            )

        status = (
            f"CPU usage is {cpu_usage:.1f} percent. "
            f"Memory usage is {memory_usage:.1f} percent. "
            f"Disk usage is {disk_usage:.1f} percent. "
            f"Battery level is {battery_status}. "
            f"There are currently {process_count} processes running."
        )

        speak(status)

        warnings = []

        if cpu_usage >= CPU_WARNING_PERCENT:
            warnings.append(
                "CPU usage is very high. "
                "Close any application that is using too much processing power."
            )

        if memory_usage >= MEMORY_WARNING_PERCENT:
            warnings.append(
                "Memory usage is high. "
                "Closing unused applications may improve performance."
            )

        if disk_usage >= DISK_WARNING_PERCENT:
            warnings.append(
                "Disk space is running low. "
                "Consider deleting or moving files you no longer need."
            )

        if (
            battery is not None
            and battery.percent <= LOW_BATTERY_PERCENT
            and not battery.power_plugged
        ):
            warnings.append(
                "The battery is low. "
                "Connect the charger when possible."
            )

        # Suggestions are spoken only when a real warning exists.
        for warning in warnings:
            speak_suggestion(warning)

    except (OSError, psutil.Error) as error:
        speak("I could not read all system health information.")
        print(f"System health error: {error}")


def report_cpu_usage():
    """Report current CPU usage."""
    try:
        cpu_usage = psutil.cpu_percent(interval=1)

        speak(
            f"Current CPU usage is "
            f"{cpu_usage:.1f} percent."
        )

        if cpu_usage >= CPU_WARNING_PERCENT:
            speak_suggestion(
                "CPU usage is very high. "
                "Closing heavy applications may help."
            )

    except psutil.Error as error:
        speak("I could not read CPU usage.")
        print(f"CPU usage error: {error}")


def report_cpu_speed():
    """Report current CPU frequency."""
    try:
        frequency = psutil.cpu_freq()

        if frequency is None:
            speak("CPU speed information is not available.")
            return

        speed_ghz = frequency.current / 1000

        speak(
            f"The current CPU speed is approximately "
            f"{speed_ghz:.2f} gigahertz."
        )

    except psutil.Error as error:
        speak("I could not read CPU speed.")
        print(f"CPU speed error: {error}")


def report_running_processes():
    """Report process count and a small sample of process names."""
    process_names = []

    for process in psutil.process_iter(["name"]):
        try:
            process_name = process.info.get("name")

            if process_name:
                process_names.append(process_name)

        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            continue

    process_names.sort(key=str.lower)
    sample_processes = ", ".join(process_names[:8])

    if sample_processes:
        speak(
            f"There are {len(process_names)} processes running. "
            f"Some of them are {sample_processes}."
        )
    else:
        speak("I could not read the running process names.")


# ============================================================
# BASIC SECURITY LOG CHECK
# ============================================================

def check_windows_failed_logins():
    """Check Windows failed-login Event ID 4625 from the last 24 hours."""
    query = (
        "*[System[(EventID=4625) and "
        "TimeCreated[timediff(@SystemTime) <= 86400000]]]"
    )

    command = [
        "wevtutil",
        "qe",
        "Security",
        f"/q:{query}",
        "/rd:true",
        "/f:xml",
        "/c:1000"
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
            check=False
        )

        if result.returncode != 0:
            details = result.stderr.strip() or result.stdout.strip()

            speak(
                "I could not read the Windows Security log."
            )

            speak_suggestion(
                "Run the terminal as administrator if you need "
                "the failed-login check."
            )

            print(f"Windows Security log error: {details}")
            return

        failed_login_count = result.stdout.count("<Event xmlns=")

        if failed_login_count > 10:
            speak(
                f"I found {failed_login_count} failed login events "
                f"during the last 24 hours."
            )

            speak_suggestion(
                "There are many failed login attempts. "
                "Review the Windows Security log and change passwords "
                "for affected accounts if necessary."
            )

        elif failed_login_count > 0:
            speak(
                f"I found {failed_login_count} failed login events "
                f"during the last 24 hours."
            )

        else:
            speak(
                "No failed Windows login events were found "
                "during the last 24 hours."
            )

    except FileNotFoundError:
        speak("The Windows event log command is unavailable.")

    except subprocess.TimeoutExpired:
        speak("Reading the Windows Security log took too long.")

    except Exception as error:
        speak("An error occurred while checking Windows security events.")
        print(f"Windows security check error: {error}")


def find_linux_auth_log():
    """Locate a common Linux authentication log."""
    possible_paths = [
        Path("/var/log/auth.log"),
        Path("/var/log/secure"),
        Path("/var/log/messages")
    ]

    for path in possible_paths:
        if path.exists() and path.is_file():
            return path

    return None


def check_linux_failed_logins():
    """Check common Linux authentication logs."""
    log_path = find_linux_auth_log()

    if log_path is None:
        speak("An authentication log file was not found.")
        return

    try:
        failed_login_count = 0

        with log_path.open(
            "r",
            encoding="utf-8",
            errors="replace"
        ) as log_file:

            for line in log_file:
                lowercase_line = line.lower()

                if (
                    "failed password" in lowercase_line
                    or "authentication failure" in lowercase_line
                ):
                    failed_login_count += 1

        if failed_login_count > 10:
            speak(
                f"I found {failed_login_count} failed authentication "
                f"entries in {log_path}."
            )

            speak_suggestion(
                "There are many failed authentication attempts. "
                "Review the authentication log and secure the affected account."
            )

        elif failed_login_count > 0:
            speak(
                f"I found {failed_login_count} failed authentication "
                f"entries in {log_path}."
            )

        else:
            speak("No failed authentication entries were found.")

    except PermissionError:
        speak("Permission was denied while reading the authentication log.")

    except OSError as error:
        speak("I could not read the authentication log.")
        print(f"Authentication log error: {error}")


def check_attacks():
    """Run the correct security-log check for the operating system."""
    current_operating_system = platform.system()

    if current_operating_system == "Windows":
        check_windows_failed_logins()

    elif current_operating_system in {"Linux", "Darwin"}:
        check_linux_failed_logins()

    else:
        speak(
            f"Security log checking is not supported "
            f"on {current_operating_system}."
        )


# ============================================================
# NOTES
# ============================================================

def open_notebook():
    """Ask for and save a spoken note."""
    speak("What should I write in the note?")

    note = listen_command()

    if not note:
        speak("No note was recorded.")
        return

    if note in {"stop", "exit", "quit", "cancel"}:
        speak("Note cancelled.")
        return

    try:
        timestamp = datetime.datetime.now().strftime(
            "%Y-%m-%d %I:%M:%S %p"
        )

        with NOTES_FILE.open("a", encoding="utf-8") as note_file:
            note_file.write(f"{timestamp}: {note}\n")

        speak(f"Note saved in {NOTES_FILE.name}.")

    except OSError as error:
        speak("I could not save the note.")
        print(f"Note saving error: {error}")


# ============================================================
# WEATHER
# ============================================================

WEATHER_CODES = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "heavy drizzle",
    61: "light rain",
    63: "moderate rain",
    65: "heavy rain",
    71: "light snow",
    73: "moderate snow",
    75: "heavy snow",
    80: "light rain showers",
    81: "moderate rain showers",
    82: "heavy rain showers",
    95: "thunderstorm",
    96: "thunderstorm with light hail",
    99: "thunderstorm with heavy hail"
}


def get_weather_forecast():
    """Ask for a city and report its current weather."""
    speak("Please tell me the city name.")

    city = listen_command()

    if not city:
        speak("I did not receive a city name.")
        return

    if city in {"stop", "exit", "quit", "cancel"}:
        speak("Weather request cancelled.")
        return

    try:
        location_response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json"
            },
            timeout=HTTP_TIMEOUT
        )

        location_response.raise_for_status()

        locations = location_response.json().get("results", [])

        if not locations:
            speak("I could not find that city.")
            speak_suggestion(
                "Try saying the city name together with its state or country."
            )
            return

        location = locations[0]

        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": (
                    "temperature_2m,"
                    "apparent_temperature,"
                    "weather_code,"
                    "wind_speed_10m"
                ),
                "timezone": "auto"
            },
            timeout=HTTP_TIMEOUT
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()
        current_weather = weather_data.get("current")

        if not current_weather:
            speak("Current weather information is unavailable.")
            return

        location_name = location.get("name", city)
        country_name = location.get("country")

        if country_name:
            location_name = f"{location_name}, {country_name}"

        weather_code = current_weather.get("weather_code")

        description = WEATHER_CODES.get(
            weather_code,
            "unknown weather conditions"
        )

        temperature = current_weather.get("temperature_2m")
        apparent_temperature = current_weather.get("apparent_temperature")
        wind_speed = current_weather.get("wind_speed_10m")

        speak(
            f"The weather in {location_name} is {description}. "
            f"The temperature is {temperature} degrees Celsius. "
            f"It feels like {apparent_temperature} degrees. "
            f"The wind speed is {wind_speed} kilometers per hour."
        )

    except requests.Timeout:
        speak("The weather request timed out.")

    except requests.RequestException as error:
        speak("I could not connect to the weather service.")
        print(f"Weather request error: {error}")

    except (KeyError, TypeError, ValueError) as error:
        speak("The weather service returned unexpected information.")
        print(f"Weather data error: {error}")


# ============================================================
# HELP AND CONTEXTUAL SUGGESTIONS
# ============================================================

def show_help():
    """Display all commands and speak a compact summary."""
    print(
        """
Available commands:

  CPU usage
  CPU speed
  System status
  Programs running
  Check threats
  Open notebook
  Weather forecast
  List microphones
  List voices
  Change voice
  Time
  Date
  Help
  Stop
  Exit
"""
    )

    speak(
        "You can ask for CPU usage, CPU speed, system status, "
        "running programs, threats, notes, weather, voice settings, time, or date."
    )


def suggest_for_unknown_command(command):
    """
    Give one useful suggestion only when the recognized command
    is unsupported.
    """
    if any(word in command for word in ("ram", "memory", "battery", "disk")):
        speak_suggestion(
            "For memory, battery, and disk information, "
            "say system status."
        )

    elif any(word in command for word in ("application", "app", "task")):
        speak_suggestion(
            "To hear about running applications, "
            "say programs running."
        )

    elif any(word in command for word in ("security", "login", "password")):
        speak_suggestion(
            "To check failed login activity, "
            "say check threats."
        )

    elif any(word in command for word in ("forecast", "temperature", "rain")):
        speak_suggestion(
            "To check the weather, "
            "say weather forecast."
        )

    elif any(word in command for word in ("note", "remember", "write")):
        speak_suggestion(
            "To save a note, "
            "say open notebook."
        )

    else:
        speak_suggestion(
            "I do not have a command for that yet. "
            "Say help to hear the available commands."
        )


# ============================================================
# COMMAND PROCESSING
# ============================================================

def process_command(command):
    """
    Process one recognized command.

    Returns False when the assistant should stop.
    Returns True when it should continue waiting.
    """
    if command in {"stop", "exit", "quit", "close", "goodbye"}:
        speak("Goodbye. Stay safe.")
        return False

    if (
        "cpu speed" in command
        or "cpu frequency" in command
        or "processor speed" in command
    ):
        report_cpu_speed()

    elif (
        "cpu usage" in command
        or "processor usage" in command
    ):
        report_cpu_usage()

    elif (
        "system status" in command
        or "system health" in command
        or command == "health"
        or "computer status" in command
    ):
        check_system_health()

    elif (
        "programs running" in command
        or "running programs" in command
        or "processes" in command
        or "applications running" in command
    ):
        report_running_processes()

    elif (
        "attack" in command
        or "threat" in command
        or "failed login" in command
        or "security check" in command
    ):
        check_attacks()

    elif (
        "open notebook" in command
        or "take note" in command
        or "save note" in command
        or "write a note" in command
    ):
        open_notebook()

    elif "weather" in command or "forecast" in command:
        get_weather_forecast()

    elif (
        "list microphones" in command
        or "microphone list" in command
        or "show microphones" in command
    ):
        list_microphones()

    elif (
        "list voices" in command
        or "show voices" in command
        or "available voices" in command
    ):
        list_voices()

    elif (
        "change voice" in command
        or "next voice" in command
        or "different voice" in command
    ):
        change_voice()

    elif "time" in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}.")

    elif "date" in command or "day is it" in command:
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today's date is {current_date}.")

    elif "help" in command or "commands" in command:
        show_help()

    else:
        suggest_for_unknown_command(command)

    return True


# ============================================================
# MAIN ASSISTANT
# ============================================================

def run_assistant():
    """Start the voice assistant."""
    initialize_voice_engine()
    check_microphone_support()

    speak(
        "Hello, I am your system monitor assistant. "
        "How can I help you?"
    )

    print("Listening continuously. Speak whenever you are ready.")

    # Do not read every command automatically.
    # Suggestions are provided later only when necessary.

    while True:
        command = listen_command()

        if not command:
            continue

        should_continue = process_command(command)

        if not should_continue:
            break


if __name__ == "__main__":
    try:
        run_assistant()

    except KeyboardInterrupt:
        print()

        speak("Assistant stopped.")

        sys.exit(0)
