# Программа для голосового ввода

## 1. Установка Vosk и зависимостей
bash

### Установка Python и pip

```
sudo dnf update -y
sudo dnf install python3 python3-pip python3-devel portaudio-devel
```

### Установка PyAudio (для работы с микрофоном)

```
pip3 install pyaudio --user
```

Если pyaudio не устанавливается через pip, попробуйте:
bash

```
sudo dnf install python3-PyAudio
```

### Установка Vosk и других библиотек

```
pip3 install vosk pyperclip keyboard
```

## 2. Скачивание языковой модели Vosk

Vosk требует языковую модель. Для русского:

```bash
wget https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip
unzip vosk-model-small-ru-0.22.zip
mv vosk-model-small-ru-0.22 model_ru
```

(Есть и другие модели, в т.ч. английские.)

