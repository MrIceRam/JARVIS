import playsound
import keyboard
import time
import os
import pygetwindow
import pyautogui

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

def PicDota(arg):
    x = pygetwindow.getActiveWindowTitle()
    switch_to_window_by_title('dota')
    pyautogui.write(arg, interval=0.1)
    pyautogui.press('enter')
    switch_to_window_by_title(x)

def ReadyDota():
    pyautogui.press('enter')

def ReadyCs():
    pyautogui.press('enter')

def Music(arg):
    if arg == 'пауза':
        x = pygetwindow.getActiveWindowTitle()
        switch_to_window_by_title('Яндекс Музыка')
        pyautogui.press('enter')
        switch_to_window_by_title(x)
    if arg == 'громче':
        x = pygetwindow.getActiveWindowTitle()
        switch_to_window_by_title('Яндекс Музыка')
        pyautogui.press('left')
        switch_to_window_by_title(x)
    else:
        print('eblo')

def WriteText(arg):
    pyautogui.write(arg)