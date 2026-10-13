

# ---------------------------------------------------------------- uzay sahneleri (kodla çizilir)
def vgrad(w, h, c1, c2):
    t = np.linspace(0, 1, h)[:, None, None]
    return (np.array(c1, float) * (1 - t) + np.array(c2, float) * t) * np.ones((1, w, 1))


SKY = {'space': ((6, 8, 28), (22, 24, 64)), 'nebula': ((24, 8, 44), (70, 30, 96)), 'sunlit': ((20, 14, 40), (90, 44, 60)),
       'ice': ((6, 18, 40), (30, 70, 110)), 'party': ((26, 8, 34), (80, 30, 50))}
GROUND = {'space': (92, 90, 104), 'nebula': (110, 92, 120), 'sunlit': (150, 110, 90), 'ice': (170, 200, 220), 'party': (90, 70, 100)}


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
    if kind == 'sunlit':   # köşede dev güneş ışığı
        glow = Image.new('RGBA', (w, h), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
        for k, al in ((620, 40), (460, 70), (320, 120)):
            gd.ellipse(box(-k + 120, 380 - k, k + 120, 380 + k), fill=(255, 190, 80, al))
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(L(40))))
    # kraterli küçük gezegen zemini (karakterler üstünde durur)
    gc = GROUND.get(kind, GROUND['space'])
    d.ellipse([-L(400), gy - L(60), w + L(400), gy + L(1400)], fill=gc)
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
