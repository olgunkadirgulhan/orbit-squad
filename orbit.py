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
def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def seg(t, a, b): return clamp((t - a) / (b - a))
def sm(u): u = clamp(u); return u * u * (3 - 2 * u)
def lerp(a, b, u): return a + (b - a) * u
def lerpc(c1, c2, u): return tuple(int(round(lerp(a, b, u))) for a, b in zip(c1, c2))
def lp(a, b, u): return (lerp(a[0], b[0], u), lerp(a[1], b[1], u))
def back(u):
    u = clamp(u); c = 1.7; v = u - 1
    return 1 + (c + 1) * v ** 3 + c * v ** 2
def spring(t, amp=1.0, f=9.0, damp=6.0):
    return amp * math.exp(-damp * t) * math.sin(f * t) if t > 0 else 0.0
def rotv(x, y, ang):  # saat yönünde (ekran koordinatı)
    a = math.radians(ang)
    return (x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a))
def L(v): return int(round(v * S))
def box(x0, y0, x1, y1): return [L(x0), L(y0), L(x1), L(y1)]


# ---------------------------------------------------------------- 3B sprite'lar
LIGHT = np.array([-0.45, -0.6, 0.66]); LIGHT /= np.linalg.norm(LIGHT)
HALF = LIGHT + np.array([0, 0, 1.0]); HALF /= np.linalg.norm(HALF)


@lru_cache(64)
def sphere_base(color, spec=0.5):
    n = 640
    y, x = np.mgrid[0:n, 0:n].astype(float)
    x = (x + 0.5) / n * 2 - 1; y = (y + 0.5) / n * 2 - 1
    d = x * x + y * y; z = np.sqrt(np.clip(1 - d, 0, 1))
    lam = np.clip(x * LIGHT[0] + y * LIGHT[1] + z * LIGHT[2], 0, 1)
    shade = 0.40 + 0.68 * lam
    rim = np.clip(1 - z, 0, 1) ** 3 * 0.15
    bounce = np.clip(y, 0, 1) * (1 - z) * 0.22
    sp = np.clip(x * HALF[0] + y * HALF[1] + z * HALF[2], 0, 1) ** 60 * spec
    c = np.array(color, float) / 255
    rgb = c * shade[..., None] + (bounce + rim)[..., None] * np.array([1.0, 0.95, 0.9]) * c + sp[..., None]
    a = np.clip((1 - np.sqrt(d)) * n * 0.5, 0, 1)
    return Image.fromarray(np.dstack([np.clip(rgb, 0, 1) * 255, a * 255]).astype(np.uint8))


def sphere(color, w, h, spec=0.5):
    return sphere_base(tuple(color), spec).resize((max(1, L(w)), max(1, L(h))), Image.BILINEAR)


@lru_cache(None)
def cyl(color, w, h, rad=0, spec=0.35):
    pw, ph = L(w), L(h)
    x = (np.arange(pw) + 0.5) / pw * 2 - 1
    z = np.sqrt(np.clip(1 - x * x, 0, 1))
    lam = np.clip(x * LIGHT[0] + z * LIGHT[2] + 0.25, 0, 1)
    shade = 0.42 + 0.6 * lam
    sp = np.clip(x * HALF[0] + z * HALF[2], 0, 1) ** 30 * spec
    row = np.clip(np.array(color, float) / 255 * shade[:, None] + sp[:, None], 0, 1)
    vy = np.linspace(1.06, 0.9, ph)[:, None, None]
    rgb = np.clip(row[None, :, :] * vy, 0, 1) * 255
    m = Image.new('L', (pw, ph), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=L(rad), fill=255)
    im = Image.fromarray(rgb.astype(np.uint8)).convert('RGBA'); im.putalpha(m)
    return im


@lru_cache(None)
def shadow_base():
    m = Image.new('L', (256, 128), 0); ImageDraw.Draw(m).ellipse([24, 24, 232, 104], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(14))
    im = Image.new('RGBA', (256, 128), (0, 0, 0, 0)); im.putalpha(m.point(lambda a: int(a * 0.4)))
    return im


def put(img, spr, cx, cy):
    img.paste(spr, (int(round(cx * S - spr.width / 2)), int(round(cy * S - spr.height / 2))), spr)
def put_sphere(img, color, cx, cy, w, h, spec=0.5): put(img, sphere(color, w, h, spec), cx, cy)
def put_rot(img, spr, cx, cy, ang):
    put(img, spr.rotate(-ang, resample=Image.BICUBIC, expand=True) if ang else spr, cx, cy)
def put_shadow(img, cx, cy, w, h):
    put(img, shadow_base().resize((max(1, L(w)), max(1, L(h))), Image.BILINEAR), cx, cy)
def fade(spr, k):
    s = spr.copy(); s.putalpha(spr.getchannel('A').point(lambda a: int(a * k))); return s
def scaled(spr, s):
    return spr.resize((max(1, int(spr.width * s)), max(1, int(spr.height * s))), Image.BILINEAR)


def particles(img, seed, t0, tt, n, origin, vx, vy, g, colors, size, life=2.0, emit=0.0):
    """Basit fizik parçacıkları. emit>0 ise parçacıklar emit saniye boyunca sırayla çıkar."""
    rnd = random.Random(seed)
    for k in range(n):
        te = t0 + (emit * k / n if emit else 0)
        c = rnd.choice(colors); ux, uy = rnd.uniform(*vx), rnd.uniform(*vy); s = rnd.uniform(*size)
        age = tt - te
        if 0 <= age < life:
            x = origin[0] + ux * age; y = origin[1] + uy * age + 0.5 * g * age * age
            if -60 < y < PH + 60: put_sphere(img, c, x, y, s, s, 0.6)


# ---------------------------------------------------------------- yazı
@lru_cache(None)
def font(sz): return ImageFont.truetype(FONT, sz)


