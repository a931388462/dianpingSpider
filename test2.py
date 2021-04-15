#!/usr/bin/env python
# _*_ UTF-8 _*_

from fontTools.ttLib import TTFont
import matplotlib.pyplot as plt
from PIL import Image
import pytesseract

# 图片转化成string：
captcha = Image.open(r'unif09e.png')
print(captcha)
result = pytesseract.image_to_string(captcha, lang='chi_sim', config='--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789').strip()
print(result)

