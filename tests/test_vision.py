from PIL import Image, ImageDraw

from src.vision import find_green_button

GREEN = (76, 175, 80)


def screen(width=2560, height=1440, button=None, background=(25, 30, 40)):
    image = Image.new("RGB", (width, height), background)
    if button:
        ImageDraw.Draw(image).rectangle(button, fill=GREEN)
    return image


def test_finds_button_in_the_middle():
    x, y = find_green_button(screen(button=(1130, 560, 1430, 640)))
    assert abs(x - 1280) < 15
    assert abs(y - 600) < 15


def test_works_on_second_monitor_size():
    x, y = find_green_button(screen(1920, 1080, button=(850, 420, 1070, 480)))
    assert abs(x - 960) < 15
    assert abs(y - 450) < 15


def test_white_text_on_button_does_not_break_it():
    image = screen(button=(1130, 560, 1430, 640))
    draw = ImageDraw.Draw(image)
    for left in range(1150, 1400, 40):
        draw.rectangle((left, 585, left + 20, 615), fill=(255, 255, 255))
    assert find_green_button(image) is not None


def test_no_button():
    assert find_green_button(screen()) is None


def test_play_button_in_the_corner_is_ignored():
    assert find_green_button(screen(button=(2200, 1300, 2500, 1400))) is None


def test_small_green_spot_is_not_a_button():
    assert find_green_button(screen(button=(1270, 590, 1290, 600))) is None


def test_green_picture_is_not_a_button():
    # Большое зелёное пятно почти квадратной формы — фон или персонаж, а не кнопка
    assert find_green_button(screen(button=(1000, 300, 1400, 700))) is None
