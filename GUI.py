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
	,"learn"             : "учить"
	,"learned"           : "выучено"
	,"study"             : "изучаем"
}

clr_stat_frame   = "#E9F6FE"
clr_word_frame   = "#FFFFE0"
clr_answer_frame = "#E9F6FE"
clr_success      = "#348000"
clr_error        = "#FC0039"

def _(name):
	return _str_dict[name]

class AutoScrollbar(Scrollbar):
	def set(self, lo, hi):
		if float(lo) <= 0.0 and float(hi) >= 1.0:
			self.tk.call("grid", "remove", self)
		else:
			self.grid()
		Scrollbar.set(self, lo, hi)

class ScrollCanvas(Canvas):
	def __init__(self, parent):
		self.delta = 1
		
		vscrollbar = AutoScrollbar(parent)
		Canvas.__init__(self, parent, yscrollcommand=vscrollbar.set)
		vscrollbar.config(command=self.yview)
		
		vscrollbar.grid(row=0, column=1, sticky=N+S)
		self.grid(row=0, column=0, sticky=N+S+E+W)
		
		parent.grid_rowconfigure(0, weight=1)
		parent.grid_columnconfigure(0, weight=1)

		parent.bind("<MouseWheel>", self.on_mouse_wheel)
		parent.bind('<Button-4>', self.scroll_up)
		parent.bind('<Button-5>', self.scroll_down)

	def scroll_up(self, event=None):
		self.yview("scroll", -self.delta, 'units')

	def scroll_down(self, event=None):
		self.yview("scroll", self.delta, 'units')

	def on_mouse_wheel(self, event):
		if event.delta > 0:
			self.scroll_up(event)
		else:
			self.scroll_down(event)

class StatisticDialog(Toplevel):
	def __init__(self, parent, dictionary):		
		Toplevel.__init__(self, parent)
		
		self.transient(parent)
		self.parent = parent

		self.body(dictionary)

		self.wait_visibility() # window needs to be visible for the grab
		self.grab_set()

		width  = 800
		height = 600
		x = (self.winfo_screenwidth() - width) / 2
		y = (self.winfo_screenheight() - height) / 2
		self.wm_geometry("%dx%d+%d+%d" % (width, height, x, y))
		self.resizable(False, False)
		self.focus_set()
		self.protocol("WM_DELETE_WINDOW", self.on_destroy)
		self.wait_window(self)

	def on_destroy(self, event=None):
		self.parent.focus_set()
		self.destroy()

	def body(self, dictionary):
		canvas = ScrollCanvas(self)
		
		fnt = Font(family="Arial", size=9)
		
		word_len = fnt.measure("W"*10) 
		cnt_len  = fnt.measure("9999")
		prs_len  = fnt.measure("100.0%")
		len_text = [word_len, word_len, word_len, cnt_len, cnt_len, prs_len, cnt_len, cnt_len, prs_len]

		for stat in dictionary.words_statistic():
			for it in range(0, 3):
				if stat[it] > 9:
					len_text[it] = max(len_text[it], fnt.measure(stat[it]))
		sm = 0
		for it in range(0, 9):
			len_text[it], sm = sm, sm+len_text[it]+20

		h = fnt.metrics("linespace")
		for i, stat in enumerate(dictionary.words_statistic()):
			for it in range(0, 9):
				canvas.create_text(len_text[it], (i+1)*h, text=stat[it], anchor=W, font=fnt)

		canvas.config(scrollregion=canvas.bbox("all"))

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
	def __init__(self, get_dict_callback, next_word_callback, end_lesson_callback):
		Tk.__init__(self)
		self.get_dict_callback   = get_dict_callback
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

		img = PhotoImage(file="info.gif")
		bt = Button(frm_stat, image=img, command=self.show_statistic)
		bt.image = img
		bt.pack(side="right")

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

	def show_statistic(self):
		StatisticDialog(self, self.get_dict_callback())

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