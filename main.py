import playsound
import keyboard
import time
import os

StartJarvis = True
UserTime = time.localtime()

def txt(x):
    fd = os.open('./date/txt/logs.txt', os.O_RDWR | os.O_CREAT | os.O_APPEND) #"a+" \|/ a+ dont working i dk
    if x == "space":
        os.write(fd, " ".encode('utf-8'))
        os.close(fd)
        return 0
    if x == "enter":
        os.write(fd, "\n".encode('utf-8'))
        os.close(fd)
        return 0
    else:
        os.write(fd, f"{x}".encode('utf-8'))
        os.close(fd)
        return 0

def go():
    while(True):
        print(26)
        if keyboard.read_key():
            txt(keyboard.read_key())
        
if StartJarvis:
    playsound.playsound("date/sound/JARVIS_start.wav", block=False) #block=False что бы не останавливал программу
    print("hi, i am Jarvis")
    fd = os.open('./date/txt/logs.txt', os.O_RDWR | os.O_CREAT | os.O_APPEND) #"a+" \|/ a+ dont working i dk)
    os.write(fd, f"\nUser {os.getlogin()}, Год {UserTime[0]}, Месяц {UserTime[1]}, День {UserTime[2]}, Час {UserTime[3]}, Минута {UserTime[4]}\n".encode('utf-8'))
    os.close(fd)
    go()

print("return error")