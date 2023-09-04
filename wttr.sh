#!/bin/bash

xterm -fa 'Monospace' -fs 10 -geometry "$1" -e "curl --max-time 5 wttr.in/$2; read line"

exit 0