@lru_cache(None)
def text_spr(txt, sz, fill, stroke=DARK):
    sw = max(2, sz // 9); f = font(sz); bb = f.getbbox(txt, stroke_width=sw)
    im = Image.new('RGBA', (bb[2] - bb[0] + 6, bb[3] - bb[1] + 6), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((3 - bb[0], 3 - bb[1]), txt, font=f, fill=fill, stroke_width=sw, stroke_fill=stroke)
    return im


def put_text_px(img, txt, x, y, sz, fill, scale=1.0, rot=0, max_w=None):
    if scale <= 0.02: return
    spr = text_spr(txt, sz, fill)
    if max_w and spr.width > max_w: scale *= max_w / spr.width
    if scale != 1: spr = scaled(spr, scale)
    if rot: spr = spr.rotate(-rot, resample=Image.BICUBIC, expand=True)
    img.paste(spr, (int(x - spr.width / 2), int(y - spr.height / 2)), spr)


def put_text(img, txt, cx, cy, sz, fill, scale=1.0, rot=0, max_w=None):
    put_text_px(img, txt, L(cx), L(cy), L(sz), fill, scale, rot, L(max_w) if max_w else None)


# ---------------------------------------------------------------- sahne
ROOMS = ('living', 'kitchen', 'bedroom', 'office', 'bathroom', 'garage', 'cafe', 'library', 'gym', 'diner', 'arcade', 'studio', 'greenhouse', 'spaceship', 'hotel')
FLOORS = {'living': (196, 138, 88), 'kitchen': (214, 204, 186), 'bedroom': (176, 120, 150), 'office': (150, 152, 165),
          'bathroom': (225, 228, 238), 'garage': (128, 128, 134), 'cafe': (150, 100, 70),
          'library': (120, 80, 55), 'gym': (70, 72, 80), 'diner': (235, 235, 235),
          'arcade': (60, 42, 80), 'studio': (105, 90, 82), 'greenhouse': (150, 132, 100), 'spaceship': (140, 145, 158), 'hotel': (150, 40, 52)}




# ---------------------------------------------------------------- durumlar
# Kural: her replik GERÇEK bir uzay bilgisi + şaka (kaynak: NASA gezegen bilgi sayfaları). Rakamlar yuvarlak ve doğru;
# kesin olmayan bilgiler "might/maybe" ile söylenir. Siyaset, din, korku/şiddet YOK.
# her gök cismi: (replik, ruh hali)  ruh hali: happy shock cool calm cry angry love sleepy shiver
# sahneler: space nebula sunlit ice party
SITUATIONS = {
    'daylength': dict(title='PLANETS: HOW LONG IS YOUR DAY?', scene='space', name='Day Length', lines={
        'EA': ('24 hours. Totally normal.', 'calm'), 'VE': ('243 Earth days! Longer than my year!', 'shock'),
        'JU': ('About 10 hours. I spin fast!', 'cool'), 'MA': ('24 hours and 37 minutes. Close!', 'happy'),
        'ME': ('Sunrise to sunrise? 176 Earth days.', 'sleepy'), 'SA': ('About ten and a half hours. Wheee!', 'happy'),
        'UR': ('17 hours, lying on my side.', 'calm'), 'NE': ('16 hours. Cold ones.', 'cool'),
        'PL': ('Six Earth days. Still counts!', 'cool'), 'MO': ('My day lasts a whole month!', 'shock')}),
    'hot': dict(title="PLANETS WHEN SOMEONE SAYS IT'S HOT", scene='sunlit', name='Temperature', lines={
        'VE': ('465°C. I could melt lead.', 'angry'), 'ME': ('430°C by day, minus 180 at night!', 'shock'),
        'EA': ('Just right for life.', 'love'), 'MA': ('Minus 60 on average. Brrr.', 'shiver'),
        'NE': ('Minus 200. What is hot?', 'shiver'), 'SU': ('My surface is 5,500°C. Cute.', 'cool'),
        'UR': ('I have the coldest air of all!', 'shiver'), 'JU': ('Cold clouds, very hot core.', 'calm')}),
    'moons': dict(title='PLANETS: HOW MANY MOONS DO YOU HAVE?', scene='space', name='Moons', lines={
        'EA': ('Just one. She is perfect.', 'love'), 'MA': ('Two tiny potato moons.', 'happy'),
        'VE': ('Zero. Just me.', 'calm'), 'ME': ('None. So lonely...', 'cry'),
        'SA': ('Over 270. I win!', 'cool'), 'JU': ('Over 90 moons!', 'happy'),
        'UR': ('28, named after Shakespeare characters!', 'love'), 'NE': ('16. Triton orbits backwards!', 'cool'),
        'PL': ('Five! Charon is huge.', 'happy')}),
    'small': dict(title="PLANETS WHEN SOMEONE SAYS 'YOU'RE SMALL'", scene='nebula', name='Size', lines={
        'JU': ('1,300 Earths fit inside me.', 'cool'), 'SU': ('1.3 million Earths fit in me.', 'cool'),
        'EA': ('Biggest rocky planet, thanks.', 'happy'), 'ME': ('Smallest planet. Fastest, though!', 'angry'),
        'MO': ('I am about a quarter of Earth.', 'calm'), 'PL': ('Smaller than the Moon. Rude.', 'cry'),
        'MA': ('Half of Earth. Fine.', 'calm'), 'SA': ('I could float in a giant bathtub!', 'happy')}),
    'year': dict(title='PLANETS: HOW LONG IS YOUR YEAR?', scene='sunlit', name='Year Length', lines={
        'ME': ('88 days. Birthday every season!', 'happy'), 'EA': ('365 days. Classic.', 'calm'),
        'MA': ('687 days. Long wait for cake.', 'sleepy'), 'JU': ('Almost 12 Earth years.', 'cool'),
        'SA': ('29 Earth years per lap.', 'calm'), 'UR': ('84 years! One birthday per lifetime!', 'shock'),
        'NE': ('165 years. Patience.', 'sleepy'), 'PL': ('248 years. Party in 2178!', 'happy'),
        'VE': ('225 days, and I spin backwards!', 'cool')}),
    'rain': dict(title='PLANETS WHEN IT RAINS', scene='ice', name='Rain', lines={
        'EA': ('Water rain. Boring!', 'calm'), 'VE': ('Sulfuric acid clouds. Ouch.', 'angry'),
        'NE': ('It might rain diamonds here!', 'love'), 'UR': ('Diamonds might fall here too!', 'love'),
        'MA': ('Dust storms, not rain.', 'cool'), 'JU': ('Helium rain, deep inside!', 'shock'),
        'MO': ('No air, no rain.', 'calm'), 'PL': ('My mountains have methane snow!', 'shiver')}),
    'wind': dict(title='PLANETS ON A WINDY DAY', scene='nebula', name='Wind', lines={
        'NE': ('2,000 km/h winds. Fastest!', 'cool'), 'SA': ('1,800 km/h at my equator!', 'shock'),
        'JU': ('My Great Red Spot is a giant storm!', 'happy'), 'EA': ('Hurricanes are my maximum.', 'calm'),
        'MA': ('Dust storms can cover all of me!', 'angry'), 'MO': ('Wind? I have no air.', 'sleepy'),
        'VE': ('My clouds circle me in four days!', 'shock')}),
    'rings': dict(title='PLANETS WHEN SOMEONE TALKS ABOUT RINGS', scene='space', name='Rings', lines={
        'SA': ('Mine are the best. Obviously.', 'cool'), 'JU': ('I have faint rings too!', 'happy'),
        'UR': ('My rings stand up sideways!', 'happy'), 'NE': ('Mine have clumpy arcs!', 'cool'),
        'EA': ('No rings. Just satellites.', 'calm'), 'MA': ('Phobos may become a ring someday!', 'shock'),
        'VE': ('No rings and no moons.', 'cry')}),
    'jump': dict(title='PLANETS WHEN YOU TRY TO JUMP', scene='space', name='Gravity', lines={
        'MO': ('Jump six times higher here!', 'happy'), 'MA': ('Almost three times higher on me!', 'happy'),
        'JU': ('You would weigh 2.4 times more!', 'angry'), 'EA': ('Normal jump. Sorry.', 'calm'),
        'PL': ('Jump 16 times higher here!', 'love'), 'SU': ('28 times your weight. Do not land.', 'shock'),
        'SA': ('Almost like Earth, surprisingly!', 'cool'), 'ME': ('Same gravity as Mars, actually!', 'cool')}),
    'sunlight': dict(title='PLANETS WHEN THE SUN SAYS GOOD MORNING', scene='sunlit', name='Sunlight', lines={
        'SU': ('Good morning, everyone!', 'happy'), 'ME': ('Too close! Too bright!', 'angry'),
        'EA': ('Your light reaches me in 8 minutes.', 'love'), 'MA': ('About 12 minutes for me.', 'calm'),
        'JU': ('43 minutes. Late as usual.', 'sleepy'), 'NE': ('Four hours. I see you dimly.', 'cry'),
        'PL': ('Five and a half hours...', 'sleepy'), 'SA': ('80 minutes of travel time.', 'calm')}),
    'monday': dict(title='PLANETS ON MONDAY MORNING', scene='sunlit', name='Monday', lines={
        'VE': ('My Monday lasts 243 days.', 'cry'), 'EA': ('Ugh. Coffee first.', 'sleepy'),
        'JU': ('Monday is over in 10 hours!', 'happy'), 'MA': ('Extra 37 minutes to snooze.', 'sleepy'),
        'UR': ('I am literally lying on my side.', 'sleepy'), 'ME': ('One sunrise every 176 days. Relax.', 'cool'),
        'SA': ('Ten hour day? Weekend soon!', 'happy')}),
    'tilt': dict(title="PLANETS WHEN TOLD 'STAND UP STRAIGHT'", scene='nebula', name='Tilt', lines={
        'UR': ('I am tilted 98 degrees. No.', 'cool'), 'EA': ('23.5 degrees. It gives me seasons!', 'happy'),
        'VE': ('177 degrees. I am upside down!', 'shock'), 'MA': ('25 degrees. Seasons too!', 'happy'),
        'JU': ('Only 3 degrees. Very upright.', 'cool'), 'ME': ('Almost zero tilt. Perfect posture.', 'cool'),
        'SA': ('27 degrees and fabulous.', 'love')}),
    'water': dict(title='PLANETS WHEN SOMEONE ASKS FOR WATER', scene='ice', name='Water', lines={
        'EA': ('71 percent of me is ocean!', 'happy'), 'MA': ('Ice at my poles!', 'cool'),
        'MO': ('Ice hiding in dark craters!', 'happy'), 'VE': ('Mine all boiled away.', 'cry'),
        'JU': ('My moon Europa hides an ocean!', 'love'), 'SA': ('Enceladus sprays water geysers!', 'shock'),
        'ME': ('Ice in my shadows. Believe it!', 'cool')}),
    'volcano': dict(title='PLANETS WHEN SOMEONE MENTIONS VOLCANOES', scene='sunlit', name='Volcanoes', lines={
        'MA': ('Olympus Mons! 2.5 times Everest!', 'cool'), 'EA': ('Over a thousand active ones!', 'happy'),
        'VE': ('I have the most volcanoes of all!', 'cool'), 'JU': ('My moon Io never stops erupting!', 'shock'),
        'MO': ('My dark spots are old lava seas!', 'calm'), 'NE': ('Triton shoots ice geysers!', 'shiver'),
        'PL': ('Ice volcanoes, maybe!', 'happy')}),
    'race': dict(title='PLANETS IN A RACE AROUND THE SUN', scene='space', name='Orbit Speed', lines={
        'ME': ('47 km per second. Fastest!', 'cool'), 'VE': ('35 km per second. Close second!', 'happy'),
        'EA': ('30 km per second. Not bad.', 'calm'), 'MA': ('24 km per second. Steady.', 'cool'),
        'JU': ('13 km per second. Heavy runner.', 'sleepy'), 'NE': ('5 km per second. Slowest. Fine.', 'sleepy'),
        'SU': ('We all orbit the galaxy at 230 km per second!', 'shock')}),
    'pluto': dict(title="PLANETS WHEN PLUTO SAYS 'I'M A PLANET'", scene='ice', name='Pluto', lines={
        'PL': ('I am still a planet. Emotionally.', 'cry'), 'EA': ('Dwarf planet since 2006, buddy.', 'calm'),
        'NE': ('You even cross my orbit!', 'shock'), 'JU': ('Four of my moons are bigger!', 'cool'),
        'SA': ('My Titan is bigger than you too.', 'cool'), 'MO': ('Even I am bigger. Sorry.', 'calm'),
        'MA': ('Love your heart, though!', 'love')}),
    'outfit': dict(title='PLANETS PICKING THEIR OUTFIT', scene='nebula', name='Colors', lines={
        'MA': ('Red. Rust, actually.', 'cool'), 'NE': ('Deep blue, thanks to methane.', 'love'),
        'UR': ('Pale cyan. Methane again!', 'happy'), 'EA': ('Blue and green. Classic.', 'happy'),
        'JU': ('Stripes. Always stripes.', 'cool'), 'VE': ('Yellow clouds. Mysterious.', 'cool'),
        'SA': ('Butterscotch with rings.', 'love'), 'SU': ('I am actually white, not yellow!', 'shock')}),
    'visitors': dict(title='PLANETS WHEN HUMANS VISIT', scene='space', name='Visitors', lines={
        'MO': ('Twelve humans walked on me!', 'love'), 'MA': ('Only robots so far. Hi, rovers!', 'happy'),
        'VE': ('Landers lasted about two hours.', 'angry'), 'EA': ('Eight billion humans live on me!', 'shock'),
        'JU': ('Galileo dove into me in 2003.', 'calm'), 'SA': ('Cassini dove into me in 2017.', 'cry'),
        'PL': ('New Horizons waved in 2015!', 'happy'), 'NE': ('Only Voyager 2 ever visited.', 'cry'),
        'UR': ('Voyager 2 only, in 1986.', 'sleepy')}),
    'halloween': dict(title='PLANETS ON HALLOWEEN', scene='party', name='Halloween', lines={
        'MA': ('Already dressed in red!', 'cool'), 'VE': ('Hotter than an oven. Scary!', 'angry'),
        'PL': ('Ghost costume. Again.', 'cry'), 'SU': ('My solar storms make auroras!', 'happy'),
        'NE': ('The darkest, coldest party.', 'shiver'), 'EA': ('Candy for everyone!', 'happy'),
        'MO': ('Full moon. Spooky time!', 'love'), 'SA': ('My hexagon storm is spooky!', 'shock')}),
    'distance': dict(title='PLANETS: HOW FAR ARE YOU FROM THE SUN?', scene='sunlit', name='Distance', lines={
        'ME': ('58 million km. Toasty.', 'angry'), 'EA': ('150 million km. Perfect spot.', 'love'),
        'MA': ('228 million km. A bit chilly.', 'shiver'), 'JU': ('778 million km away!', 'cool'),
        'SA': ('1.4 billion km. Far!', 'calm'), 'NE': ('4.5 billion km. So lonely.', 'cry'),
        'VE': ('108 million km. Too hot.', 'angry')}),
}

# 2026-10-13: kullanıcı isteği "tekrar olmasın, replikleri 3 katına çıkar" → 39 yeni durum (toplam 59). Aynı kural: her replik gerçek bilgi.
SITUATIONS.update({
    'age': dict(title='PLANETS: HOW OLD ARE YOU?', scene='nebula', name='Age', lines={
        'SU': ('4.6 billion years. Still shining!', 'cool'), 'EA': ('4.5 billion. I look great, right?', 'happy'),
        'MO': ('Probably born from a giant crash!', 'shock'), 'JU': ('Probably the first planet to form!', 'cool'),
        'MA': ('4.6 billion. Rusty but strong.', 'cool'), 'SA': ('4.5 billion years young.', 'love'),
        'PL': ('Same age as you all. Just smaller.', 'calm')}),
    'scale': dict(title='PLANETS STEPPING ON A SCALE', scene='space', name='Mass', lines={
        'JU': ('Twice all other planets combined!', 'cool'), 'SU': ('99.8 percent of all the mass here!', 'shock'),
        'EA': ('Densest planet. Heavy for my size!', 'happy'), 'SA': ('Lowest density. I could float!', 'love'),
        'ME': ('A giant iron core inside!', 'cool'), 'PL': ('Less than one percent of Earth.', 'cry'),
        'MO': ('About 1.2 percent of Earth.', 'calm')}),
    'closest': dict(title="PLANETS: WHO'S CLOSEST TO EARTH?", scene='sunlit', name='Closest', lines={
        'VE': ('I come the closest to Earth!', 'cool'), 'ME': ('On average, I am closest!', 'happy'),
        'MA': ('I come close every 26 months!', 'happy'), 'MO': ('384,000 km. Closest of all!', 'love'),
        'SU': ('Eight light minutes away.', 'calm'), 'JU': ('Not me. Way out here.', 'sleepy')}),
    'round': dict(title="PLANETS WHEN SOMEONE SAYS 'YOU'RE ROUND'", scene='nebula', name='Shape', lines={
        'SA': ('I am squished! Flattest planet.', 'shock'), 'JU': ('I bulge at the middle too!', 'happy'),
        'EA': ('Slightly wider at the equator.', 'calm'), 'SU': ('Almost a perfect sphere!', 'cool'),
        'MA': ('My moon Phobos looks like a potato!', 'happy'), 'MO': ('Round, with lots of dents.', 'calm')}),
    'shield': dict(title='PLANETS SHOWING THEIR SHIELDS', scene='space', name='Magnetic Field', lines={
        'EA': ('My magnetic field protects life!', 'love'), 'JU': ('Strongest magnetic field of all!', 'cool'),
        'MA': ('I lost my global magnetic field.', 'cry'), 'VE': ('No magnetic field. Wild.', 'shock'),
        'ME': ('Weak field, but I have one!', 'happy'), 'SU': ('My field flips every 11 years!', 'shock'),
        'UR': ('My field is tilted and off-center!', 'sleepy')}),
    'aurora': dict(title='PLANETS WHEN THE LIGHT SHOW STARTS', scene='ice', name='Auroras', lines={
        'EA': ('Northern lights! So pretty.', 'love'), 'JU': ('My auroras are bigger than Earth!', 'cool'),
        'SA': ('Auroras at my poles too!', 'happy'), 'SU': ('My solar wind makes them happen!', 'happy'),
        'MA': ('Patchy auroras, even without a field!', 'shock'), 'UR': ('Mine glow in ultraviolet!', 'cool'),
        'NE': ('Webb spotted my auroras!', 'love')}),
    'cloudy': dict(title="PLANETS WHEN IT'S CLOUDY", scene='nebula', name='Clouds', lines={
        'VE': ('Thick clouds hide my whole surface.', 'cool'), 'JU': ('Ammonia clouds in stripes!', 'happy'),
        'EA': ('Water clouds. Classic.', 'calm'), 'MA': ('Thin clouds of water ice!', 'shiver'),
        'NE': ('Bright methane clouds!', 'cool'), 'SA': ('Hazy yellow clouds!', 'sleepy'),
        'MO': ('No clouds. Ever.', 'calm'), 'PL': ('Blue haze layers!', 'love')}),
    'mountains': dict(title='PLANETS BRAGGING ABOUT MOUNTAINS', scene='sunlit', name='Mountains', lines={
        'EA': ('Everest is 8.8 km tall!', 'happy'), 'MA': ('Olympus Mons is about 22 km!', 'cool'),
        'VE': ('Maxwell Montes, 11 km high!', 'cool'), 'PL': ('Mountains made of water ice!', 'shiver'),
        'MO': ('Mountains from giant impacts.', 'calm'), 'JU': ('No surface, no mountains.', 'sleepy'),
        'SA': ('My moon Iapetus has a giant ridge!', 'shock')}),
    'canyons': dict(title='PLANETS SHOWING OFF THEIR CANYONS', scene='sunlit', name='Canyons', lines={
        'MA': ('Valles Marineris, as long as the USA!', 'cool'), 'EA': ('The Grand Canyon. Pretty deep!', 'happy'),
        'VE': ('Huge rift valleys!', 'cool'), 'ME': ('Giant cliffs called scarps!', 'shock'),
        'MO': ('Long winding channels called rilles!', 'calm')}),
    'changed': dict(title="PLANETS WHEN SOMEONE SAYS 'YOU CHANGED'", scene='space', name='Changes', lines={
        'ME': ('I am shrinking as my core cools!', 'cry'), 'MO': ('I drift 3.8 cm away every year!', 'sleepy'),
        'SU': ('I am slowly getting brighter!', 'cool'), 'EA': ('My days get slightly longer!', 'calm'),
        'MA': ('Phobos is slowly spiraling into me!', 'shock'), 'NE': ('Triton is spiraling inward!', 'shock'),
        'SA': ('My rings may vanish someday!', 'cry')}),
    'trip': dict(title='PLANETS: HOW LONG TO GET THERE?', scene='space', name='Travel Time', lines={
        'MO': ('Three days, by Apollo!', 'happy'), 'MA': ('About seven months by spacecraft!', 'cool'),
        'JU': ('Juno took five years!', 'calm'), 'SA': ('Cassini took almost seven years!', 'calm'),
        'PL': ('New Horizons took nine and a half years!', 'shock'), 'ME': ('MESSENGER took six and a half years!', 'sleepy'),
        'NE': ('Voyager 2 took 12 years!', 'cry')}),
    'bedtime': dict(title='PLANETS AT BEDTIME', scene='space', name='Night', lines={
        'ME': ('My nights last about 88 Earth days!', 'sleepy'), 'MO': ('Two weeks of night. Cozy.', 'sleepy'),
        'UR': ('42 years of night at my poles!', 'shock'), 'EA': ('Eight hours, please.', 'sleepy'),
        'VE': ('My night lasts 58 Earth days.', 'sleepy'), 'JU': ('Five hour nights. Quick nap!', 'happy'),
        'MA': ('Like Earth, plus 37 minutes!', 'calm')}),
    'seasons': dict(title='PLANETS WHEN THE SEASONS CHANGE', scene='ice', name='Seasons', lines={
        'EA': ('Four seasons, every year!', 'happy'), 'MA': ('My seasons are twice as long!', 'cool'),
        'UR': ('Each season lasts 21 years!', 'shock'), 'NE': ('Each season lasts over 40 years!', 'shock'),
        'SA': ('Seven year seasons!', 'calm'), 'JU': ('Barely any seasons. Tiny tilt!', 'cool'),
        'VE': ('Almost no seasons at all.', 'calm')}),
    'snow': dict(title='PLANETS WHEN IT SNOWS', scene='ice', name='Snow', lines={
        'MA': ('Carbon dioxide snow at my poles!', 'shiver'), 'PL': ('Methane snow on my peaks!', 'shiver'),
        'EA': ('Water snow. Build a snowman!', 'happy'), 'VE': ('Metal frost on my mountains!', 'cool'),
        'NE': ('Triton has nitrogen frost!', 'shiver'), 'MO': ('No snow, just dust.', 'calm'),
        'JU': ('Ammonia ice crystals up high!', 'cool')}),
    'smell': dict(title='PLANETS IF YOU COULD SMELL THEM', scene='nebula', name='Smell', lines={
        'MO': ('Astronauts said I smell like gunpowder!', 'shock'), 'UR': ('Rotten eggs! Hydrogen sulfide.', 'cry'),
        'VE': ('Sulfur. Also rotten eggs!', 'angry'), 'EA': ('Fresh rain smell. Petrichor!', 'love'),
        'JU': ('Ammonia, like cleaning products!', 'shock')}),
    'sound': dict(title="PLANETS WHEN ASKED TO 'SAY SOMETHING'", scene='space', name='Sound', lines={
        'SU': ('Space is silent. No air for sound!', 'calm'), 'MA': ('Perseverance recorded my wind!', 'happy'),
        'VE': ('Venera landers recorded my wind!', 'cool'), 'EA': ('Birds, waves and music!', 'love'),
        'MO': ('Total silence up here.', 'sleepy'), 'JU': ('Juno turned my radio waves into sound!', 'cool')}),
    'swim': dict(title='PLANETS WHEN SOMEONE GOES SWIMMING', scene='ice', name='Oceans', lines={
        'EA': ('Five oceans. Dive in!', 'happy'), 'JU': ('Europa may hold twice Earth’s ocean water!', 'shock'),
        'SA': ('Titan has lakes of methane!', 'cool'), 'NE': ('Triton might hide an ocean!', 'cool'),
        'MA': ('I had water long ago!', 'cry'), 'PL': ('Maybe an ocean under my ice!', 'love'),
        'VE': ('Maybe oceans, billions of years ago.', 'cry')}),
    'sky': dict(title='PLANETS IN YOUR NIGHT SKY', scene='space', name='Night Sky', lines={
        'VE': ('Brightest planet in your sky!', 'cool'), 'JU': ('Usually second brightest!', 'happy'),
        'MA': ('The red dot in your sky!', 'cool'), 'SA': ('Visible without a telescope!', 'happy'),
        'UR': ('Barely visible to the eye.', 'sleepy'), 'NE': ('You need a telescope for me.', 'cool'),
        'MO': ('Brightest thing at night!', 'love'), 'ME': ('Hard to spot, so close to the Sun.', 'cry')}),
    'names': dict(title='PLANETS EXPLAINING THEIR NAMES', scene='nebula', name='Names', lines={
        'JU': ('King of the Roman gods!', 'cool'), 'VE': ('Roman goddess of love!', 'love'),
        'ME': ('The fast messenger god. Like me!', 'happy'), 'SA': ('Roman god of farming!', 'calm'),
        'NE': ('God of the sea. I am blue!', 'cool'), 'UR': ('Greek god of the sky!', 'happy'),
        'PL': ('Named by an 11 year old girl!', 'love'), 'EA': ('My name just means the ground.', 'calm')}),
    'discovered': dict(title='PLANETS: WHEN WERE YOU DISCOVERED?', scene='space', name='Discovery', lines={
        'UR': ('1781, by William Herschel!', 'happy'), 'NE': ('1846, found with math!', 'cool'),
        'PL': ('1930, by Clyde Tombaugh!', 'love'), 'EA': ('Discovered? I am home!', 'calm'),
        'SA': ('Known since ancient times!', 'cool'), 'JU': ('Galileo found my moons in 1610!', 'happy'),
        'VE': ('Ancient people tracked me!', 'cool')}),
    'galaxy': dict(title='PLANETS WHEN SOMEONE ASKS ABOUT THE GALAXY', scene='nebula', name='Galaxy', lines={
        'SU': ('One lap around the galaxy takes 230 million years!', 'cool'), 'EA': ('We live in the Milky Way!', 'love'),
        'JU': ('The galaxy is 100,000 light years wide!', 'shock'), 'NE': ('Andromeda arrives in about 4.5 billion years!', 'shock'),
        'MA': ('Space is mostly empty!', 'calm'), 'SA': ('Billions of galaxies out there!', 'happy')}),
    'eclipse': dict(title='PLANETS DURING AN ECLIPSE', scene='sunlit', name='Eclipse', lines={
        'MO': ('I cover the Sun perfectly!', 'cool'), 'SU': ('400 times bigger, 400 times farther!', 'cool'),
        'EA': ('My shadow turns the Moon red!', 'shock'), 'JU': ('My moons cast shadows on me!', 'happy'),
        'MA': ('Phobos makes mini eclipses here!', 'happy'), 'ME': ('I cross the Sun as a tiny dot!', 'calm')}),
    'asteroid': dict(title='PLANETS WHEN AN ASTEROID SHOWS UP', scene='space', name='Asteroids', lines={
        'JU': ('A comet hit me in 1994!', 'shock'), 'EA': ('About 100 tons of space dust a day!', 'shock'),
        'MO': ('No air to stop them. Craters!', 'cry'), 'MA': ('The asteroid belt is my neighbor!', 'cool'),
        'SU': ('Over a million asteroids orbit me!', 'calm'), 'SA': ('My rings are made of ice chunks!', 'cool')}),
    'giants': dict(title="PLANETS WHEN SOMEONE SAYS 'GAS GIANT'", scene='space', name='Planet Types', lines={
        'UR': ('Ice giant! Water, methane, ammonia.', 'cool'), 'NE': ('Ice giant too! Twins!', 'happy'),
        'JU': ('Gas giant. Mostly hydrogen!', 'cool'), 'SA': ('Gas giant, hydrogen and helium!', 'love'),
        'EA': ('Rocky planet, thank you.', 'calm'), 'PL': ('Dwarf planet of ice and rock!', 'cry'),
        'MA': ('Rocky, with icy poles!', 'cool')}),
    'inside': dict(title="PLANETS WHEN ASKED WHAT'S INSIDE", scene='sunlit', name='Inside', lines={
        'EA': ('An iron core almost as hot as the Sun’s surface!', 'shock'), 'ME': ('Huge iron core, 85 percent of my radius!', 'cool'),
        'JU': ('Maybe a fuzzy, dissolved core!', 'calm'), 'MO': ('A small iron core.', 'calm'),
        'SU': ('Fusion! Hydrogen into helium!', 'happy'), 'MA': ('A liquid core, says InSight!', 'cool'),
        'SA': ('A rocky core, probably!', 'calm')}),
    'lights': dict(title='PLANETS WHEN THE LIGHTS GO OUT', scene='space', name='Light', lines={
        'MO': ('I do not glow. I reflect sunlight!', 'calm'), 'SU': ('I make my own light!', 'cool'),
        'EA': ('City lights from space!', 'love'), 'JU': ('Lightning stronger than Earth’s!', 'shock'),
        'SA': ('Lightning storms here too!', 'happy'), 'VE': ('Maybe lightning in my clouds!', 'cool')}),
    'weird': dict(title='PLANETS SHARING THEIR WEIRDEST FACT', scene='nebula', name='Weird Facts', lines={
        'VE': ('The Sun rises in my west!', 'shock'), 'UR': ('I roll around the Sun!', 'happy'),
        'SA': ('My moon Pan looks like ravioli!', 'love'), 'MO': ('The same side always faces Earth!', 'calm'),
        'ME': ('Sometimes the Sun goes backwards here!', 'shock'), 'PL': ('Charon and I always face each other!', 'love'),
        'JU': ('I have no solid surface!', 'cool')}),
    'interview': dict(title='PLANETS AT A JOB INTERVIEW', scene='sunlit', name='Job Interview', lines={
        'EA': ('Experience: hosting life for billions of years.', 'cool'), 'SU': ('I power everything here.', 'cool'),
        'MO': ('I make your ocean tides!', 'happy'), 'MA': ('Hosting robots since 1976!', 'happy'),
        'JU': ('Skills: gravity. Lots of it.', 'cool'), 'PL': ('Part-time planet, full-time cute.', 'love')}),
    'selfie': dict(title='PLANETS TAKING SELFIES', scene='space', name='Photos', lines={
        'EA': ('Pale Blue Dot, 1990!', 'love'), 'MA': ('Curiosity takes selfies on me!', 'happy'),
        'SA': ('Cassini photographed Earth from behind me!', 'cool'), 'PL': ('New Horizons saw my heart!', 'love'),
        'JU': ('Juno close-ups look like art!', 'cool'), 'MO': ('Earthrise, 1968!', 'happy')}),
    'olympics': dict(title='PLANETS AT THE SPACE OLYMPICS', scene='party', name='Records', lines={
        'ME': ('Fastest orbit. Gold medal!', 'happy'), 'JU': ('Biggest and fastest spin!', 'cool'),
        'VE': ('Hottest planet. Gold in heat!', 'angry'), 'NE': ('Fastest winds. Gold!', 'cool'),
        'SA': ('Lowest density. Gold in floating!', 'love'), 'UR': ('Coldest air. Gold!', 'shiver'),
        'EA': ('Only known home of life. Gold!', 'love')}),
    'coffee': dict(title='PLANETS ORDERING COFFEE', scene='sunlit', name='Coffee', lines={
        'VE': ('Extra hot. 465 degrees, please.', 'angry'), 'NE': ('Iced. I am minus 200!', 'shiver'),
        'MA': ('Something red. Like my rust.', 'cool'), 'EA': ('A latte. Room temperature.', 'happy'),
        'ME': ('To go! I orbit fast!', 'happy'), 'SA': ('With a ring of foam!', 'love')}),
    'wifi': dict(title='PLANETS WHEN THE WIFI IS SLOW', scene='space', name='Signal Delay', lines={
        'MA': ('Messages take up to 22 minutes!', 'angry'), 'MO': ('About a 1.3 second delay. Fine.', 'calm'),
        'PL': ('My photos took over a year to download!', 'cry'), 'EA': ('Five bars. All good.', 'happy'),
        'JU': ('Juno signals take about 45 minutes!', 'sleepy')}),
    'gym': dict(title='PLANETS AT THE GYM', scene='party', name='Gym', lines={
        'JU': ('Lifting with 2.4 times gravity!', 'angry'), 'MO': ('Easy mode. One sixth gravity!', 'happy'),
        'MA': ('Lift almost three times more here!', 'cool'), 'EA': ('Standard weights.', 'calm'),
        'ME': ('Cardio. 47 km per second!', 'happy'), 'SA': ('Spin class. Ten hour days!', 'cool')}),
    'air': dict(title='PLANETS WHEN SOMEONE TAKES A DEEP BREATH', scene='nebula', name='Atmosphere', lines={
        'EA': ('Nitrogen and oxygen. Breathe!', 'love'), 'MA': ('95 percent carbon dioxide.', 'cool'),
        'VE': ('96 percent carbon dioxide too!', 'angry'), 'JU': ('Mostly hydrogen and helium.', 'cool'),
        'MO': ('Almost no air at all.', 'calm'), 'ME': ('A super thin exosphere.', 'calm'),
        'SA': ('Hydrogen and helium, please.', 'happy')}),
    'twins': dict(title='PLANETS MEETING THEIR TWIN', scene='space', name='Twins', lines={
        'VE': ('I am Earth’s twin in size!', 'love'), 'EA': ('Twins? You are 465 degrees!', 'shock'),
        'UR': ('Neptune and I are almost twins!', 'happy'), 'NE': ('Same size, different blue!', 'cool'),
        'PL': ('Charon is half my size!', 'love'), 'SA': ('Jupiter is just a bigger me.', 'cool')}),
    'school': dict(title='PLANETS ON THE FIRST DAY OF SCHOOL', scene='party', name='School', lines={
        'ME': ('First in line. Closest to the Sun!', 'happy'), 'EA': ('Third seat. Perfect spot.', 'cool'),
        'JU': ('Biggest kid in class!', 'cool'), 'PL': ('Still not on the class list.', 'cry'),
        'NE': ('Farthest seat, by the window.', 'sleepy'), 'MA': ('Fourth seat, red backpack.', 'happy')}),
    'famous': dict(title='PLANETS WHEN THEY GET FAMOUS', scene='party', name='Fame', lines={
        'MA': ('Most explored planet after Earth!', 'cool'), 'MO': ('The only world humans walked on!', 'love'),
        'JU': ('Galileo’s moons made history!', 'happy'), 'SA': ('The most famous rings!', 'love'),
        'PL': ('Everyone still loves me!', 'happy'), 'EA': ('Only planet with pizza.', 'happy')}),
    'freezing': dict(title='PLANETS WHEN THE HEATER BREAKS', scene='ice', name='Cold', lines={
        'NE': ('Minus 200. Normal Tuesday.', 'cool'), 'UR': ('Minus 224 at my coldest!', 'shiver'),
        'PL': ('Minus 230. Pass the blanket.', 'shiver'), 'MO': ('Minus 130 at night!', 'shiver'),
        'MA': ('Minus 125 at my poles!', 'shiver'), 'EA': ('Minus 89 was my record!', 'shock'),
        'VE': ('Heater? I am 465!', 'angry')}),
    'rocket': dict(title='PLANETS WHEN A ROCKET LAUNCHES', scene='sunlit', name='Escape Speed', lines={
        'EA': ('Escape speed: 11 km per second!', 'cool'), 'MO': ('Only 2.4 km per second to leave me!', 'happy'),
        'MA': ('Five km per second to leave!', 'cool'), 'JU': ('60 km per second. Good luck!', 'angry'),
        'SU': ('618 km per second!', 'shock'), 'PL': ('About 1.2 km per second!', 'love')}),
})

SITUATIONS.update({
    'vacation': dict(title='PLANETS PLANNING YOUR VACATION', scene='sunlit', name='Vacation', lines={
        'EA': ('Visit the Moon. Three days away!', 'happy'), 'MO': ('Bring a spacesuit. No air!', 'calm'),
        'MA': ('Pack warm. Minus 60!', 'shiver'), 'VE': ('Do not. 92 times Earth’s air pressure!', 'angry'),
        'SA': ('Come see Titan’s methane lakes!', 'love'), 'NE': ('Bring a jacket. Minus 200!', 'shiver'),
        'PL': ('Long flight. About nine years!', 'cry'), 'JU': ('Watch my storms from a safe moon!', 'cool')}),
    'pressure': dict(title='PLANETS UNDER PRESSURE', scene='nebula', name='Pressure', lines={
        'VE': ('92 times Earth’s air pressure!', 'angry'), 'EA': ('One atmosphere. Comfy.', 'calm'),
        'MA': ('Less than one percent of Earth’s!', 'shock'), 'MO': ('Basically zero pressure!', 'calm'),
        'JU': ('Deep inside, hydrogen acts like metal!', 'shock'), 'SA': ('Metallic hydrogen inside me too!', 'cool'),
        'ME': ('Almost a vacuum here.', 'calm')}),
    'bestfriend': dict(title='PLANETS INTRODUCING THEIR BEST FRIEND', scene='party', name='Best Friends', lines={
        'EA': ('The Moon, obviously!', 'love'), 'MO': ('Earth! I always show one face.', 'love'),
        'PL': ('Charon! We orbit each other.', 'love'), 'MA': ('Phobos and Deimos!', 'happy'),
        'JU': ('My four big Galilean moons!', 'cool'), 'SA': ('Titan, bigger than Mercury!', 'cool'),
        'NE': ('Triton, probably captured from far away!', 'cool')}),
    'skycolor': dict(title='PLANETS: WHAT COLOR IS YOUR SKY?', scene='sunlit', name='Sky Color', lines={
        'EA': ('Blue by day, orange sunsets!', 'happy'), 'MA': ('Butterscotch by day, blue sunsets!', 'love'),
        'VE': ('Orange, under thick clouds.', 'cool'), 'MO': ('Black, even in daytime!', 'shock'),
        'SA': ('Titan’s sky is orange haze!', 'cool')}),
    'storm': dict(title='PLANETS DURING A STORM', scene='nebula', name='Storms', lines={
        'JU': ('My Great Red Spot is wider than Earth!', 'cool'), 'SA': ('A giant storm circled me in 2010!', 'shock'),
        'NE': ('Voyager saw my Great Dark Spot!', 'cool'), 'EA': ('Hurricanes up to 300 km/h!', 'shock'),
        'MA': ('Dust storms that last for months!', 'angry'), 'UR': ('Storms pop up near my poles!', 'happy')}),
    'newyear': dict(title="PLANETS ON NEW YEAR'S EVE", scene='party', name="New Year's Eve", lines={
        'EA': ('Countdown every 365 days!', 'happy'), 'ME': ('New Year every 88 days!', 'happy'),
        'UR': ('Happy New Year! Next one in 84 years!', 'sleepy'), 'NE': ('One New Year every 165 years!', 'cry'),
        'PL': ('My next New Year? 2178!', 'cry'), 'JU': ('Every 12 years. Big party!', 'love'),
        'MA': ('Every 687 days!', 'cool')}),
    'moonlight': dict(title='PLANETS WHEN THE MOON SHOWS UP', scene='space', name='Moon', lines={
        'MO': ('Hi! I am 3,474 km wide.', 'happy'), 'EA': ('She controls my ocean tides!', 'love'),
        'SU': ('Moonlight is just my light, reflected!', 'cool'), 'JU': ('My Ganymede is bigger than Mercury!', 'cool'),
        'MA': ('My moons are tiny potatoes.', 'cry'), 'PL': ('Charon is huge for my size!', 'happy'),
        'SA': ('Titan has thicker air than Earth!', 'shock')}),
})

# 2026-10-13: kullanıcı "oyuncuları artır" → 4 yeni karakter: Titan (TI), Europa (EU), Io (IO), Ceres (CE). Aynı kural: gerçek bilgi.
_NEW = {
    'daylength': {'TI': ('16 Earth days. Same as my orbit!', 'calm'), 'EU': ('3.5 days. Locked to Jupiter!', 'cool'),
                  'IO': ('42 hours. Fast lap!', 'happy'), 'CE': ('Nine hours. Quick spin!', 'happy')},
    'hot': {'IO': ('My lava is over 1,000°C!', 'angry'), 'EU': ('Minus 160 on my ice.', 'shiver'), 'TI': ('Minus 179. Brrr.', 'shiver')},
    'moons': {'TI': ('I am Saturn\'s biggest moon!', 'cool'), 'EU': ('One of Jupiter\'s four big moons!', 'happy'),
              'IO': ('The closest of Jupiter\'s big moons!', 'cool'), 'CE': ('No moons. Just asteroid friends.', 'calm')},
    'small': {'TI': ('Bigger than Mercury!', 'cool'), 'EU': ('A bit smaller than your Moon.', 'calm'),
              'IO': ('Slightly bigger than your Moon!', 'happy'), 'CE': ('Biggest in the asteroid belt!', 'cool')},
    'rain': {'TI': ('Methane rain! Real rain!', 'shock'), 'IO': ('Sulfur frost falls here!', 'cool')},
    'water': {'EU': ('A whole ocean under my ice!', 'love'), 'TI': ('Lakes of liquid methane!', 'cool'),
              'CE': ('Maybe salty water deep inside!', 'happy'), 'IO': ('Bone dry. Just lava.', 'angry')},
    'volcano': {'IO': ('Over 400 active volcanoes!', 'shock'), 'EU': ('Maybe water plumes!', 'cool'),
                'TI': ('Maybe ice volcanoes!', 'calm'), 'CE': ('An ice volcano called Ahuna Mons!', 'happy')},
    'visitors': {'TI': ('Huygens landed on me in 2005!', 'love'), 'EU': ('Europa Clipper is on its way!', 'happy'),
                 'CE': ('Dawn orbited me in 2015!', 'love'), 'IO': ('Juno flew close to me!', 'cool')},
    'pluto': {'CE': ('I am a dwarf planet too!', 'love'), 'TI': ('I am bigger than you, Pluto.', 'cool'),
              'EU': ('Even I am bigger than you!', 'calm')},
    'outfit': {'IO': ('Yellow and orange sulfur!', 'cool'), 'TI': ('Orange haze. Always.', 'calm'),
               'EU': ('White ice with reddish cracks.', 'love'), 'CE': ('Gray with bright salty spots!', 'happy')},
    'air': {'TI': ('Thicker air than Earth!', 'shock'), 'IO': ('Thin sulfur dioxide air.', 'cool'),
            'EU': ('A tiny bit of oxygen!', 'happy'), 'CE': ('Almost no air.', 'calm')},
    'jump': {'TI': ('With wings, you could fly here!', 'love'), 'EU': ('Jump about seven times higher!', 'happy'),
             'IO': ('Jump five times higher!', 'happy'), 'CE': ('Jump 35 times higher!', 'shock')},
    'weird': {'IO': ('Jupiter squeezes me and I melt!', 'shock'), 'TI': ('I have rivers, lakes and seas!', 'cool'),
              'EU': ('One of the smoothest surfaces around!', 'cool'), 'CE': ('My bright spots are salt!', 'shock')},
    'swim': {'TI': ('Swim in methane? Maybe not.', 'calm'), 'EU': ('My ocean may hold twice Earth\'s water!', 'love'),
             'CE': ('Maybe salty water inside!', 'happy')},
    'bestfriend': {'TI': ('Saturn, my giant buddy!', 'love'), 'EU': ('Jupiter, of course!', 'love'),
                   'IO': ('Jupiter. He squeezes me!', 'angry'), 'CE': ('Vesta, my asteroid neighbor!', 'happy')},
    'discovered': {'TI': ('1655, by Christiaan Huygens!', 'cool'), 'EU': ('1610, by Galileo!', 'happy'),
                   'IO': ('1610, by Galileo too!', 'happy'), 'CE': ('1801, the first asteroid ever found!', 'love')},
    'giants': {'CE': ('Dwarf planet, rock and ice!', 'cool'), 'TI': ('A moon with planet vibes.', 'cool')},
    'skycolor': {'IO': ('Jupiter fills my sky!', 'shock'), 'EU': ('Giant Jupiter in my sky!', 'love')},
    'trip': {'EU': ('Clipper takes almost six years!', 'calm'), 'CE': ('Dawn took about eight years to reach me.', 'sleepy'),
             'TI': ('Cassini-Huygens took seven years!', 'calm')},
    'freezing': {'TI': ('Minus 179. Normal.', 'cool'), 'EU': ('Minus 160 on the surface!', 'shiver'),
                 'CE': ('About minus 105. Brrr.', 'shiver'), 'IO': ('Cold ground, hot volcanoes!', 'cool')},
    'olympics': {'IO': ('Most volcanic world. Gold!', 'happy'), 'TI': ('Only moon with thick air. Gold!', 'cool'),
                 'CE': ('Biggest in the asteroid belt. Gold!', 'happy'), 'EU': ('Smoothest surface. Gold!', 'love')},
    'selfie': {'CE': ('Dawn snapped my bright spots!', 'love'), 'IO': ('Juno caught my lava lakes!', 'cool'),
               'EU': ('Galileo mapped my cracks!', 'happy'), 'TI': ('Huygens took photos on the way down!', 'love')},
}
for _k, _v in _NEW.items():
    SITUATIONS[_k]['lines'].update(_v)

# 2026-10-25: yeni durumlar (her durum Shorts'ta yalnız bir kez) + yeni ortamlar (belt, aurora, rings, volcano, eclipse)
SITUATIONS.update({
    'backwards': dict(title="PLANETS WHEN TOLD 'YOU'RE DOING IT BACKWARDS'", scene='rings', name='Backwards Spin', lines={
        'VE': ('I spin backwards. My Sun rises in the west!', 'cool'), 'EA': ('Sun rises in the east. Like a normal planet.', 'calm'),
        'NE': ('My moon Triton orbits me backwards!', 'shock'), 'PL': ('I spin backwards too. Rebel life!', 'happy'),
        'JU': ('Forward, and fastest of all!', 'cool'), 'MO': ('I always show Earth the same face.', 'calm'),
        'UR': ('I just roll along on my side.', 'sleepy')}),
    'reply': dict(title='PLANETS WHEN YOU TEXT THEM', scene='space', name='Message Delay', lines={
        'MO': ('Reply in about 1.3 seconds!', 'happy'), 'MA': ('3 to 22 minutes, one way. Sorry!', 'calm'),
        'SU': ('My light takes 8 minutes to reach you.', 'cool'), 'JU': ('Roughly 35 to 50 minutes. Patience!', 'sleepy'),
        'SA': ('Over an hour. Each way!', 'shock'), 'NE': ('About four hours. Leave a voicemail.', 'cool'),
        'PL': ('Four to seven hours. Hold on!', 'cry'), 'EA': ('Instant. I am right here.', 'love')}),
    'tides': dict(title='PLANETS WHEN THE TIDE COMES IN', scene='aurora', name='Tides', lines={
        'MO': ('My gravity pulls your oceans. Tides!', 'cool'), 'EA': ('Two high tides a day. Thanks, Moon!', 'love'),
        'SU': ('I make tides too, about half as strong.', 'calm'), 'IO': ("Jupiter's tides melt my insides!", 'shock'),
        'EU': ('Tides may keep my ocean liquid!', 'happy'), 'JU': ('My tides squeeze Io into volcanoes.', 'cool'),
        'NE': ('Tides pull Triton closer to me!', 'calm')}),
    'drifting': dict(title="PLANETS WHEN SOMEONE SAYS 'WE'RE DRIFTING APART'", scene='space', name='Drifting', lines={
        'MO': ('I move 3.8 centimeters away every year.', 'cry'), 'EA': ('My days get a tiny bit longer every century.', 'sleepy'),
        'MA': ('Phobos creeps closer every year!', 'shock'), 'NE': ('Triton is spiraling in toward me.', 'calm'),
        'SA': ('My rings might vanish someday.', 'cry'), 'SU': ('I lose a bit of mass every second.', 'calm')}),
    'craters': dict(title='PLANETS SHOWING THEIR SCARS', scene='belt', name='Craters', lines={
        'MO': ('No wind here, so my craters stay forever!', 'calm'), 'ME': ('Caloris Basin, 1,500 km wide!', 'shock'),
        'EA': ('Chicxulub crater. Ask the dinosaurs.', 'cry'), 'MA': ('Hellas Basin, over 2,000 km wide!', 'cool'),
        'CE': ('Occator crater holds my bright salt!', 'love'), 'JU': ('A comet smashed into me in 1994!', 'angry')}),
    'icecold': dict(title='PLANETS WHEN SOMEONE ORDERS ICE', scene='aurora', name='Ice', lines={
        'EA': ('Ice caps at both poles.', 'calm'), 'MA': ('Polar caps of water ice and dry ice!', 'cool'),
        'ME': ('Even I have ice, in shadowy craters!', 'shock'), 'MO': ('Ice hides in my dark polar craters!', 'happy'),
        'EU': ('My whole surface is ice!', 'love'), 'PL': ('A heart-shaped glacier of nitrogen ice!', 'love'),
        'UR': ('They call me an ice giant.', 'sleepy'), 'NE': ('Ice giant too. Coolest family.', 'cool')}),
    'neighbors': dict(title='PLANETS MEETING THE NEIGHBORS', scene='belt', name='Neighbors', lines={
        'EA': ('Fun fact: Mercury is my closest neighbor on average!', 'shock'), 'VE': ('But I get closest to Earth!', 'angry'),
        'CE': ('I live in the asteroid belt!', 'happy'), 'JU': ('Trojan asteroids share my orbit!', 'cool'),
        'NE': ('Pluto crosses my orbit!', 'angry'), 'PL': ('Relax, Neptune. We never collide.', 'cool'),
        'MA': ('Next door to the asteroid belt.', 'calm')}),
    'cleanroom': dict(title='PLANETS CLEANING THEIR ROOM', scene='belt', name='Cleaning', lines={
        'MA': ('Dust storms can cover my whole planet!', 'angry'), 'EA': ('Over 25,000 tracked pieces of space junk!', 'cry'),
        'MO': ('Humans left over 180 tons of stuff on me!', 'shock'), 'SA': ('My rings are icy chunks. Neat!', 'happy'),
        'JU': ('I sweep up comets and asteroids!', 'cool'), 'SU': ('My solar wind blows dust away!', 'cool')}),
    'diet': dict(title='PLANETS ON A DIET', scene='sunlit', name='Mass', lines={
        'SU': ('I lose 4 million tons every second!', 'shock'), 'EA': ('Tons of space dust land on me daily!', 'cry'),
        'ME': ('I shrank! Up to 7 km across.', 'happy'), 'MA': ('I lost most of my air to the solar wind.', 'cry'),
        'JU': ('Mostly hydrogen and helium. Light stuff!', 'cool'), 'SA': ('My rings are mostly water ice.', 'calm')}),
    'superpower': dict(title='PLANETS SHOWING THEIR SUPERPOWER', scene='eclipse', name='Superpowers', lines={
        'SU': ('I fuse 600 million tons of hydrogen per second!', 'cool'), 'EA': ('Only known planet with life!', 'love'),
        'MO': ("I keep Earth's tilt steady!", 'cool'), 'MA': ('I make the biggest dust storms!', 'angry'),
        'VE': ('Brightest planet in your night sky!', 'happy'), 'ME': ('Fastest planet around the Sun!', 'happy'),
        'TI': ('Thicker air than Earth!', 'cool')}),
    'future': dict(title='PLANETS PREDICTING THE FUTURE', scene='eclipse', name='Future', lines={
        'SU': ('Red giant in about 5 billion years.', 'calm'), 'MO': ('Total eclipses end in about 600 million years.', 'cry'),
        'EA': ('In a billion years, my oceans get too hot.', 'shiver'), 'MA': ('Phobos may become a ring!', 'shock'),
        'NE': ('Triton may become a ring too!', 'shock'), 'SA': ('My rings might be gone someday.', 'cry')}),
    'crash': dict(title='PLANETS WHEN SOMEONE BUMPS INTO THEM', scene='belt', name='Impacts', lines={
        'MO': ('I was probably born from a crash!', 'shock'), 'EA': ('A Mars-sized world hit me. Then came the Moon!', 'cool'),
        'UR': ('A giant crash may have knocked me sideways!', 'sleepy'), 'VE': ('Maybe a crash flipped my spin.', 'angry'),
        'MA': ('A huge impact may explain my two halves.', 'calm'), 'ME': ('A giant hit may have stripped my outer layers!', 'cry'),
        'JU': ('Comet Shoemaker-Levy 9. Ouch!', 'angry')}),
    'gift': dict(title='PLANETS GIVING GIFTS', scene='party', name='Gifts', lines={
        'MA': ('I sent you hundreds of meteorites!', 'happy'), 'MO': ('Apollo took home 382 kg of my rocks!', 'love'),
        'SU': ('Free sunlight. You are welcome.', 'cool'), 'EA': ('I gave the Moon footprints. Twelve people!', 'love'),
        'CE': ('Shiny salt spots, just for you!', 'happy'), 'SA': ('Ring photos from Cassini!', 'love')}),
    'dance': dict(title='PLANETS AT A DANCE PARTY', scene='party', name='Spins', lines={
        'EA': ('I wobble! Once every 26,000 years.', 'happy'), 'JU': ('I spin fastest of all planets!', 'cool'),
        'PL': ('Charon and I always face each other!', 'love'), 'MO': ('I never turn my back on Earth.', 'love'),
        'SA': ('My rings ripple with spiral waves!', 'happy'), 'NE': ('Triton dances backwards around me!', 'cool'),
        'UR': ('I roll on my side. Signature move.', 'sleepy')}),
    'bright': dict(title="PLANETS WHEN SOMEONE SAYS 'YOU'RE NOT THAT BRIGHT'", scene='eclipse', name='Brightness', lines={
        'VE': ('Brightest planet in your sky!', 'angry'), 'MO': ('Brightest thing at night!', 'cool'),
        'SU': ('Brightest thing, period.', 'cool'), 'EU': ('My ice reflects lots of sunlight!', 'happy'),
        'SA': ('My moon Enceladus is the shiniest!', 'love'), 'JU': ('Often third brightest at night!', 'calm'),
        'MA': ('I glow red. Easy to spot!', 'happy')}),
    'darkside': dict(title="PLANETS WHEN SOMEONE SAYS 'DARK SIDE'", scene='eclipse', name='Dark Side', lines={
        'MO': ('Not dark! My far side gets sunlight too.', 'angry'), 'EA': ('Half of me is always night.', 'calm'),
        'UR': ('Each pole gets 42 years of darkness!', 'shock'), 'SA': ('My rings cast shadows on me!', 'cool'),
        'ME': ('Night lasts months here.', 'sleepy'), 'SU': ('Dark side? Never heard of it.', 'cool')}),
    'quake': dict(title='PLANETS WHEN THE GROUND SHAKES', scene='volcano', name='Quakes', lines={
        'EA': ('About half a million quakes a year!', 'shock'), 'MO': ('Some moonquakes last over 10 minutes!', 'shiver'),
        'MA': ('InSight heard over 1,300 marsquakes!', 'cool'), 'SU': ('Sunquakes ripple my surface!', 'cool'),
        'ME': ('I am shrinking, so my crust cracks!', 'cry'), 'IO': ('My lava never stops bubbling!', 'angry')}),
    'beach': dict(title='PLANETS AT THE BEACH', scene='sunlit', name='Beach', lines={
        'MA': ('Sand dunes everywhere!', 'happy'), 'EA': ('Real beaches, real water.', 'love'),
        'TI': ('My dunes are made of hydrocarbon grains!', 'cool'), 'VE': ('Beach day at 465°C? Pass.', 'angry'),
        'PL': ('I have dunes of methane ice!', 'shiver'), 'MO': ('My soil is sharp, not soft!', 'cry')}),
    'telescope': dict(title='PLANETS WHEN THE TELESCOPE ARRIVES', scene='rings', name='Telescopes', lines={
        'SA': ('Galileo thought my rings were ears!', 'shock'), 'VE': ('Galileo saw my phases, like the Moon!', 'happy'),
        'NE': ('Webb photographed my rings!', 'love'), 'UR': ('Webb snapped my rings too!', 'love'),
        'MA': ('Hubble watches my dust storms!', 'cool'), 'JU': ('Even binoculars show my four big moons!', 'happy')}),
    'jewelry': dict(title='PLANETS WHEN SOMEONE TALKS ABOUT JEWELRY', scene='rings', name='Jewelry', lines={
        'NE': ('It might rain diamonds inside me!', 'shock'), 'UR': ('Maybe diamond rain deep inside!', 'love'),
        'SA': ('Maybe diamond hail deep inside!', 'cool'), 'EA': ('I make diamonds deep underground.', 'cool'),
        'MA': ('I have rust. Does that count?', 'cry'), 'CE': ('Salt crystals! Sodium carbonate!', 'happy')}),
    'lava': dict(title='PLANETS WHEN SOMEONE SAYS "THE FLOOR IS LAVA"', scene='volcano', name='Lava', lines={
        'IO': ('My floor IS lava. Over 400 volcanoes!', 'happy'), 'EA': ('Only in a few hot spots.', 'calm'),
        'VE': ('Huge lava plains cover me!', 'cool'), 'MO': ('My dark patches are old lava!', 'calm'),
        'MA': ('Olympus Mons is an old lava volcano!', 'cool'), 'ME': ('Ancient lava flooded my plains!', 'shock')}),
})


# ---------------------------------------------------------------- uzay sahneleri (kodla çizilir)
def vgrad(w, h, c1, c2):
    t = np.linspace(0, 1, h)[:, None, None]
    return (np.array(c1, float) * (1 - t) + np.array(c2, float) * t) * np.ones((1, w, 1))


SKY = {'space': ((6, 8, 28), (22, 24, 64)), 'nebula': ((24, 8, 44), (70, 30, 96)), 'sunlit': ((20, 14, 40), (90, 44, 60)),
       'ice': ((6, 18, 40), (30, 70, 110)), 'party': ((26, 8, 34), (80, 30, 50)),
       # 2026-10-25 yeni ortamlar (aynı sahne hissi tekrar etmesin)
       'belt': ((10, 10, 20), (40, 34, 48)), 'aurora': ((4, 14, 30), (10, 50, 60)), 'rings': ((14, 10, 30), (60, 46, 70)),
       'volcano': ((30, 8, 6), (110, 40, 14)), 'eclipse': ((2, 2, 8), (16, 14, 34))}
GROUND = {'space': (92, 90, 104), 'nebula': (110, 92, 120), 'sunlit': (150, 110, 90), 'ice': (170, 200, 220), 'party': (90, 70, 100),
          'belt': (112, 98, 84), 'aurora': (150, 175, 190), 'rings': (196, 170, 120), 'volcano': (70, 56, 40), 'eclipse': (70, 72, 86)}
SCENES = tuple(SKY)


@lru_cache(None)
def scene_bg(kind):
    w, h = L(W), L(H)
    gy = int(h * 0.70)
    c1, c2 = SKY.get(kind, SKY['space'])
    img = Image.fromarray(vgrad(w, h, c1, c2).astype(np.uint8)).convert('RGBA'); d = ImageDraw.Draw(img)
    rnd = random.Random(sum(map(ord, kind)))
    if kind in ('nebula', 'party'):   # yumuşak bulutsu lekeleri
        neb = Image.new('RGBA', (w, h), (0, 0, 0, 0)); nd = ImageDraw.Draw(neb)
        for _ in range(7):
            x, y, r = rnd.uniform(0, W), rnd.uniform(100, H * 0.6), rnd.uniform(160, 340)
            col = rnd.choice([(170, 70, 200), (60, 120, 230), (230, 90, 150)] if kind == 'nebula' else [(240, 120, 40), (150, 60, 200)])
            nd.ellipse(box(x - r, y - r * 0.7, x + r, y + r * 0.7), fill=col + (70,))
        img.alpha_composite(neb.filter(ImageFilter.GaussianBlur(L(60))))
    for _ in range(220):   # yıldızlar
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H * 0.69), rnd.choice([1.5, 2, 2.5, 3.5])
        d.ellipse(box(x - r, y - r, x + r, y + r), fill=(255, 255, 240))
    if kind == 'aurora':   # dalgalı yeşil-mor kutup ışığı perdeleri
        au = Image.new('RGBA', (w, h), (0, 0, 0, 0)); ad = ImageDraw.Draw(au)
        for k, col in enumerate(((60, 230, 140), (90, 255, 180), (150, 90, 230))):
            pts = [(x, 260 + 110 * k + 70 * math.sin(x / 170 + k * 1.7)) for x in range(-40, W + 60, 30)]
            for x, y in pts:
                ad.rectangle(box(x - 14, y, x + 14, y + 330), fill=col + (55,))
        img.alpha_composite(au.filter(ImageFilter.GaussianBlur(L(26))))
    if kind == 'rings':   # gökyüzünü kesen dev halka yayı
        rg = Image.new('RGBA', (w, h), (0, 0, 0, 0)); rd = ImageDraw.Draw(rg)
        for k, (col, al) in enumerate((((230, 200, 150), 150), ((190, 160, 120), 120), ((240, 220, 180), 170), ((160, 130, 100), 110))):
            r = 1300 + 50 * k
            rd.arc(box(W / 2 - r * 0.9, 1150 - r * 0.45, W / 2 + r * 0.9, 1150 + r * 0.45), 180, 360, fill=col + (al,), width=L(48))
        img.alpha_composite(rg.filter(ImageFilter.GaussianBlur(L(2))))
    if kind == 'eclipse':   # kara güneş + taç ışığı
        cr = Image.new('RGBA', (w, h), (0, 0, 0, 0)); cd = ImageDraw.Draw(cr)
        for k, al in ((260, 40), (200, 80), (160, 140)):
            cd.ellipse(box(W * 0.7 - k, 520 - k, W * 0.7 + k, 520 + k), fill=(255, 235, 190, al))
        img.alpha_composite(cr.filter(ImageFilter.GaussianBlur(L(30))))
        d.ellipse(box(W * 0.7 - 140, 520 - 140, W * 0.7 + 140, 520 + 140), fill=(4, 4, 10))
    if kind == 'volcano':   # ufukta kızıl lav parıltısı
        gl = Image.new('RGBA', (w, h), (0, 0, 0, 0)); gd2 = ImageDraw.Draw(gl)
        gd2.ellipse(box(-200, H * 0.55, W + 200, H * 0.85), fill=(255, 110, 30, 120))
        img.alpha_composite(gl.filter(ImageFilter.GaussianBlur(L(70))))
    if kind == 'belt':   # süzülen kaya parçaları
        for _ in range(26):
            x, y, r = rnd.uniform(0, W), rnd.uniform(80, H * 0.62), rnd.uniform(10, 46)
            pts = [(x + r * rnd.uniform(0.7, 1.2) * math.cos(a), y + r * rnd.uniform(0.6, 1.1) * math.sin(a)) for a in [i * math.pi / 4 for i in range(8)]]
            d.polygon([(L(px), L(py)) for px, py in pts], fill=(120, 108, 96))
            d.ellipse(box(x - r * 0.3, y - r * 0.3, x, y), fill=(92, 82, 74))
    if kind == 'sunlit':   # köşede dev güneş ışığı
        glow = Image.new('RGBA', (w, h), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
        for k, al in ((620, 40), (460, 70), (320, 120)):
            gd.ellipse(box(-k + 120, 380 - k, k + 120, 380 + k), fill=(255, 190, 80, al))
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(L(40))))
    # kraterli küçük gezegen zemini (karakterler üstünde durur)
    gc = GROUND.get(kind, GROUND['space'])
    d.ellipse([-L(400), gy - L(60), w + L(400), gy + L(1400)], fill=gc)
    if kind == 'volcano':   # lav çatlakları
        for _ in range(9):
            x0, y0 = rnd.uniform(0, W), rnd.uniform(H * 0.74, H * 0.97)
            pts = [(x0 + 40 * j, y0 + rnd.uniform(-18, 18)) for j in range(6)]
            d.line([(L(px), L(py)) for px, py in pts], fill=(255, 120, 30), width=L(6))
    for _ in range(14):
        x, y, r = rnd.uniform(0, W), rnd.uniform(H * 0.73, H * 0.98), rnd.uniform(25, 70)
        d.ellipse(box(x - r, y - r * 0.4, x + r, y + r * 0.4), fill=tuple(int(c * 0.82) for c in gc))
        d.arc(box(x - r, y - r * 0.4, x + r, y + r * 0.4), 200, 340, fill=tuple(min(255, int(c * 1.12)) for c in gc), width=L(4))
    return img


