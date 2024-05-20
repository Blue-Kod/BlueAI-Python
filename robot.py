
import socket
import threading

import cv2
import numpy as np
import speech_recognition as sr
from speakerpy.lib_speak import Speaker


def short():
    # создаем сокет объект
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # получаем имя хоста сервера
    host = socket.gethostname()
    port = 10000

    # связываем сокет с хостом и портом
    server_socket.bind((host, port))

    # слушаем подключения
    server_socket.listen(1)

    def handle_client(client_socket):
        cap = cv2.VideoCapture(0)
        cap.read()
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            commands = data.decode()
            for command in commands.split("/"):
                print(">", command)
                command = command.replace("/", "")
                if command == "get_camera":
                    ret, frame = cap.read()
                    encoded, buffer = cv2.imencode(".jpg", frame)
                    data = np.array(buffer).tostring()
                    client_socket.send(data)
                elif command.startswith("motor"):
                    print(command.replace("motor ", ""))

    while True:
        client_socket, addr = server_socket.accept()
        print("Получено соединение(S) от", addr)
        handle_client(client_socket)
        client_socket.close()


def long():
    # создаем сокет объект
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # получаем имя хоста сервера
    host = socket.gethostname()
    port = 10001

    # связываем сокет с хостом и портом
    server_socket.bind((host, port))

    # слушаем подключения
    server_socket.listen(1)

    def handle_client(client_socket):
        r = sr.Recognizer()
        tts = None
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            commands = data.decode()
            for command in commands.split("/"):
                print(">", command)
                command = command.replace("/", "")
                if command == "stt":

                    with sr.Microphone(device_index=None) as source:
                        audio = r.listen(source)
                    try:
                        text = r.recognize_google(audio, language="ru-RU")
                        client_socket.send(text.encode())
                    except:
                        client_socket.send("".encode())
                elif command.startswith("voice"):
                    tts = Speaker(model_id="ru_v3", language="ru", speaker=command.replace("voice ", "").lower(), device="cpu")
                    client_socket.send("OK".encode())
                elif command.startswith("say"):
                    tts.speak(command.replace("say ", ""), sample_rate=24000, speed=1)
                    client_socket.send("OK".encode())
    while True:
        client_socket, addr = server_socket.accept()
        print("Получено соединение(L) от", addr)
        handle_client(client_socket)
        client_socket.close()

threading.Thread(target=short).start()
threading.Thread(target=long).start()