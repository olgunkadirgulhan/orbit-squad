

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
