#!/bin/bash

tk=~/arcade/.bin/tk.py
rm -f $tk
wget https://raw.githubusercontent.com/senapk/tk/master/tk.py -O $tk
chmod +x $tk

runner=~/arcade/.bin/runner.py
rm -f  $runner
wget https://raw.githubusercontent.com/senapk/indexer/master/runner.py -O $runner
chmod +x $runner

mkdir ~/include

aux=~/include/aux.hpp
rm -f $aux
wget https://raw.githubusercontent.com/senapk/cppaux/master/aux.hpp -O $aux