def effects(img, kind, t):
    d = ImageDraw.Draw(img)
    rnd = random.Random(21)
    for j in range(18):   # parıldayan yıldızlar
        x, y = rnd.uniform(0, W), rnd.uniform(0, H * 0.66)
        k = 0.5 + 0.5 * math.sin(t * rnd.uniform(2, 5) + j)
        r = 2 + 4 * k
        d.line(box(x - r * 2, y, x + r * 2, y), fill=(255, 255, 255), width=L(2)); d.line(box(x, y - r * 2, x, y + r * 2), fill=(255, 255, 255), width=L(2))
    u = (t % 4.0) / 4.0   # kayan yıldız
    if u < 0.25:
        x0, y0 = 1100 - u * 4 * 900, 150 + u * 4 * 380
        d.line(box(x0, y0, x0 + 160, y0 - 68), fill=(255, 255, 230), width=L(5))
    if kind == 'volcano':   # yükselen kıvılcımlar
        for j in range(24):
            x0, sp = rnd.uniform(0, W), rnd.uniform(90, 200)
            y = H * 0.8 - (rnd.uniform(0, H * 0.7) + t * sp) % (H * 0.7)
            d.ellipse(box(x0 - 4, y - 4, x0 + 4, y + 4), fill=(255, 170, 60))
    if kind == 'belt':   # yavaşça geçen kaya
        x = (t * 120 + 200) % (W + 300) - 150
        d.ellipse(box(x - 34, 300 - 22, x + 34, 300 + 22), fill=(130, 116, 100))
    if kind == 'party':
        for j in range(30):
            x0, sp = rnd.uniform(0, W), rnd.uniform(150, 300)
            y = (rnd.uniform(0, H) + t * sp) % H; x = x0 + 30 * math.sin(t * 2 + j)
            d.rectangle(box(x - 8, y - 5, x + 8, y + 5), fill=[(255, 140, 40), (160, 80, 220), (120, 230, 120)][j % 3])


