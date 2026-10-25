"""Bir Short üret ve yükle: durum + 4 ülke seç (tekrar etmez) -> render -> YouTube -> history.json.

  python run.py --no-upload
"""
import json, os, random, re, sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import orbit as balls  # noqa: E402

HISTORY = HERE / 'history.json'
# en çok aranan/izlenen gök cisimleri daha sık (2026-10-13 trend: solarballs medyan 237K, "what if earth" 189K)
WEIGHT = {'EA': 3, 'SA': 2.5, 'JU': 2.5, 'MA': 2.5, 'SU': 2, 'PL': 2, 'MO': 2, 'VE': 1.5, 'NE': 1.5, 'UR': 1.5, 'ME': 1.2,
          'TI': 1.3, 'EU': 1.3, 'IO': 1.3, 'CE': 1.1}
TITLES = ['{t} 🪐 #space', '{t} 😂 #planets', '{t} 🌍 #solarsystem', 'Solar System Facts: {s} 🚀',
          '{t} (Real Space Facts!) 🪐', 'POV: {t} 😂 #space']


def load():
    return json.loads(HISTORY.read_text()) if HISTORY.exists() else {'videos': []}


def voiced(sit):
    """Bu durumda kendi aksanlı sesi hazır olan ülkeler (voices/cw/<ÜLKE>/<durum>.wav)."""
    return [c for c in balls.SITUATIONS[sit]['lines'] if (HERE / 'voices' / 'os' / c / f'{sit}.wav').exists()]


def tkey(t):
    """Başlık karşılaştırma anahtarı: emoji/etiket/parantez/noktalama/POV önekleri atılır."""
    t = re.sub(r'#\w+|\(.*?\)', ' ', t.lower())
    t = re.sub(r'^(pov|solar system facts)\s*:\s*', '', re.sub(r'[^a-z0-9: ]', ' ', t).strip())
    return ' '.join(re.sub(r'[^a-z0-9 ]', ' ', t).replace('planets ', '', 1).split())


def short_sits(hist):
    """Shorts'ta (eski kayıtlarda kind yok) en az bir kez kullanılmış durumlar."""
    return {v.get('situation') for v in hist['videos'] if v.get('kind', 'short') == 'short'}


def pick_plan(hist, rnd, mode='short'):
    """Sadece 4 cismin de konuştuğu planlar (sessiz video yok).
    2026-10-25: tekrar eden Shorts YouTube'da dağıtılmıyor (tekrar medyan 450 vs yeni 1,181) →
    mode='short': her durum Shorts'ta yalnız BİR kez; yeni durum yoksa None → slot atlanır (yeni durum + ses eklenir).
    mode='episode': uzun bölüm = Shorts'ta işlenmiş konuların derlemesi (yeni Shorts havuzunu tüketmez); aynı dörtlü asla tekrar etmez."""
    from itertools import combinations
    used = short_sits(hist)
    cands = []
    for sit in balls.SITUATIONS:
        if (sit in used) == (mode == 'short'):
            continue
        vs = voiced(sit)
        seen = {tuple(sorted(v.get('countries', []))) for v in hist['videos'] if v.get('situation') == sit}
        combos = [c for c in combinations(vs, 4) if tuple(sorted(c)) not in seen
                  and len({balls.SITUATIONS[sit]['lines'][x][1] for x in c}) >= 3]   # tepkiler çeşitli olsun
        if combos:
            cands.append((sit, combos))
    if not cands:
        return None
    sit, combos = rnd.choice(cands)
    cs = list(rnd.choices(combos, weights=[sum(WEIGHT.get(x, 1) for x in c) for c in combos])[0])
    rnd.shuffle(cs)
    # ortam: durumun kendi sahnesi ya da yeni ortamlardan biri; son 3 Short'un ortamı tekrar etmez
    recent = [v.get('scene') or balls.SITUATIONS.get(v.get('situation'), {}).get('scene') for v in hist['videos'][-3:]]
    own = balls.SITUATIONS[sit]['scene']
    pool = [k for k in balls.SCENES if k not in recent] or list(balls.SCENES)
    scene = rnd.choices(pool, weights=[3 if k == own else 1 for k in pool])[0]
    return dict(situation=sit, countries=cs, scene=scene, seed=rnd.randrange(10 ** 6))


