import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ElementTree
from math import sqrt

from talon import ctrl, ui
from talon.voice import Context
from ..utils import parse_word, join_words

# UPSCALE = 1

RETINA_SIZE = (
    1680,
    1050,
)  # Hack.  If I'm exactly this resolution, assume I'm in retina mode.
RETINA_FACTOR = 2
SCALE = 1


def ocr_screen(x, y, w, h, factor):
    subprocess.check_call(
        ["screencapture", "-t", "png", "-x", f"-R{x},{y},{w},{h}", "/tmp/capture.png"]
    )
    subprocess.check_call(
        [
            "/usr/local/bin/convert",
            "/tmp/capture.png",
            "-colorspace",
            "Gray",
            "-sharpen",
            "0x1",
            "-sample",
            f"{w*SCALE*factor}x{h*SCALE*factor}",
            "-contrast-stretch",
            "0",
            "/tmp/capture2.png",
        ]
    )
    hocr = subprocess.check_output(
        [
            "/usr/local/bin/tesseract",
            "-l",
            "eng",
            "--dpi",
            "72",
            "--psm",
            "4",
            "/tmp/capture2.png",
            "stdout",
            "hocr",
        ]
    ).decode()  # type: str
    return "\n".join(hocr.splitlines()[1:])


def distance(point1, point2):
    return sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def move_to_ocr(m):
    old_pos = ctrl.mouse_pos()
    start = time.time()
    screen = ui.main_screen()
    factor = 1
    if (int(screen.width), int(screen.height)) == RETINA_SIZE:
        factor = RETINA_FACTOR
    midpoint = None
    bounds = [0, 0, screen.width, screen.height]
    which = int(parse_word(m._words[1]))
    row = int(which - 1) // 3
    col = int(which - 1) % 3
    bounds = [
        int(col * screen.width // 3),
        int(row * screen.height // 3),
        screen.width // 3,
        screen.height // 3,
    ]
    midpoint = (bounds[0] + bounds[2] // 2, bounds[1] + bounds[3] // 2)
    print(which, row, col, bounds, midpoint)
    # noinspection PyProtectedMember
    search = join_words(list(map(parse_word, m.dgnwords[0]._words))).lower().strip()
    ctrl.mouse_move(*midpoint)
    print(f"Starting teleport {which} to {search}")
    hocr = ocr_screen(*bounds, factor=factor)
    print(f"... OCR'd screen: {time.time() - start} seconds.")
    tree = ElementTree.XML(hocr)  # type: list[ElementTree.Element]
    # print(list(tree[1]))
    best_pos = None
    best_distance = screen.width + screen.height
    for span in tree[1].iter():
        # print(span, span.attrib.get("class", ""))
        if span.attrib.get("class", "") == "ocrx_word":
            if search in span.text.lower():
                # title is something like"bbox 72 3366 164 3401; x_wconf 95"
                title = span.attrib["title"]  # type: str
                x, y, side, bottom = [
                    int(i) / (SCALE * factor) for i in title.split(";")[0].split()[1:]
                ]
                candidate = bounds[0] + (x + side) / 2, bounds[1] + (y + bottom) / 2
                dist = distance(candidate, midpoint)
                if dist < best_distance:
                    # print(search, span.text, span.attrib["title"])
                    best_pos = candidate
    if best_pos is not None:
        print(f"... Found match, moving to {best_pos}.  {time.time() - start} seconds.")
        ctrl.mouse_move(best_pos[0], best_pos[1])
        return
    print(f"... No match. {time.time() - start} seconds.")
    ctrl.mouse_move(*old_pos)


ctx = Context("ocr")

ctx.keymap({"teleport (1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9) <dgnwords>++": [move_to_ocr]})
