#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path
import src.singleton
import src.app


def run():
	src.singleton.SingleInstance()
	os.chdir(os.path.dirname(os.path.abspath(__file__)))
	src.app.App()

if __name__ == "__main__":
	run()
