#!/bin/sh
# orbit.py = src/ parçalarının birleşimi (yardımcılar ve ses Bloop Bonkers motorundan). Düzenleme src/ içinde yapılır.
cd "$(dirname "$0")" && cat src/head.py src/helpers.py src/bank.py src/scene.py > orbit.py && echo "" >> orbit.py && cat src/audio.py src/tail.py >> orbit.py
