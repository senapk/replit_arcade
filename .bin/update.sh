#!/bin/bash

# baixando tk
tk=~/arcade/.bin/tk.py
rm -f $tk
wget https://raw.githubusercontent.com/senapk/tk/master/tk.py -O $tk
chmod +x $tk

# baixando aux

aux=~/arcade/.include/aux.hpp
rm -f $aux
wget https://raw.githubusercontent.com/senapk/cppaux/master/aux.hpp -O $aux

md=~/arcade/Readme.md
rm -f $rm
wget https://raw.githubusercontent.com/senapk/indexer/master/runner.md -O $md