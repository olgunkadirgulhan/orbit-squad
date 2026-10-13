

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
