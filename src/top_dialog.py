# -*- coding: utf-8 -*-

import Tkinter


class TopDialog(Tkinter.Toplevel):
    "Базовый класс для диалогов"

    def __init__(self, parent, init_params):
        Tkinter.Toplevel.__init__(self, parent)

        self.withdraw()
        self.init_window(init_params)
        self.transient(parent)
        self.parent = parent
        self.deiconify()

    def run(self):
        self.protocol("WM_DELETE_WINDOW", self.on_destroy)
        self.focus_set()
        self.wait_window(self)

    def set_size(self, width, height):
        sc_width = self.winfo_screenwidth()
        sc_height = self.winfo_screenheight()
        width = min(width, sc_width)
        height = min(height, sc_height)
        x = (sc_width - width) / 2
        y = (sc_height - height) / 2
        y = max(y - 20, 0)
        self.wm_geometry("%dx%d+%d+%d" % (width, height, x, y))

    def init_window(self, params):
        pass

    def on_destroy(self, event=None):
        self.parent.focus_set()
        self.destroy()