def metadata(plan, hist, rnd):
    s = balls.SITUATIONS[plan['situation']]
    t = ' '.join(re.sub(r'[A-Za-z]', lambda m: m.group().upper(), w.lower(), count=1) for w in s['title'].split()).replace('°c', '°C')
    used = {tkey(v['title']) for v in hist['videos'] if v.get('title')}
    short_s = t.replace('Planets: ', '', 1).replace('Planets ', '', 1)
    opts = [x.format(t=t, s=short_s) for x in TITLES]; rnd.shuffle(opts)
    title = next((x for x in opts if tkey(x) not in used), None)
    if title is None:   # aynı konu başlığı zaten var → yeniden yükleme yok
        return None, None, None
    names = [balls.NAMES[c].title() for c in plan['countries']]
    lines = '\n'.join(f'{balls.NAMES[c].title()}: "{s["lines"][c][0]}"' for c in plan['countries'])
    desc = (f'{t}! Which one are YOU? Comment below 👇\n\n{lines}\n\n'
            'Every line is a real space fact (rounded numbers, based on NASA planetary data), told by the Orbit Squad. '
            'New space Shorts every day 🪐\n\n#shorts #space #planets #solarsystem #animation')
    tags = ['space', 'planets', 'solar system', 'space facts', 'planet facts', 'solarsystem animation', 'planets for fun',
            'astronomy', s['name'].lower(), 'animation', 'shorts'] + [n.lower() for n in names]
    return title, desc, tags


def social(mp4, title, vid):
    """Short → social/ (artifact 'social-<run>'): fenek-shorts sosyal yayıncısı Instagram/TikTok'a koyar."""
    import re, shutil
    soc = HERE / 'social'
    soc.mkdir(exist_ok=True)
    shutil.copy(mp4, soc / 'video.mp4')
    clean = re.sub(r'\s*#\w+', '', title).strip()
    tiktok = f"{clean}\nWhich planet are you? 👇\n\n#space #planets #solarsystem #animation #funny #fyp"
    insta = f"{clean}\n\nWhich planet are you? 👇 Follow for daily episodes\n\n#space #planets #solarsystem #animation #funny"  # Instagram: en fazla 5 etiket
    (soc / 'post.json').write_text(json.dumps({'channel': 'Orbit Squad', 'title': clean, 'url': f'https://youtube.com/shorts/{vid}',
                                               'tiktok': tiktok, 'instagram': insta}, ensure_ascii=False, indent=1),
                                   encoding='utf-8')


def main():
    no_upload = '--no-upload' in sys.argv
    hist = load(); rnd = random.Random()
    plan = pick_plan(hist, rnd)
    if plan is None:
        print('Sesli yeni plan kalmadı → bu slot atlandı (yeni ses klipleri gerekiyor)'); return
    title, desc, tags = metadata(plan, hist, rnd)
    if title is None:
        print(f"'{plan['situation']}' başlığı zaten kullanılmış → slot atlandı"); return
    key = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    print(f'plan: {plan}\ntitle: {title}', flush=True)
    out = HERE / 'output' / key
    mp4 = balls.render_video(plan, str(out))
    (out / 'meta.json').write_text(json.dumps(dict(plan=plan, title=title, description=desc, tags=tags), indent=2))
    if no_upload:
        print('render ok (yükleme yok):', mp4); return
    import upload
    if not upload.configured():
        sys.exit('YouTube secrets yok')
    print('kanal:', upload.check_channel())
    privacy = os.environ.get('YT_PRIVACY') or 'private'
    vid = upload.upload(mp4, title, desc, tags, privacy, category='28')
    print(f'yüklendi: https://youtube.com/shorts/{vid} ({privacy})')
    pl = HERE / 'playlists.json'
    if pl.exists() and json.loads(pl.read_text()).get('all'):
        try: upload.add_to_playlist(json.loads(pl.read_text())['all'], vid)
        except Exception as e: print('playlist:', e)
    hist['videos'].append(dict(id=vid, date=datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M'), kind='short',
                               title=title, privacy=privacy, **plan))
    HISTORY.write_text(json.dumps(hist, indent=2, ensure_ascii=False) + '\n')
    if privacy == 'public':
        social(mp4, title, vid)


if __name__ == '__main__':
    main()
