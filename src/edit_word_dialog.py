# -*- coding: utf-8 -*-

from Tkinter import *
from tkFont import Font
import tkMessageBox
import dictionary
from loc_res import _
from top_dialog import TopDialog
from operation import BaseOperation


class _EditWordDialog(TopDialog):

	def __init__(self, parent, en_str, tr_str, ru_str, callback):
		TopDialog.__init__(self, parent, (en_str, tr_str, ru_str))
		self._callback = callback
		self.title(_("win_editword_title"))
		self.wait_visibility()
		self.set_size(self.winfo_reqwidth(), self.winfo_reqheight())
		self.resizable(True, False)
		self.run()

	def init_window(self, (en_str, tr_str, ru_str)):
		prnt = self
		fnt_edit = Font(family="Arial", size=-16)  # 12pt

		self.var_en = StringVar(value=en_str)
		self.var_tr = StringVar(value=tr_str)
		self.var_ru = StringVar(value=ru_str)

		Label(prnt, text=_("lbl_edit_en")).grid(padx=15, sticky=SW)
		edit_en = Entry(prnt, font=fnt_edit, textvariable=self.var_en)
		edit_en.grid(padx=15, pady=4, sticky=EW)
		edit_en.focus()
		edit_en.select_range(0, END)

		Label(prnt, text=_("lbl_edit_tr")).grid(padx=15, sticky=W)
		Entry(prnt, font=fnt_edit, textvariable=self.var_tr).grid(padx=15, pady=4, sticky=EW)

		Label(prnt, text=_("lbl_edit_ru")).grid(padx=15, sticky=W)
		Entry(prnt, font=fnt_edit, textvariable=self.var_ru).grid(padx=15, pady=4, sticky=EW)

		frm_btn = Frame(prnt)
		Button(frm_btn, text="OK", width=10, command=self.on_ok, default=ACTIVE).pack(side=LEFT, padx=5, pady=5)
		Button(frm_btn, text="Cancel", width=10, command=self.on_destroy).pack(side=LEFT, padx=5, pady=5)
		frm_btn.grid(padx=10, pady=5, sticky=EW)

		self.bind("<Return>", self.on_ok)
		self.bind("<Escape>", self.on_destroy)

		prnt.grid_rowconfigure(0, minsize=30)
		prnt.grid_columnconfigure(0, weight=1)
		prnt.minsize(300, prnt.minsize()[1])

	def on_ok(self, event=None):
		if tkMessageBox.askyesno(_("win_confirm_title"), _("msg_confirm_rename")):
			if self._callback(self.var_en.get(), self.var_tr.get(), self.var_ru.get()):
				self.on_destroy()


class OperationEditWord(BaseOperation):

	def __init__(self, dictionary):
		BaseOperation.__init__(self)
		self._dictionary = dictionary

	def execute(self, parent, (en_str, tr_str, ru_str)):
		self.old_en = en_str
		_EditWordDialog(parent, en_str, tr_str, ru_str, self._rename_word)

	def _rename_word(self, en_str, tr_str, ru_str):
		result = True
		try:
			self._dictionary.rename_word(self.old_en, en_str, tr_str, ru_str)
			self.callback()
		except dictionary.ErrDict as err:
			import error_dialog
			error_dialog.show_error(err.loc_res_msg)
			result = False
		return result


def _test_run():
	OperationEditWord(None).execute(Tk(), (u"action", u"'ækʃən", u"действие"))

if __name__ == '__main__':
	_test_run()
