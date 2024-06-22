from DTClientAutotest import pc, global_var
import os
import requests
import json
import re
import pyautogui
from pynput import mouse, keyboard
import time
import subprocess
import shutil

if __name__ == '__main__':
    global_var.root_path = os.path.dirname(__file__) + '/pc'
    print(f"{pc.get_screenshot_resolution()}")
    print(f"[{pc.get_uuid()}]")
    # time.sleep(5)
    # pc.screenshot()
    # res = pc.exist_text('此电脑', pic_full_path=r'C:\Users\admin\Desktop\client_autotest\pc\screenshot\1.png', preview=True)
    # print(res)