from gtts import gTTS
#pip install gTTS

sounds = {"tnt.mp3": "Ich habe T N T gesetzt", "invisible.mp3": "Ich benutze Unsichtbarkeit"}
for f, t in sounds.items():
    gTTS(t, lang='de').save(f)
