# ================= CONFIG =================
SAMPLE_RATE = 16000
DURATION = 5
AUDIO_FILE = "input.wav"

AI_AVAILABLE = True  # auto-disable if quota fails

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

engine = pyttsx3.init()
engine.setProperty("rate", 170)

recognizer = sr.Recognizer()

# ================= SPEAK =================
def speak(text):
    print("KRATOS:", text)
    engine.say(text)
    engine.runAndWait()

# ================= LISTEN =================
def listen():
    try:
        print("Listening...")
        recording = sd.rec(
            int(DURATION * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="int16"
        )
        sd.wait()
        sf.write(AUDIO_FILE, recording, SAMPLE_RATE)

        with sr.AudioFile(AUDIO_FILE) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            print("You:", text)
            return text.lower()

    except Exception as e:
        print("Listening error:", e)
        return ""

# ================= OFFLINE COMMANDS =================
def handle_offline(command):
    # ---- TIME ----
    if "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"The time is {now}"

    # ---- DATE ----
    if "date" in command:
        today = datetime.datetime.now().strftime("%A, %d %B %Y")
        return f"Today is {today}"

    # ---- OPEN APPS ----
    if "open chrome" in command:
        os.system("start chrome")
        return "Opening Chrome"

    if "open notepad" in command:
        os.system("start notepad")
        return "Opening Notepad"

    # ---- TYPE TEXT ----
    if command.startswith("type "):
        text = command.replace("type ", "")
        pyautogui.write(text)
        return "Typed successfully"

    # ---- CREATE FILE ----
    if command.startswith("create file"):
        name = command.replace("create file", "").strip()
        if not name:
            return "Please tell the file name"
        open(name, "w").close()
        return f"File {name} created"

    # ---- SHUTDOWN / RESTART ----
    if "shutdown" in command:
        os.system("shutdown /s /t 5")
        return "Shutting down"

    if "restart" in command:
        os.system("shutdown /r /t 5")
        return "Restarting system"

    # ---- EXIT ----
    if "exit" in command or "stop" in command or "bye" in command:
        speak("Goodbye")
        exit()

    return None

# ================= AI RESPONSE (SAFE) =================
def ask_ai(prompt):
    global AI_AVAILABLE

    if not AI_AVAILABLE:
        return "AI is currently unavailable."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are KRATOS, a helpful AI assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print("AI error:", e)
        AI_AVAILABLE = False
        return "AI is offline. I can still run system commands."

# ================= MAIN LOOP =================
def main():
    speak("KRATOS online. Listening.")

    while True:
        command = listen()
        if not command:
            continue

        offline_reply = handle_offline(command)

        if offline_reply:
            speak(offline_reply)
        else:
            reply = ask_ai(command)
            speak(reply)

# ================= START =================
if __name__ == "__main__":
    main()