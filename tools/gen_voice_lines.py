"""src/bank.py → voice_lines.py (gecmiste-sen/tools/voice_lib.py bunu GitHub API'den okur; gök cismi başına 1 Gemini isteği)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import orbit as balls

VOICE = {  # gök cismi → (Gemini sesi, karakter tarifi) — kişilik tutarlı kalsın diye sabit
    'SU': ('Fenrir', 'a booming, proud and warm'), 'ME': ('Puck', 'a hyper, fast-talking'),
    'VE': ('Kore', 'a dramatic, fiery diva'), 'EA': ('Achird', 'a friendly, upbeat'),
    'MO': ('Leda', 'a calm, gentle'), 'MA': ('Algenib', 'a tough, sporty'),
    'JU': ('Charon', 'a deep-voiced, confident'), 'SA': ('Aoede', 'a glamorous, cheerful'),
    'UR': ('Orus', 'a laid-back, sleepy'), 'NE': ('Iapetus', 'a cool, mysterious'),
    'PL': ('Zephyr', 'a small but brave'),
    'TI': ('Enceladus', 'a dreamy, mysterious'), 'EU': ('Vindemiatrix', 'a gentle, curious'),
    'IO': ('Sadachbia', 'a hyper, fiery'), 'CE': ('Zubenelgenubi', 'a humble, cheerful'),
}
lines = {}
for sit, s in balls.SITUATIONS.items():
    for code, (txt, mood) in s['lines'].items():
        lines.setdefault(code, {})[sit] = (txt, mood)
out = os.path.join(balls.HERE, 'voice_lines.py')
with open(out, 'w', encoding='utf-8') as f:
    f.write('"""ÜRETİLDİ: tools/gen_voice_lines.py (kaynak src/bank.py). Ses: voices/os/<GÖK_CİSMİ>/<durum>.wav"""\n')
    f.write(f'VOICE = {json.dumps(VOICE, ensure_ascii=False, indent=1)}\n')
    f.write(f'LINES = {json.dumps(lines, ensure_ascii=False, indent=1)}\n')
print({k: len(v) for k, v in lines.items()})
