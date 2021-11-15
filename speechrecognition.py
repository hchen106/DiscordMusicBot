import speech_recognition as sr

r = sr.Recognizer()
mic = sr.Microphone()

with mic as source:
    print("talk")
    audio = r.listen(source)
    print("Time Over")

    try:
        print("You said: " + r.recognize_google(audio, language="zh"))
    except:
        print("I didn't get that")