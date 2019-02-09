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

RETINA_SIZE = (1680, 1050)  # Hack.  If I'm exactly this resolution, assume I'm in retina mode.
RETINA_FACTOR = 2

def ocr_screen():
    subprocess.check_call(["screencapture", "-t", "png", "-x", "/tmp/capture.png"])
    hocr = subprocess.check_output(
        ["/usr/local/bin/tesseract", "/tmp/capture.png", "stdout", "hocr"]
    ).decode()  # type: str
    return "\n".join(hocr.splitlines()[1:])


def distance(point1, point2):
    return sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


def move_to_ocr(m):
    # noinspection PyProtectedMember
    start = time.time()
    screen = ui.main_screen()

    factor = 1
    if (int(screen.width), int(screen.height)) == RETINA_SIZE:
        factor = RETINA_FACTOR
    midpoint = (screen.width / 2, screen.height / 2)
    search = join_words(list(map(parse_word, m.dgnwords[0]._words)))
    print(f"Starting teleport to {search}")
    hocr = ocr_screen()
    print("... OCR'd screen: " + hocr)
    tree = ElementTree.XML(hocr)  # type: list[ElementTree.Element]
    # print(list(tree[1]))
    best_pos = None
    best_distance = distance((0, 0), (screen.width, screen.height))
    for span in tree[1].iter():
        # print(span, span.attrib.get("class", ""))
        if span.attrib.get("class", "") == "ocrx_word":
            if search in span.text.lower():
                # title is something like"bbox 72 3366 164 3401; x_wconf 95"
                title = span.attrib["title"]  # type: str
                x, y, side, bottom = [int(i)/factor for i in title.split(";")[0].split()[1:]]
                candidate = (x + side) / 2, (y + bottom) / 2
                dist = distance(candidate, midpoint)
                if dist < best_distance:
                    print(search, span.text, span.attrib["title"])
                    best_pos = candidate
    if best_pos is not None:
        print(f"... Found match, moving to {best_pos}.  {time.time() - start} seconds.")
        ctrl.mouse_move(best_pos[0], best_pos[1])
        return
    print(f"... No match. {time.time() - start} seconds.")


ctx = Context("ocr")

ctx.keymap({"teleport <dgnwords>": [move_to_ocr]})
