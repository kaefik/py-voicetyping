import os
import sys
import json
from vosk import Model, KaldiRecognizer
import pyaudio
import pyperclip
import subprocess
import time
from pynput import keyboard

# Укажите путь к модели Vosk
model_path = "model_ru"
if not os.path.exists(model_path):
    print(f"Ошибка: Модель {model_path} не найдена!")
    print("Скачайте её с https://alphacephei.com/vosk/models и распакуйте в текущую папку.")
    sys.exit(1)

# Инициализация модели
model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

# Настройка микрофона
mic = pyaudio.PyAudio()
stream = mic.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=8192
)

def send_text(text):
    """Вставляет текст через xdotool (работает без root в X11)"""
    try:
        pyperclip.copy(text)
        # Попытка вставки через xdotool (для X11)
        subprocess.run(["xdotool", "key", "ctrl+v"], check=True)
    except:
        # Fallback: просто копируем в буфер (пользователь вставит вручную)
        print(f"Текст скопирован в буфер: '{text}'")
        

print("Говорите! Нажмите Ctrl+C для выхода.")

is_listening = False
buffer = []

def on_press(key):
    global is_listening
    if key == keyboard.Key.space:
        is_listening = not is_listening
        if is_listening:
            print("Начинаем распознавание...")
        else:
            print("Останавливаем распознавание...")
            time.sleep(0.1)
            if buffer:
                text = " ".join(buffer)
                print(f"Распознано: {text}")
                send_text(  text + " ")
                buffer.clear()

def main():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        while True:
            if is_listening:
                data = stream.read(4096)
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        buffer.append(text)
            #else:
            #    time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nОстановлено пользователем.")
    finally:
        stream.stop_stream()
        stream.close()
        mic.terminate()
        listener.stop()

if __name__ == "__main__":
    main()
