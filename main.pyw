#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import os.path


def run_new_process():
    import subprocess
    subprocess.Popen([sys.executable] + sys.argv + ["-new"])


def run_statistic():
    import src.statistic_dialog
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    src.statistic_dialog.run_exclusive()


def run_import_lingueleo():
    import src.import_dict
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    src.import_dict.ImportDict().import_dict("lingualeo.txt", "lingualeo")


def run_main():
    import src.singleton
    si = src.singleton.SingleInstance()
    si

    import src.app
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    src.app.App()

if __name__ == "__main__":
    if "-new" not in sys.argv:
        run_new_process()
    elif "-stat" in sys.argv:
        run_statistic()
    elif "-lingualeo" in sys.argv:
        run_import_lingueleo()
    else:
        run_main()
