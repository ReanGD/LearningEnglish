#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import os.path
import subprocess
import src.app
import src.singleton


def run():
	src.singleton.SingleInstance()
	os.chdir(os.path.dirname(os.path.abspath(__file__)))
	src.app.App()

if __name__ == "__main__":
	if "-new" not in sys.argv:
		subprocess.Popen([sys.executable] + sys.argv + ["-new"])
	else:
		run()
