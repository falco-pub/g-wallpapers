#!/usr/bin/python3

import subprocess, shlex

cl = 'gsettings set org.cinnamon.desktop.background picture-uri file:///usr/share/antergos/wallpapers/early_morning_by_kylekc.jpg'
args = shlex.split(cl)

print(args)
subprocess.Popen(args)


