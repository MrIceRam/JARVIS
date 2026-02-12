import playsound
import keyboard
import time
import os
import pygetwindow
import pyautogui
import asyncio

import comands

StartJarvis = False

def txt(): #working
    while True:
        if keyboard.read_key():
            fd = os.open('./date/txt/logs.txt', os.O_RDWR | os.O_CREAT | os.O_APPEND) #"a+" \|/ a+ dont working i dk
            if keyboard.read_key() == "space":
                os.write(fd, " ".encode('utf-8'))
                os.close(fd)
                return 0
            if keyboard.read_key() == "enter":
                os.write(fd, "\n".encode('utf-8'))
                os.close(fd)
                return 0
            else:
                os.write(fd, f"{keyboard.read_key()}".encode('utf-8'))
                os.close(fd)
                return 0

def switch_to_window_by_title(window_title): #working переключение окна
    """Переключиться на окно по заголовку"""
    try:
        window = pygetwindow.getWindowsWithTitle(window_title)[0]
        window.activate()
        time.sleep(0.5)  # Даем время для переключения  
        return True
    except (IndexError, Exception) as e:
        print(f"Окно '{window_title}' не найдено: {e}")
        return False

def go():
    while(True):
        UserTime = time.localtime() 
        print(UserTime[4],UserTime[5])
        time.sleep(0.5)
            
if StartJarvis:
    playsound.playsound("date/sound/JARVIS_start.wav", block=False) #block=False что бы не останавливал программу
    print("hi, i am Jarvis")
    fd = os.open('./date/txt/logs.txt', os.O_RDWR | os.O_CREAT | os.O_APPEND) #"a+" \|/ a+ dont working i dk)
    UserTime = time.localtime()
    os.write(fd, f"\nUser {os.getlogin()}, Год {UserTime[0]}, Месяц {UserTime[1]}, День {UserTime[2]}, Час {UserTime[3]}, Минута {UserTime[4]}\n".encode('utf-8'))
    os.close(fd)

print("return error")