# ---------------------------------------------------------------- gezegen dokuları (prosedürel)
def _noise(w, h, seed, scale):
    r = np.random.default_rng(seed)
    out = np.zeros((h, w))
    for k, amp in ((1, 1.0), (2, 0.5), (4, 0.25)):
        g = r.random((max(2, int(h / scale * k)) + 1, max(2, int(w / scale * k)) + 1))
        out += amp * np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), float) / 255
    return out / 1.75


def _bands(h, w, cols, seed, wob=0.04):
    y = np.linspace(0, 1, h)[:, None] + wob * np.sin(np.linspace(0, 6.28, w)[None, :] * 3 + seed)
    idx = (y * (len(cols) - 1)).clip(0, len(cols) - 1.001)
    i0 = idx.astype(int); f = (idx - i0)[..., None]
    c = np.array(cols, float)
    return c[i0] * (1 - f) + c[np.minimum(i0 + 1, len(cols) - 1)] * f


@lru_cache(64)
def flag_img(code):
    """Gök cismi dokusu (580x400 RGB): bayrak yerine; ball_sprite bunu küreye sarar."""
    w, h = 580, 400
    n = _noise(w, h, sum(map(ord, code)), 60)[..., None]
    if code == 'SU':
        a = np.array((255, 196, 60)) * (0.85 + 0.3 * n) + np.array((40, 30, 0)) * _noise(w, h, 5, 12)[..., None]
    elif code in ('ME', 'MO'):
        a = np.array((165, 160, 155) if code == 'ME' else (200, 200, 205)) * (0.75 + 0.4 * n)
        im = Image.fromarray(a.clip(0, 255).astype(np.uint8)); d = ImageDraw.Draw(im); rnd = random.Random(code)
        if code == 'MO':   # karanlık denizler (maria)
            for _ in range(5):
                x, y, r = rnd.uniform(150, 450), rnd.uniform(90, 310), rnd.uniform(40, 80)
                d.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], fill=(130, 130, 140))
        for _ in range(26):
            x, y, r = rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(6, 26)
            d.ellipse([x - r, y - r, x + r, y + r], outline=(110, 105, 100), width=3)
        return im
    elif code == 'VE':
        a = _bands(h, w, [(235, 205, 140), (220, 180, 110), (240, 215, 160), (215, 175, 105)], 1, 0.08) * (0.85 + 0.25 * n)
    elif code == 'EA':
        land = _noise(w, h, 7, 90) > 0.52
        a = np.where(land[..., None], np.array((70, 150, 70)) * (0.8 + 0.3 * n), np.array((40, 110, 210)) * (0.85 + 0.2 * n))
        clouds = (_noise(w, h, 9, 40) > 0.6)[..., None]
        a = np.where(clouds, a * 0.3 + 255 * 0.7, a)
        a[:30] = a[-30:] = 245   # kutuplar
    elif code == 'MA':
        a = np.array((205, 92, 50)) * (0.8 + 0.35 * n)
        a = np.where((_noise(w, h, 3, 70) > 0.6)[..., None], a * 0.75, a)
        a[:36] = (250, 245, 240)
    elif code == 'JU':
        a = _bands(h, w, [(230, 215, 190), (190, 130, 90), (235, 220, 195), (175, 115, 80), (225, 205, 175), (195, 140, 100),
                          (235, 220, 200)], 2) * (0.9 + 0.15 * n)
        im = Image.fromarray(a.clip(0, 255).astype(np.uint8)); ImageDraw.Draw(im).ellipse([330, 230, 420, 275], fill=(200, 90, 60))
        return im
    elif code == 'SA':
        a = _bands(h, w, [(240, 220, 170), (220, 190, 130), (245, 228, 180), (210, 180, 120), (240, 220, 170)], 3, 0.02) * (0.92 + 0.12 * n)
    elif code == 'UR':
        a = _bands(h, w, [(175, 230, 235), (160, 220, 230), (180, 235, 240)], 4, 0.01) * (0.95 + 0.08 * n)
    elif code == 'NE':
        a = _bands(h, w, [(60, 100, 220), (45, 80, 200), (70, 115, 230)], 5) * (0.88 + 0.2 * n)
        im = Image.fromarray(a.clip(0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
        d.ellipse([340, 170, 420, 210], fill=(30, 50, 140)); d.line([(150, 120), (260, 115)], fill=(220, 230, 255), width=6)
        return im
    elif code == 'TI':   # turuncu pus
        a = _bands(h, w, [(235, 170, 80), (220, 150, 60), (240, 180, 95)], 6, 0.02) * (0.93 + 0.1 * n)
    elif code == 'EU':   # beyaz buz + kırmızımsı çatlaklar
        a = np.array((235, 225, 210)) * (0.9 + 0.12 * n)
        im = Image.fromarray(a.clip(0, 255).astype(np.uint8)); d = ImageDraw.Draw(im); rnd = random.Random('EU')
        for _ in range(16):
            x, y = rnd.uniform(0, w), rnd.uniform(0, h); pts = [(x, y)]
            for _ in range(5):
                x += rnd.uniform(-90, 90); y += rnd.uniform(-40, 40); pts.append((x, y))
            d.line(pts, fill=(160, 90, 60), width=rnd.choice([3, 4, 5]))
        return im
    elif code == 'IO':   # kükürt sarısı + volkan lekeleri
        a = np.array((235, 200, 70)) * (0.85 + 0.3 * n)
        im = Image.fromarray(a.clip(0, 255).astype(np.uint8)); d = ImageDraw.Draw(im); rnd = random.Random('IO')
        for _ in range(14):
            x, y, r = rnd.uniform(0, w), rnd.uniform(40, h - 40), rnd.uniform(8, 22)
            d.ellipse([x - r * 1.8, y - r * 1.8, x + r * 1.8, y + r * 1.8], fill=(215, 120, 50)); d.ellipse([x - r, y - r, x + r, y + r], fill=(60, 40, 30))
        return im
    elif code == 'CE':   # gri + parlak tuz lekeleri
        a = np.array((140, 135, 130)) * (0.8 + 0.35 * n)
        im = Image.fromarray(a.clip(0, 255).astype(np.uint8)); d = ImageDraw.Draw(im); rnd = random.Random('CE')
        for _ in range(18):
            x, y, r = rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(8, 24)
            d.ellipse([x - r, y - r, x + r, y + r], outline=(105, 100, 95), width=3)
        d.ellipse([280, 285, 312, 310], fill=(250, 250, 245)); d.ellipse([322, 298, 334, 310], fill=(250, 250, 245))
        return im
    else:  # PL: kalp şekilli buzul (Tombaugh Regio)
        a = np.array((200, 165, 130)) * (0.8 + 0.3 * n)
        im = Image.fromarray(a.clip(0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
        d.ellipse([250, 190, 310, 250], fill=(245, 235, 220)); d.ellipse([295, 190, 355, 250], fill=(245, 235, 220))
        d.polygon([(254, 230), (351, 230), (302, 300)], fill=(245, 235, 220))
        return im
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


@lru_cache(64)
def ball_sprite(code, d, tint=None):
    """Bayrak dokulu, ışıklı top (d piksel, S ölçekli). tint: (r,g,b,alfa) üst renk (ör. üşüme = mavi)."""
    n = L(d)
    fl = flag_img(code)
    fw = int(n * 1.45)
    fl = fl.resize((fw, n), Image.LANCZOS).crop(((fw - n) // 2, 0, (fw - n) // 2 + n, n))
    a = np.asarray(fl, float) / 255
    y, x = np.mgrid[0:n, 0:n].astype(float)
    x = (x + 0.5) / n * 2 - 1; y = (y + 0.5) / n * 2 - 1
    dd = x * x + y * y; z = np.sqrt(np.clip(1 - dd, 0, 1))
    lam = np.clip(x * -0.45 + y * -0.6 + z * 0.66, 0, 1)
    shade = 0.55 + 0.55 * lam
    sp = np.clip(x * -0.3 + y * -0.45 + z * 0.84, 0, 1) ** 45 * 0.55
    rgb = np.clip(a * shade[..., None] + sp[..., None], 0, 1)
    if tint:
        rgb = rgb * (1 - tint[3]) + np.array(tint[:3]) / 255 * tint[3]
    alpha = np.clip((1 - np.sqrt(dd)) * n * 0.5, 0, 1)
    im = Image.fromarray(np.dstack([rgb * 255, alpha * 255]).astype(np.uint8))
    ImageDraw.Draw(im).ellipse([1, 1, n - 2, n - 2], outline=(20, 20, 25, 255), width=max(2, int(n * 0.022)))
    return im


def eyes(img, cx, cy, d, mood, t, look=(0.0, 0.0)):
    dr = ImageDraw.Draw(img)
    ew, eh = d * 0.17, d * 0.21
    big = mood in ('shock', 'shiver')
    if big: ew, eh = d * 0.21, d * 0.26
    lw = max(3, L(d * 0.016))
    for s in (-1, 1):
        ex, ey = cx + s * d * 0.19, cy - d * 0.06
        if mood == 'cool':
            continue
        if mood == 'happy':
            dr.arc(box(ex - ew / 2, ey - eh * 0.2, ex + ew / 2, ey + eh * 0.8), 200, 340, fill=(255, 255, 255), width=L(d * 0.05))
            dr.arc(box(ex - ew / 2 - 3, ey - eh * 0.2 - 3, ex + ew / 2 + 3, ey + eh * 0.8 + 3), 200, 340, fill=(20, 20, 25), width=lw)
            continue
        if mood == 'sleepy':
            dr.line(box(ex - ew / 2, ey + eh * 0.1, ex + ew / 2, ey + eh * 0.1), fill=(20, 20, 25), width=L(d * 0.02))
            continue
        if mood == 'love':   # beyaz kenarlı kalp (kırmızı bayraklarda da görünsün)
            for dx in (-0.22, 0.22):
                put_sphere(img, (255, 255, 255), ex + dx * ew, ey - eh * 0.15, ew * 0.78, ew * 0.78, 0.0)
            dr.polygon([(L(ex - ew * 0.66), L(ey - eh * 0.08)), (L(ex + ew * 0.66), L(ey - eh * 0.08)), (L(ex), L(ey + eh * 0.66))],
                       fill=(255, 255, 255))
            for dx in (-0.22, 0.22):
                put_sphere(img, (235, 45, 75), ex + dx * ew, ey - eh * 0.15, ew * 0.6, ew * 0.6, 0.5)
            dr.polygon([(L(ex - ew * 0.52), L(ey - eh * 0.05)), (L(ex + ew * 0.52), L(ey - eh * 0.05)), (L(ex), L(ey + eh * 0.5))],
                       fill=(235, 45, 75))
            continue
        dr.ellipse(box(ex - ew / 2, ey - eh / 2, ex + ew / 2, ey + eh / 2), fill=(255, 255, 255), outline=(20, 20, 25), width=lw)
        pr = ew * (0.16 if big else 0.28)
        px, py = ex + look[0] * ew * 0.22, ey + look[1] * eh * 0.22
        dr.ellipse(box(px - pr, py - pr, px + pr, py + pr), fill=(20, 20, 25))
        if mood == 'calm':   # yarı kapalı göz kapağı
            dr.chord(box(ex - ew / 2 - 2, ey - eh / 2 - 2, ex + ew / 2 + 2, ey + eh / 2 + 2), 180, 360, fill=(20, 20, 25))
        if mood == 'angry':
            dr.line(box(ex - s * ew * 0.6, ey - eh * 0.75, ex + s * ew * 0.5, ey - eh * 0.4), fill=(20, 20, 25), width=L(d * 0.03))
        if mood == 'cry':
            k = (t * 2) % 1
            put_sphere(img, (110, 180, 250), ex, ey + eh * 0.6 + k * d * 0.25, d * 0.05, d * 0.08, 0.8)
    if mood == 'cool':  # güneş gözlüğü
        dr.rounded_rectangle(box(cx - d * 0.36, cy - d * 0.14, cx + d * 0.36, cy + d * 0.02), radius=L(d * 0.05), fill=(15, 15, 20))
        dr.line(box(cx - d * 0.30, cy - d * 0.10, cx - d * 0.18, cy - d * 0.10), fill=(120, 120, 130), width=L(d * 0.015))


def _ring(img, cx, cy, d, front):
    """Satürn halkası: arka yarı topun önce, ön yarı sonra çizilir."""
    dr = ImageDraw.Draw(img)
    for k, (col, wd) in enumerate((((205, 185, 140), 0.07), ((235, 215, 170), 0.045))):
        rx, ry = d * (0.95 - k * 0.1), d * (0.26 - k * 0.03)
        dr.arc(box(cx - rx, cy - ry, cx + rx, cy + ry), 0 if front else 180, 180 if front else 360, fill=col, width=L(d * wd))


def ball(img, code, cx, cy, d, mood='normal', t=0.0, squash=0.0, look=(0.0, 0.0)):
    put_shadow(img, cx, cy + d * 0.5, d * 0.9, d * 0.16)
    if code == 'SU':   # Güneş parıltısı
        put_sphere(img, (255, 210, 90), cx, cy, d * (0.72 + 0.03 * math.sin(t * 4)), d * (0.72 + 0.03 * math.sin(t * 4)), 0.0)
    if code == 'SA': _ring(img, cx, cy + d * 0.05, d, False)
    tint = (120, 180, 255, 0.25) if mood == 'shiver' else (255, 60, 40, 0.18) if mood == 'angry' else None
    spr = ball_sprite(code, int(d), tint)
    if squash:
        spr = spr.resize((int(spr.width * (1 + squash)), int(spr.height * (1 - squash))), Image.BILINEAR)
    put(img, spr, cx, cy + d * squash * 0.5)
    if code == 'SA': _ring(img, cx, cy + d * 0.05, d, True)
    eyes(img, cx, cy + d * squash * 0.4, d, mood, t, look)
    if mood == 'sleepy':
        for j in range(3):
            u = (t * 0.7 + j / 3) % 1
            put_text(img, 'Z', cx + d * 0.45 + 40 * u, cy - d * 0.5 - 120 * u, 40 + 30 * u, (255, 255, 255), scale=min(1, u * 4) * (1 - u) * 1.6)
    if mood == 'shiver':
        put_text(img, 'BRRR', cx + d * 0.55, cy - d * 0.55, 54, (190, 225, 255), rot=10)


# ---------------------------------------------------------------- konuşma balonu (aksanlı harfler için yedek yazı tipi)
FONT2 = os.path.join(HERE, 'fonts', 'Anton-Regular.ttf')


@lru_cache(None)
def font_for(text, sz):
    f = ImageFont.truetype(FONT, sz)
    notdef = f.getmask('￿').getbbox()
    missing = any(f.getmask(ch).getbbox() == notdef for ch in set(text) if not ch.isspace() and ord(ch) > 127)
    return ImageFont.truetype(FONT2, sz) if missing and os.path.exists(FONT2) else f


def wrap(txt, f, maxw):
    words, lines, cur = txt.split(), [], ''
    for w in words:
        nxt = (cur + ' ' + w).strip()
        if f.getlength(nxt) <= maxw: cur = nxt
        else: lines.append(cur); cur = w
    lines.append(cur)
    return [l for l in lines if l]


def bubble(img, txt, cx, cy, tail_to, k):
    if k <= 0.01: return
    f = font_for(txt, L(74))
    lines = wrap(txt, f, L(860))
    lh = f.getbbox('Ag')[3] + L(10)
    tw = max(f.getlength(l) for l in lines); th = lh * len(lines)
    pad = L(40)
    layer = Image.new('RGBA', (int(tw + 2 * pad + L(20)), int(th + 2 * pad + L(70))), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([L(6), L(6), tw + 2 * pad, th + 2 * pad], radius=L(44), fill=(255, 255, 255), outline=(20, 20, 25), width=L(6))
    bx = (tw + 2 * pad) / 2
    d.polygon([(bx - L(40), th + 2 * pad - L(4)), (bx + L(40), th + 2 * pad - L(4)), (bx + L(10) * (1 if tail_to >= 0 else -1), th + 2 * pad + L(60))],
              fill=(255, 255, 255), outline=(20, 20, 25))
    d.rectangle([bx - L(36), th + 2 * pad - L(12), bx + L(36), th + 2 * pad - L(2)], fill=(255, 255, 255))
    for i, ln in enumerate(lines):
        d.text(((tw + 2 * pad) / 2 - f.getlength(ln) / 2 + L(4), pad + i * lh), ln, font=f, fill=(25, 25, 30))
    s = back(k)
    lay = layer.resize((max(1, int(layer.width * s)), max(1, int(layer.height * s))), Image.BILINEAR)
    img.paste(lay, (int(L(cx) - lay.width / 2), int(L(cy) - lay.height)), lay)

rng = np.random.default_rng(1)
def t_arr(d): return np.arange(int(SR * d)) / SR
def noise(d): return rng.uniform(-1, 1, int(SR * d))
def dec(d, k): return np.exp(-t_arr(d) * k)
def lpf(x, k): return np.convolve(x, np.ones(k) / k, mode='same') if k > 1 else x
def bell(d, p=1.0): return np.sin(np.linspace(0, np.pi, int(SR * d))) ** p
def osc(freq, shape='sine'):
    ph = 2 * np.pi * np.cumsum(freq) / SR
    if shape == 'saw': return 2 * ((ph / (2 * np.pi)) % 1) - 1
    return np.sin(ph)
def sweep(f0, f1, d, shape='sine'): return osc(np.geomspace(f0, f1, int(SR * d)), shape)


def sfx(name, dur=None):
    if name == 'pop': x, g = sweep(900, 240, 0.09) * dec(0.09, 35), 0.6
    elif name == 'crunch':
        n = noise(0.18); m = (rng.uniform(0, 1, len(n) // 220 + 1) > 0.45).repeat(220)[:len(n)]
        x, g = lpf(n, 2) * m * dec(0.18, 14), 0.55
    elif name == 'gulp': x, g = sweep(420, 140, 0.16) * bell(0.16), 0.7
    elif name == 'burp':
        s = sweep(95, 70, 0.7, 'saw') * (1 + 0.5 * noise(0.7)); x, g = lpf(s, 18) * bell(0.7, 0.5), 1.0
    elif name == 'ring':
        tt = t_arr(dur); x = (np.sin(2 * np.pi * 1750 * tt) + 0.6 * np.sin(2 * np.pi * 2630 * tt)) * (np.sin(2 * np.pi * 22 * tt) > 0); g = 0.22
    elif name == 'ring_weak':
        x = osc(np.linspace(1500, 1000, int(SR * 0.3))) * (np.sin(2 * np.pi * 18 * t_arr(0.3)) > 0) * dec(0.3, 5); g = 0.12
    elif name == 'click': x, g = np.diff(noise(0.02), prepend=0) * dec(0.02, 200), 0.5
    elif name in ('smash', 'bonk'):
        d = 0.6 if name == 'smash' else 0.35
        th = sweep(110 if name == 'smash' else 160, 40, d) * dec(d, 6)
        nz = lpf(noise(d), 3) * dec(d, 9)
        cl = sum(np.sin(2 * np.pi * f * t_arr(d)) * dec(d, k) for f, k in ((523, 7), (787, 9), (1187, 11)))
        x, g = th + 0.7 * nz + 0.25 * cl, 1.0 if name == 'smash' else 0.85
    elif name in ('whoosh', 'whoosh_s'):
        d = 0.4 if name == 'whoosh' else 0.22; x = lpf(noise(d), 10) * bell(d, 2); g = 0.6 if name == 'whoosh' else 0.3
    elif name == 'squirt': x, g = lpf(noise(0.2), 5) * dec(0.2, 10) + 0.3 * sweep(700, 250, 0.2) * dec(0.2, 15), 0.5
    elif name == 'slurp':
        tt = t_arr(dur); n = lpf(noise(dur), 6) * (0.6 + 0.4 * np.sin(2 * np.pi * 8 * tt))
        s = osc(220 + 70 * np.sin(2 * np.pi * 6 * tt)); x, g = (n * 1.5 + 0.35 * s) * bell(dur, 0.3), 0.55
    elif name == 'ahh':
        tt = t_arr(0.8); f = 170 * (1 - 0.15 * tt / 0.8) + 4 * np.sin(2 * np.pi * 5.5 * tt)
        x, g = lpf(osc(f, 'saw'), 9) * bell(0.8, 0.4), 0.7
    elif name == 'inhale': x, g = lpf(noise(dur), 4) * np.linspace(0, 1, int(SR * dur)) ** 2, 0.6
    elif name == 'blow': x, g = lpf(noise(dur), 12) * bell(dur, 0.5), 0.8
    elif name == 'splat': x, g = sweep(80, 40, 0.5) * dec(0.5, 8) + 3 * lpf(noise(0.5), 20) * dec(0.5, 10), 1.0
    elif name == 'horn':
        tt = t_arr(0.55); x, g = lpf(osc(520 + 30 * np.sin(2 * np.pi * 6 * tt), 'saw'), 5) * bell(0.55, 0.3), 0.3
    elif name == 'clap': x, g = np.diff(noise(0.08), prepend=0) * dec(0.08, 60), 0.45
    elif name == 'sting':
        x = lpf(osc(np.full(int(SR * 0.9), 110.0), 'saw') + osc(np.full(int(SR * 0.9), 55.6), 'saw'), 6) * dec(0.9, 3.5)
        x += 0.5 * np.sin(2 * np.pi * 55 * t_arr(0.9)) * dec(0.9, 3); g = 0.55
    elif name == 'ding':
        x = np.sin(2 * np.pi * 1320 * t_arr(0.9)) * dec(0.9, 5) + 0.4 * np.sin(2 * np.pi * 2640 * t_arr(0.9)) * dec(0.9, 8); g = 0.35
    elif name == 'boing':
        tt = t_arr(0.5); x, g = osc(180 + 300 * tt + 40 * np.sin(2 * np.pi * 18 * tt)) * dec(0.5, 5), 0.4
    elif name == 'yawn':
        tt = t_arr(0.9); f = np.linspace(330, 190, len(tt)) + 6 * np.sin(2 * np.pi * 5 * tt)
        x, g = (osc(f) + 0.3 * lpf(noise(0.9), 8)) * bell(0.9, 0.6), 0.3
    elif name == 'psst': x, g = np.diff(noise(0.25), prepend=0) * dec(0.25, 9), 0.4
    elif name == 'fizz': x, g = np.diff(noise(dur), prepend=0) * (rng.uniform(0, 1, int(SR * dur)) > 0.6) * dec(dur, 1.5), 0.45
    elif name == 'rattle':
        tt = t_arr(dur); x, g = lpf(noise(dur), 3) * (np.sin(2 * np.pi * 15 * tt) > 0.3), 0.45
    elif name == 'lick': x, g = lpf(noise(0.14), 4) * bell(0.14) + 0.4 * sweep(300, 700, 0.14) * bell(0.14), 0.45
    elif name == 'freeze':
        tt = t_arr(1.2); x = sum(np.sin(2 * np.pi * f * (1 - 0.25 * tt / 1.2) * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * (9 + j) * tt))
                                for j, f in enumerate((2100, 2650, 3150, 3700))) * dec(1.2, 2); g = 0.3
    elif name == 'bang': x, g = sweep(150, 40, 0.4) * dec(0.4, 8) + lpf(noise(0.4), 2) * dec(0.4, 14), 1.0
    elif name == 'carve':
        tt = t_arr(0.28); x, g = lpf(noise(0.28), 3) * (0.6 + 0.4 * np.sin(2 * np.pi * 30 * tt)) * bell(0.28), 0.4
    else: raise ValueError(name)
    return x / (np.abs(x).max() + 1e-9) * g


def music(dur, seed):
    rnd = random.Random(seed)
    bpm = rnd.choice([116, 120, 124, 128, 132]); beat = 60 / bpm; key = rnd.randint(-3, 3)
    out = np.zeros(int(SR * dur) + SR)
    def mf(m): return 440 * 2 ** ((m + key - 69) / 12)
    def pluck(f, d, k, bright):
        tt = t_arr(d); return (np.sin(2 * np.pi * f * tt) + bright * np.sin(4 * np.pi * f * tt) + 0.12 * np.sin(6 * np.pi * f * tt)) * np.exp(-tt * k)
    def add(t0, x):
        i0 = int(t0 * SR); out[i0:i0 + len(x)] += x[:max(0, len(out) - i0)]
    prog = rnd.choice([[48, 45, 41, 43], [48, 43, 45, 41], [45, 41, 48, 43], [48, 41, 43, 48]])
    penta = [60, 62, 64, 67, 69, 72, 74, 76]; bright = rnd.uniform(0.2, 0.5)
    motif = [None if rnd.random() < 0.3 else rnd.choice(penta) for _ in range(16)]
    motif2 = [m if (m is None or rnd.random() < 0.6) else rnd.choice(penta) for m in motif]
    for b in range(int(dur / beat) + 1):
        t0 = b * beat; bar = b // 4; root = prog[bar % 4]
        add(t0, 0.9 * pluck(mf(root if b % 2 == 0 else root + 7), 0.35, 7, 0.35))
        if b % 2 == 0: add(t0, 0.8 * sweep(130, 45, 0.18) * dec(0.18, 18))
        else: add(t0, 0.25 * lpf(noise(0.12), 2) * dec(0.12, 30))
        add(t0 + beat / 2, 0.12 * np.diff(noise(0.03), prepend=0) * dec(0.03, 120))
        mot = motif if (bar // 2) % 2 == 0 else motif2
        for h in (0, 1):
            n = mot[(b * 2 + h) % 16]
            if n is not None: add(t0 + h * beat / 2, 0.32 * pluck(mf(n), 0.25, 11, bright))
    out = out[:int(SR * dur)]
    out *= np.clip((dur - t_arr(dur)) / 0.6, 0, 1)
    return out / np.abs(out).max() * 0.22




# ---------------------------------------------------------------- zaman çizelgesi
STAGE = (540, 1010)
BIG = 500
SLOTS4 = [(170, 1660), (400, 1660), (680, 1660), (910, 1660)]
FINAL4 = [(300, 830), (780, 830), (300, 1330), (780, 1330)]


def total(plan=None):
    return INTRO + TURN * len((plan or PLAN)['countries']) + OUTRO


def turn_pose(k, lt, code, mood):
    """k. ülkenin sahnedeki konumu/ölçüsü (lt: tur içi saniye)."""
    if lt < 0.55:   # sağdan zıplayarak gelir
        u = sm(lt / 0.55)
        x = lerp(1300, STAGE[0], u); y = STAGE[1] - 260 * math.sin(math.pi * u)
        return x, y, BIG, 0.0
    if lt < TURN - 0.6:
        tt = lt - 0.55
        sq = 0.08 * abs(math.sin(tt * 6)) if mood in ('happy', 'love') else 0.0
        jit = 7 * math.sin(lt * 60) if mood == 'shiver' else (5 * math.sin(lt * 45) if mood == 'angry' else 0.0)
        hop = 120 * abs(math.sin(tt * 4.5)) if mood in ('shock', 'happy') and tt < 1.4 else 0.0
        sway = 25 * math.sin(tt * 2) if mood in ('calm', 'sleepy', 'cool') else 0.0
        return STAGE[0] + jit + sway, STAGE[1] - hop, BIG, sq
    u = sm((lt - (TURN - 0.6)) / 0.6)   # sıraya geçer
    sx, sy = SLOTS4[k]
    return lerp(STAGE[0], sx, u), lerp(STAGE[1], sy, u), lerp(BIG, 190, u), 0.0


def title_band(img, txt, t, t0):
    k = back(seg(t, t0, t0 + 0.3))
    f = font(L(84)); lines = wrap(txt, f, L(980))
    for i, ln in enumerate(lines):
        put_text(img, ln, W / 2, 150 + i * 95, 84, (255, 230, 60) if i == len(lines) - 1 else (255, 255, 255), scale=k)


def name_tag(img, name, x, y, k=1.0, size=60):
    put_text(img, name, x, y, size, (255, 255, 255), scale=k)


def render_frame(i):
    T = i / FPS
    sit = SITUATIONS[PLAN['situation']]
    codes = PLAN['countries']; n = len(codes)
    img = scene_bg(PLAN.get('scene') or sit['scene']).copy()
    effects(img, PLAN.get('scene') or sit['scene'], T)
    # koyu üst bant (başlık okunsun)
    band = Image.new('RGBA', (L(W), L(330)), (20, 18, 35, 170)); img.alpha_composite(band, (0, 0))
    title_band(img, sit['title'], T, 0.0)
    end = INTRO + TURN * n
    if T < INTRO:
        put_text(img, 'ORBIT SQUAD', W / 2, 900, 110, (255, 255, 255), scale=back(seg(T, 0.35, 0.7)), rot=-4)
        put_text(img, 'REAL SPACE FACTS!', W / 2, 1040, 80, (255, 230, 60), scale=back(seg(T, 0.6, 0.95)), rot=3)
    elif T < end:
        k = int((T - INTRO) // TURN); lt = T - INTRO - k * TURN
        for j in range(k):   # sıradakiler
            sx, sy = SLOTS4[j]
            ball(img, codes[j], sx, sy, 190, sit['lines'][codes[j]][1], T, look=(0.6 if sx < STAGE[0] else -0.6, -0.5))
        code = codes[k]; line, mood = sit['lines'][code]
        x, y, d, sq = turn_pose(k, lt, code, mood)
        lv = speech_levels(str(PLAN.get('seed')) + PLAN['situation'] + ','.join(codes))
        sq += 0.07 * float(lv[min(len(lv) - 1, i)])   # konuşurken sese göre esner
        ball(img, code, x, y, d, mood if lt >= 0.45 else 'normal', T, sq, look=(0, 0))
        if 0.45 <= lt < TURN - 0.55:
            bubble(img, line, STAGE[0], 690, 0, seg(lt, 0.45, 0.7) * (1 - seg(lt, TURN - 0.75, TURN - 0.55)))
            name_tag(img, NAMES[code], STAGE[0], 1330, back(seg(lt, 0.5, 0.75)), 76)
    else:
        lt = T - end
        for j, code in enumerate(codes):
            sx, sy = SLOTS4[j]; fx, fy = FINAL4[j]
            u = sm(seg(lt, 0.0, 0.6))
            x, y, d = lerp(sx, fx, u), lerp(sy, fy, u), lerp(190, 330, u)
            y -= 40 * abs(math.sin(lt * 5 + j)) * u
            ball(img, code, x, y, d, 'happy', T)
            if u > 0.9: name_tag(img, NAMES[code], x, y + d * 0.68, 1.0, 50)
        s = back(seg(lt, 0.4, 0.75)) * (1 + 0.04 * math.sin(lt * 7))
        put_text(img, 'WHICH ONE', W / 2, 1640, 96, (255, 255, 255), scale=s, rot=-3)
        put_text(img, 'ARE YOU?', W / 2, 1760, 110, (255, 230, 60), scale=s, rot=3)
    return img.convert('RGB').reduce(S)


@lru_cache(2)
def _first_frame(key):
    return render_frame(0)


def render_frame_loop(i):
    """Shorts başa sarar: son 0.45 sn ilk kareye karışır (kesintisiz döngü)."""
    T = i / FPS; tot = total(); f = render_frame(i)
    if T > tot - 0.45:
        f = Image.blend(f, _first_frame(str(PLAN.get('seed'))), seg(T, tot - 0.45, tot))
    return f


def _frame_bytes(i): return render_frame_loop(i).tobytes()


# ---------------------------------------------------------------- ses
@lru_cache(None)
def load_clip(f):
    with wave.open(f) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
        sr = w.getframerate()
    if sr != SR:
        x = np.interp(np.arange(0, len(x), sr / SR), np.arange(len(x)), x)
    nz = np.nonzero(np.abs(x) > 0.02)[0]
    return x[max(0, nz[0] - 200):nz[-1] + 800] if len(nz) else None


MOOD_KIND = {'happy': 'yay', 'love': 'yay', 'shock': 'yell', 'shiver': 'yell', 'cry': 'yell', 'angry': 'yell',
             'cool': 'hm', 'calm': 'hm', 'sleepy': 'hm', 'normal': 'hm'}


def exclaim(code, mood, seed):
    """Ülkeye özgü perde + duruma uygun anime ünlemi (kütüphane: voices/zephyr_ex, voices/puck_ex)."""
    lib = 'zephyr_ex' if sum(map(ord, code)) % 2 else 'puck_ex'
    kind = MOOD_KIND.get(mood, 'hm')
    files = sorted(glob.glob(os.path.join(HERE, 'voices', lib, f'{kind}_*.wav'))) or \
        sorted(glob.glob(os.path.join(HERE, 'voices', lib, '*.wav')))
    if not files: return None
    x = load_clip(files[random.Random(f'{seed}{code}').randrange(len(files))])
    if x is None: return None
    r = 0.9 + (sum(map(ord, code)) % 9) * 0.04   # ülke başına perde
    x = np.interp(np.arange(0, len(x) - 1, r), np.arange(len(x)), x)
    return x / (np.abs(x).max() + 1e-9) * 0.7


def line_clip(sit, code):
    """Ülkenin bu durumdaki repliği (kendi aksanıyla): voices/cw/<ÜLKE>/<durum>.wav; yoksa None → anime ünlemi."""
    f = os.path.join(HERE, 'voices', 'os', code, f'{sit}.wav')
    x = load_clip(f) if os.path.exists(f) else None
    if x is None: return None
    x = x[:int(SR * (TURN - 1.1))]
    return x / (np.abs(x).max() + 1e-9) * 0.85


@lru_cache(4)
def speech_levels(key):
    """Konuşan topun kare başına ses seviyesi (konuşurken zıplar)."""
    sit = PLAN['situation']; nf = int(total() * FPS) + 2; lv = np.zeros(nf); hop = SR // FPS
    for k, code in enumerate(PLAN['countries']):
        x = line_clip(sit, code)
        if x is None: continue
        m = len(x) // hop
        rms = np.sqrt((x[:m * hop].reshape(m, hop) ** 2).mean(axis=1))
        i0 = int((INTRO + k * TURN + 0.5) * FPS); seg_ = lv[i0:i0 + m]; seg_ += rms[:len(seg_)]
    return lv / (lv.max() + 1e-9)


def ambience(kind, dur):
    tt = t_arr(dur)
    if kind == 'rain': return lpf(noise(dur), 2) * 0.12
    if kind == 'snow': return lpf(noise(dur), 40) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.2 * tt)) * 0.18
    if kind == 'stadium': return lpf(noise(dur), 12) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.5 * tt)) * 0.22
    if kind == 'party': return lpf(noise(dur), 20) * 0.06
    # uzay uğultusu: alçak, yavaş dalgalanan
    return (lpf(noise(dur), 80) * 0.5 + 0.02 * np.sin(2 * np.pi * 55 * tt)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.15 * tt)) * 0.25


def build_audio(path):
    tot = total(); n = int(SR * tot); mus = music(tot, PLAN['seed'])
    sit = SITUATIONS[PLAN['situation']]
    mix = np.zeros(n); vo = np.zeros(n)
    def place(arr, t0, x):
        if x is None: return
        i0 = int(t0 * SR); arr[i0:i0 + len(x)] += x[:max(0, n - i0)]
    place(mix, 0.0, ambience(PLAN.get('scene') or sit['scene'], tot))
    for t0 in (0.0, 0.4, 0.7): place(mix, t0, sfx('pop'))
    for k, code in enumerate(PLAN['countries']):
        base = INTRO + k * TURN; mood = sit['lines'][code][1]
        place(mix, base, sfx('whoosh_s')); place(mix, base + 0.5, sfx('boing'))
        ln = line_clip(PLAN['situation'], code)
        place(vo, base + 0.5, ln if ln is not None else exclaim(code, mood, PLAN['seed'] + k))
        place(mix, base + TURN - 0.6, sfx('whoosh_s'))
    end = INTRO + TURN * len(PLAN['countries'])
    place(mix, end, sfx('ding')); place(mix, end + 0.4, sfx('clap')); place(mix, end + 0.55, sfx('clap'))
    env = np.convolve(np.abs(vo), np.ones(int(SR * 0.25)) / int(SR * 0.25), mode='same')
    duck = 1 - 0.6 * np.clip(env / (env.max() + 1e-9) * 4, 0, 1)
    mix = mus[:n] * duck + mix + vo
    mix *= np.clip((tot - t_arr(tot)[:n]) / 0.25, 0, 1)
    mix = mix / np.abs(mix).max() * 0.92
    pcm = (np.repeat(mix[:, None], 2, axis=1) * 32767).astype(np.int16)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


# ---------------------------------------------------------------- video
def render_video(plan, out_dir, workers=None):
    configure(plan)
    os.makedirs(out_dir, exist_ok=True)
    wav = os.path.join(out_dir, 'audio.wav'); mp4 = os.path.join(out_dir, 'video.mp4')
    build_audio(wav)
    nf = int(total() * FPS)
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', wav, '-c:v', 'libx264', '-preset', 'medium',
           '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', mp4]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(workers or os.cpu_count(), initializer=configure, initargs=(plan,)) as pool:
        for i, buf in enumerate(pool.imap(_frame_bytes, range(nf), chunksize=6)):
            p.stdin.write(buf)
            if i % 150 == 0: print(f'  frame {i}/{nf}', flush=True)
    p.stdin.close()
    if p.wait() != 0: raise RuntimeError('ffmpeg failed')
    os.remove(wav)
    return mp4


def _arg(name, default):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


if __name__ == '__main__':
    plan = dict(situation=_arg('--sit', 'snow'), countries=_arg('--countries', 'CA,BR,TR,JP').split(','), seed=1)
    out = os.path.join(HERE, 'output', 'preview')
    if '--preview' in sys.argv:
        configure(plan); os.makedirs(out, exist_ok=True)
        for s in _arg('--preview', '3').split(','):
            render_frame(int(float(s) * FPS)).save(os.path.join(out, f'p_{s}.png'))
        print('preview ok')
    else:
        print(render_video(plan, out))
