import os
import sys
import json
import argparse
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



is_listening = False
buffer = []
shift_pressed = False
immediate_insert = True  # Флаг для немедленной вставки
is_running = True

def send_text(text):
    """Вставляет текст через xdotool (работает без root в X11)"""
    try:
        pyperclip.copy(text)
        # Попытка вставки через xdotool (для X11)
        subprocess.run(["xdotool", "key", "ctrl+v"], check=True)
    except:
        # Fallback: просто копируем в буфер (пользователь вставит вручную)
        print(f"Текст скопирован в буфер: '{text}'")
        

def on_press(key):
    global is_listening, shift_pressed, immediate_insert, buffer, is_running
    if key == keyboard.Key.shift:
        shift_pressed = True
    elif key == keyboard.Key.f12 and shift_pressed:
        is_listening = not is_listening
        if is_listening:
            print("Начинаем распознавание...")
        else:
            print("Останавливаем распознавание...")
            time.sleep(0.1)
            print(f"buffer: {buffer}")
            if buffer:
                text = " ".join(buffer)
                print(f"Распознано: {text}")
                pyperclip.copy(text)  # Копируем в буфер только при остановке
                print(f"Текст скопирован в буфер: '{text}'")
                buffer.clear()
    elif key == keyboard.Key.f11 and shift_pressed:
        immediate_insert = not immediate_insert
        print(f"Немедленная вставка: {'включена' if immediate_insert else 'выключена'}")
    elif key == keyboard.Key.esc:  # Добавляем обработку ESC для остановки в auto-start режиме
        if is_listening:
            is_listening = False
            print("Останавливаем распознавание...")
            time.sleep(0.1)
            if buffer:
                text = " ".join(buffer)
                print(f"Распознано: {text}")
                pyperclip.copy(text)
                print(f"Текст скопирован в буфер: '{text}'")
                buffer.clear()
            print("\nВыход из программы...")
            is_running = False
                

def on_release(key):
    global shift_pressed
    if key == keyboard.Key.shift:
        shift_pressed = False

def main():
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(description='Голосовой ввод текста')
    parser.add_argument('--auto-start', action='store_true', help='Автоматически начать распознавание при запуске')
    args = parser.parse_args()

    # Настройка микрофона
    mic = pyaudio.PyAudio()
    stream = mic.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=8192
    )

    # Инициализация модели
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()

    # Автоматический старт если указан флаг
    if args.auto_start:
        global is_listening
        is_listening = True
        print("Автоматически начато распознавание...")
    else:
        print("Для включения/отключения распознавания нажмите  Shift+F12.\nДля выхода из программы нажмите Ctrl+C.")
        print("Для включения/отключения немедленной вставки нажмите  Shift+F11.")



    try:
        while is_running:
            if is_listening:
                data = stream.read(2048)
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "").strip()
                    if text:
                        print(f"Распознано - : {text}")  # Вывод в реальном времени
                        if immediate_insert:
                            #send_text(text + " ")
                            buffer.append(text)
                            print(f"buffer: {buffer}")
                            


    except KeyboardInterrupt:
        print("\nОстановлено пользователем.")
    finally:
        stream.stop_stream()
        stream.close()
        mic.terminate()
        listener.stop()

if __name__ == "__main__":
    main()
