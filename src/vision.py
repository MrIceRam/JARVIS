"""Поиск кнопки на скриншоте. Здесь нет ничего про Windows, поэтому легко тестировать."""

from collections import deque

from PIL import Image

# Какую часть окна смотреть (лево, верх, право, низ). Кнопка "Принять" всплывает в середине,
# а внизу справа в CS2 есть своя зелёная кнопка "Играть" — её трогать нельзя.
SEARCH_AREA = (0.25, 0.15, 0.75, 0.75)
SCAN_WIDTH = 240  # скриншот уменьшается до этой ширины, иначе перебор пикселей будет долгим

MIN_WIDTH = 0.12  # ширина кнопки от ширины области поиска
MIN_FILL = 0.4  # сколько прямоугольника кнопки зелёное: остальное занимает белая надпись
MIN_ASPECT, MAX_ASPECT = 1.5, 10  # кнопка вытянута в ширину


def _is_green(red: int, green: int, blue: int) -> bool:
    return green >= 100 and green > red * 1.3 and green > blue * 1.3


def _green_blobs(pixels, width: int, height: int) -> list[list[tuple[int, int]]]:
    """Группы соприкасающихся зелёных пикселей."""
    seen = set()
    blobs = []
    for start_y in range(height):
        for start_x in range(width):
            if (start_x, start_y) in seen or not _is_green(*pixels[start_x, start_y]):
                continue
            seen.add((start_x, start_y))
            queue = deque([(start_x, start_y)])
            blob = []
            while queue:
                x, y = queue.popleft()
                blob.append((x, y))
                for near in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if 0 <= near[0] < width and 0 <= near[1] < height and near not in seen:
                        if _is_green(*pixels[near]):
                            seen.add(near)
                            queue.append(near)
            blobs.append(blob)
    return blobs


def find_green_button(image: Image.Image) -> tuple[int, int] | None:
    """Центр самой крупной зелёной кнопки в координатах image. None, если кнопки нет."""
    left = int(image.width * SEARCH_AREA[0])
    top = int(image.height * SEARCH_AREA[1])
    area = image.convert("RGB").crop(
        (left, top, int(image.width * SEARCH_AREA[2]), int(image.height * SEARCH_AREA[3]))
    )

    scale = area.width / SCAN_WIDTH
    width, height = SCAN_WIDTH, max(1, round(area.height / scale))
    small = area.resize((width, height), Image.Resampling.BILINEAR)

    best, best_size = None, 0
    for blob in _green_blobs(small.load(), width, height):
        xs = [x for x, _ in blob]
        ys = [y for _, y in blob]
        box_width, box_height = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
        is_button = (
            box_width >= width * MIN_WIDTH
            and MIN_ASPECT <= box_width / box_height <= MAX_ASPECT
            and len(blob) / (box_width * box_height) >= MIN_FILL
        )
        if is_button and len(blob) > best_size:
            best, best_size = ((min(xs) + max(xs) + 1) / 2, (min(ys) + max(ys) + 1) / 2), len(blob)

    if best is None:
        return None
    return left + round(best[0] * scale), top + round(best[1] * scale)
