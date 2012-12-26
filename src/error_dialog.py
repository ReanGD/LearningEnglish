# -*- coding: utf-8 -*-

import tkMessageBox
from loc_res import _


def show_critical_error(loc_res_msg):
	tkMessageBox.showerror(_("win_critical_error"), _(loc_res_msg))


def show_error(loc_res_msg):
	tkMessageBox.showerror(_("win_error"), _(loc_res_msg))
