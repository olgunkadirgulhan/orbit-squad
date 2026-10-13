#!/usr/bin/env python3
"""Orbit Squad video motoru: Güneş, gezegenler ve Ay sevimli toplar olarak bir duruma gerçek uzay bilgileriyle tepki verir.

Telif yok: karakterler, dokular, sahneler, müzik ve efektler kodla üretilir; yapı Countryball Chaos motorundan.
Bir video = plan (durum + 4 gök cismi + müzik tohumu). Planı run.py seçer.

  python orbit.py --preview 2,6,12 [--sit moons] [--countries EA,MA,JU,SA]
"""
import glob, math, os, random, subprocess, sys, wave
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, S = 1080, 1920, 30, 2
PH = H
FONT = os.path.join(HERE, 'fonts', 'LuckiestGuy-Regular.ttf')
INTRO, TURN, OUTRO = 1.5, 4.0, 3.6
SR = 44100
DARK = (28, 22, 40)

NAMES = {'SU': 'SUN', 'ME': 'MERCURY', 'VE': 'VENUS', 'EA': 'EARTH', 'MO': 'MOON', 'MA': 'MARS', 'JU': 'JUPITER',
         'SA': 'SATURN', 'UR': 'URANUS', 'NE': 'NEPTUNE', 'PL': 'PLUTO',
         'TI': 'TITAN', 'EU': 'EUROPA', 'IO': 'IO', 'CE': 'CERES'}

PLAN = {}


def configure(plan):
    global PLAN
    PLAN = plan


# ---------------------------------------------------------------- yardımcılar (Bloop Bonkers motorundan)
