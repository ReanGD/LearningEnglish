# -*- coding: utf-8 -*-

from tkFont import Font
from Tkinter import *
import tkSimpleDialog

_str_dict = {
	 "end_lesson"        : "Завершить текущий урок"
	,"end_program"       : "Закрыть программу"
	,"correct_incorrect" : "Верно/Неверно"
	,"learning_english"  : "Изучаем английский"
	,"correct"           : "Верно"
	,"incorrect"         : "Неверно"
	,"of"                : "из"
}

clr_stat_frame   = "#E9F6FE"
clr_word_frame   = "#FFFFE0"
clr_answer_frame = "#E9F6FE"
clr_success      = "#348000"
clr_error        = "#FC0039"

def _(name):
	return _str_dict[name]

class CloseDialog(tkSimpleDialog.Dialog):
	def body(self, master):
		self.var = IntVar(0)
		Radiobutton(master, text=_("end_lesson"),  variable=self.var, value=0).grid(sticky="w")
		Radiobutton(master, text=_("end_program"), variable=self.var, value=1).grid(sticky="w")
		self.resizable(False, False)
		return None

	def apply(self):
		self.result = self.var.get()

class MainWindow(Tk):
	def __init__(self, next_word_callback, end_lesson_callback):
		Tk.__init__(self)
		self.next_word_callback  = next_word_callback
		self.end_lesson_callback = end_lesson_callback
		self.show_answer         = False
		self.practice            = None
		self.lbl_word            = None
		self.lbl_transcription   = None
		self.lbl_result_msg      = None
		self.lbl_correct_word    = None
		self.lbl_correct_word_tr = None

	def init_window(self):
		fnt_stat          = Font(family="Arial", size=9)
		fnt_msg           = Font(family="Arial", size=10, weight="bold")
		fnt_word          = Font(family="Arial", size=14)
		fnt_transcription = Font(family="Arial", size=10)
		fnt_translate     = Font(family="Arial", size=12)

		########################################################

		frm_stat = Frame(self, bg=clr_stat_frame, bd=5)
		frm_stat.pack(fill="both")

		Label(frm_stat, font=fnt_stat, bg=clr_stat_frame, text=_("correct_incorrect")).pack(side="left")

		self.lbl_stat_error = Label(frm_stat, font=fnt_stat, bg=clr_stat_frame, fg=clr_error, borderwidth=0)
		self.lbl_stat_error.pack(side="right")

		self.lbl_stat_success = Label(frm_stat, font=fnt_stat, bg=clr_stat_frame, fg=clr_success, borderwidth=0)
		self.lbl_stat_success.pack(side="right")

		########################################################

		frm_word = Frame(self, bg=clr_word_frame, bd=5)
		frm_word.pack(fill="both")

		self.lbl_word = Label(frm_word, font=fnt_word, bg=clr_word_frame)
		self.lbl_word.pack()

		self.lbl_transcription = Label(frm_word, font=fnt_transcription, bg=clr_word_frame)
		self.lbl_transcription.pack()

		########################################################

		frm_answer = Frame(self, bg=clr_answer_frame, bd=15)
		frm_answer.pack(fill="both")

		frm_message = Frame(frm_answer, bg=clr_answer_frame)
		frm_message.pack(fill="both")

		self.lbl_result_msg = Label(frm_message, font=fnt_msg, bg=clr_answer_frame)
		self.lbl_result_msg.pack(side="left")

		self.lbl_correct_word = Label(frm_message, font=fnt_msg, bg=clr_answer_frame)
		self.lbl_correct_word.pack(side="left")

		self.lbl_correct_word_tr = Label(frm_message, font=fnt_transcription, bg=clr_answer_frame)
		self.lbl_correct_word_tr.pack(side="left")

		self.edit_translate = Entry(frm_answer, font=fnt_translate, width=30)
		self.edit_translate.bind("<Return>", self.on_check_translate)
		self.edit_translate.pack(side="bottom")
		self.edit_translate.focus()

		########################################################

		x = (self.winfo_screenwidth() - self.winfo_reqwidth()) / 2
		y = (self.winfo_screenheight() - self.winfo_reqheight()) / 2
		self.title(_("learning_english"))
		self.resizable(False, False)
		self.wm_geometry("+%d+%d" % (x, y))
		self.protocol("WM_DELETE_WINDOW", self.on_destroy)

	def show(self):
		self.deiconify()
		self.edit_translate.focus()

	def hide(self):
		self.withdraw()

	def on_destroy(self):
		dlg = CloseDialog(self)
		if dlg.result == 1:
			self.end_lesson_callback()
			self.quit()
		elif dlg.result == 0:
			self.end_lesson_callback()

	def set_word(self, practice):
		self.practice = practice

		self.lbl_word["text"],  self.lbl_transcription["text"] = practice.source_data()
		
		self.lbl_result_msg["text"]      = ""
		self.lbl_correct_word["text"]    = ""
		self.lbl_correct_word_tr["text"] = ""
		self.edit_translate.delete(0, END)

	def set_stat(self, stat):
		success_cnt = stat[0]
		max_success = stat[1]
		error_cnt   = stat[2]
		self.lbl_stat_success['text'] = "%i %s %i/" % (success_cnt, _("of"), max_success)
		self.lbl_stat_error['text']   = "%i" % error_cnt
	
	def on_check_translate(self, event):
		self.show_answer = not self.show_answer
		if not self.show_answer:
			self.next_word_callback()
			return

		user_answer = event.widget.get()
		is_success, self.lbl_correct_word["text"], self.lbl_correct_word_tr["text"] = self.practice.check(user_answer)
		if is_success:
			self.lbl_result_msg["text"] = _("correct")
			self.lbl_result_msg["fg"]   = clr_success
		else:
			self.lbl_result_msg["text"] = _("incorrect")
			self.lbl_result_msg["fg"]   = clr_error