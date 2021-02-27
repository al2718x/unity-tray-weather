#!/bin/bash

xterm -fa 'Monospace' -fs 10 -geometry 125x40 -e "curl wttr.in/Tokyo?lang=en; read line"

exit 0

