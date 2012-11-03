# -*- coding: utf-8 -*-

import math
from tkFont import Font
from Tkinter import *
from loc_res import _
from tkintertable.Tables import TableCanvas
from tkintertable.TableModels import TableModel
import tkSimpleDialog


clr_stat_frame    = "#E9F6FE"
clr_word_frame    = "#FFFFE0"
clr_answer_frame  = "#E9F6FE"
clr_success       = "#348000"
clr_error         = "#FC0039"
clr_stat          = ["#7B7B00", "#007B00", "#7B7B7B"]

class StatisticDialog(Toplevel):
	def __init__(self, parent, statistic, stat_count_row):
		Toplevel.__init__(self, parent)
		
		self.withdraw()
		self.body(statistic, stat_count_row)
		
		self.transient(parent)
		self.parent = parent
		
		width  = min(self.table_detailed_stat.get_totalWidth(), self.winfo_screenwidth())
		height = min(750, self.winfo_screenheight())
		x = (self.winfo_screenwidth() - width) / 2
		y = (self.winfo_screenheight() - height) / 2
		self.title(_("win_statistic_title"))
		self.resizable(True, True)
		self.wm_geometry("%dx%d+%d+%d" % (width, height, x, y))

		self.deiconify()
		self.wait_visibility() # window needs to be visible for the grab
		self.grab_set()

		self.focus_set()
		self.protocol("WM_DELETE_WINDOW", self.on_destroy)
		self.wait_window(self)

	def on_destroy(self, event=None):
		self.parent.focus_set()
		self.destroy()

	def init_common_stat(self, statistic):
		self.frame_common_stat = Frame(self)
		self.frame_common_stat.grid(row=1, column=0, columnspan=6, sticky=N+S+E+W)

		model_common_stat = TableModel(10, False)
		model_common_stat.add_column(_("clm_name"),       typedata = 'text',    align='left')
		model_common_stat.add_column(_("clm_ru_en_cnt"),  typedata = 'number',  align='right', max_val=u"99999")
		model_common_stat.add_column(_("clm_en_ru_cnt"),  typedata = 'number',  align='right', max_val=u"99999")
		model_common_stat.add_column(_("clm_ru_en_pers"), typedata = 'percent', align='right', max_val=u"100.0 %")
		model_common_stat.add_column(_("clm_en_ru_pers"), typedata = 'percent', align='right', max_val=u"100.0 %")

		row_name = [[_("row_learned")], [_("row_study")], [_("row_learn")], [_("row_total")]]
		for row in [row_name[i] + it for i, it in enumerate(statistic.get_common_stat())]:
			model_common_stat.add_row(row)

		self.table_common_stat = TableCanvas(self.frame_common_stat, model_common_stat, sort_enable = False)
		self.table_common_stat.createTableFrame()
		self.frame_common_stat.grid_forget()

	def init_detailed_stat(self, statistic, stat_count_row):
		self.frame_detailed_stat = Frame(self)
		self.frame_detailed_stat.grid(row=1, column=0, columnspan=6, sticky=N+S+E+W)		

		self.model_ru_en = TableModel(stat_count_row, True)
		self.model_ru_en.add_column(_("clm_word"),          typedata = 'text',    align='left')
		self.model_ru_en.add_column(_("clm_transcription"), typedata = 'text',    align='left')
		self.model_ru_en.add_column(_("clm_translate"),     typedata = 'text',    align='left')
		self.model_ru_en.add_column(_("clm_cnt_suc"),       typedata = 'number',  align='right', max_val=u"999")
		self.model_ru_en.add_column(_("clm_cnt_err"),       typedata = 'number',  align='right', max_val=u"999")
		self.model_ru_en.add_column(_("clm_pers_suc"),      typedata = 'percent', align='right', max_val=u"100.0 %")
		self.model_ru_en.add_column(_("clm_state"),         typedata = 'text',    align='left', max_val=_("st_study")+u"  ")

		for row in statistic.get_ru_en():
			self.model_ru_en.add_row(row)
		self.model_ru_en.sort(6, False)

		self.table_detailed_stat = TableCanvas(self.frame_detailed_stat, self.model_ru_en, sort_enable = True, callback = self.draw_callback)
		self.table_detailed_stat.createTableFrame()

		self.model_en_ru = TableModel(stat_count_row, True)
		self.model_en_ru.add_column(_("clm_word"),          typedata = 'text',    align='left')
		self.model_en_ru.add_column(_("clm_transcription"), typedata = 'text',    align='left')
		self.model_en_ru.add_column(_("clm_translate"),     typedata = 'text',    align='left')
		self.model_en_ru.add_column(_("clm_cnt_suc"),       typedata = 'number',  align='right')
		self.model_en_ru.add_column(_("clm_cnt_err"),       typedata = 'number',  align='right')
		self.model_en_ru.add_column(_("clm_pers_suc"),      typedata = 'percent', align='right')
		self.model_en_ru.add_column(_("clm_state"),         typedata = 'text',    align='left')

		for row in statistic.get_en_ru():
			self.model_en_ru.add_row(row)
		self.model_en_ru.sort(6, False)

		for col in range(0, self.model_en_ru.get_column_count()):
			self.model_en_ru.get_column(col).width = self.model_ru_en.get_column(col).width		

	def body(self, statistic, stat_count_row):
		self.last_button = 0
		Label(self, text="").grid(row=0, column=0, sticky=W+E, padx=0)
		self.btRuEn = Button(self, text=_("btn_ru_en"), command=self.show_ru_en)
		self.btRuEn.grid(row=0, column=1, sticky=W+E, pady=5, padx=1)
		self.btEnRu = Button(self, text=_("btn_en_ru"), command=self.show_en_ru)
		self.btEnRu.grid(row=0, column=2, sticky=W+E, pady=5, padx=1)
		self.btCmnStat = Button(self, text=_("btn_common_stat"), command=self.show_common_stat)
		self.btCmnStat.grid(row=0, column=3, sticky=W+E, pady=5, padx=1)

		self.init_common_stat(statistic)
		self.init_detailed_stat(statistic, stat_count_row)

		self.grid_rowconfigure(1, weight=1)
		self.grid_columnconfigure(1, weight=1)
		self.grid_columnconfigure(2, weight=1)
		self.grid_columnconfigure(3, weight=1)

		self.show_ru_en()
	
	def draw_callback(self, row, col, celltxt, clr):
		if col == 6:
			words = [_("st_learned"), _("st_study"), _("st_learn")]
			ind = int(celltxt)
			return words[ind], clr_stat[ind]
		else:
			return celltxt, clr

	def show_ru_en(self):
		self.btRuEn["relief"]    = "sunken"
		self.btEnRu["relief"]    = "raised"
		self.btCmnStat["relief"] = "raised"
		if self.last_button != 0:
			self.table_detailed_stat.setModel(self.model_ru_en)
			self.frame_common_stat.grid_forget()
			self.frame_detailed_stat.grid(row=1, column=0, columnspan=6, sticky=N+S+E+W)
		self.table_detailed_stat.do_bindings()
		self.last_button = 0

	def show_en_ru(self):
		self.btRuEn["relief"]    = "raised"
		self.btEnRu["relief"]    = "sunken"
		self.btCmnStat["relief"] = "raised"
		if self.last_button != 1:
			self.table_detailed_stat.setModel(self.model_en_ru)
			self.frame_common_stat.grid_forget()
			self.frame_detailed_stat.grid(row=1, column=0, columnspan=6, sticky=N+S+E+W)
		self.table_detailed_stat.do_bindings()
		self.last_button = 1

	def show_common_stat(self):
		self.btRuEn["relief"]    = "raised"
		self.btEnRu["relief"]    = "raised"
		self.btCmnStat["relief"] = "sunken"
		if self.last_button != 2:
			self.frame_detailed_stat.grid_forget()
			self.frame_common_stat.grid(row=1, column=0, columnspan=6, sticky=N+S+E+W)
		self.table_common_stat.do_bindings()
		self.last_button = 2

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
	def __init__(self):
		Tk.__init__(self)
		self.show_answer         = True
		self.lbl_word            = None
		self.lbl_transcription   = None
		self.lbl_result_msg      = None
		self.lbl_correct_word    = None
		self.lbl_correct_word_tr = None
		self.edit_translate      = None
		self.init_window()

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
		bt = Button(frm_stat, image=img, bg=clr_stat_frame, relief="flat", command=self.show_statistic)
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
		self.edit_translate.pack(side="bottom")
		self.edit_translate.focus()

		self.bind("<Return>", self.on_check_translate)
		self.bind("<FocusIn>", lambda event: self.edit_translate.focus())
		########################################################

		x = (self.winfo_screenwidth() - self.winfo_reqwidth()) / 2
		y = (self.winfo_screenheight() - self.winfo_reqheight()) / 2
		self.title(_("win_learning_english"))
		self.resizable(False, False)
		self.wm_geometry("+%d+%d" % (x, y))
		self.protocol("WM_DELETE_WINDOW", self.on_destroy)

	def new_lesson(self):
		pass

	def end_lesson(self):
		pass

	def new_practice(self):
		pass

	def end_practice(self, user_answer):
		pass

	def global_statistic(self):
		pass

	def show(self):
		self.deiconify()
		self.edit_translate.focus()

	def hide(self):
		self.withdraw()

	def on_destroy(self):
		dlg = CloseDialog(self)
		if dlg.result == 1:
			self.end_lesson()
			self.quit()
		elif dlg.result == 0:
			self.end_lesson()

	def show_statistic(self):		
		StatisticDialog(self, self.global_statistic(), self.cfg.get_dict()["stat_count_row"])

	def set_word(self, new_word, is_new):
		if is_new:
			self.lbl_result_msg["text"]  = ""
		else:
			self.lbl_result_msg["text"]  = _("reiterate")
			self.lbl_result_msg["fg"]    = clr_error
		self.lbl_word["text"]            = new_word.word
		self.lbl_transcription["text"]   = "" if self.cfg.get_dict()["hide_transcription"] == "yes" else new_word.transcription
		self.lbl_correct_word["text"]    = ""
		self.lbl_correct_word_tr["text"] = ""
		self.edit_translate.delete(0, END)

	def set_practice_result(self, is_success, right_answer):
		self.lbl_correct_word["text"]    = right_answer.word
		self.lbl_correct_word_tr["text"] = "" if self.cfg.get_dict()["hide_transcription"] == "yes" else right_answer.transcription
		if is_success:
			self.lbl_result_msg["text"] = _("correct")
			self.lbl_result_msg["fg"]   = clr_success
		else:
			self.lbl_result_msg["text"] = _("incorrect")
			self.lbl_result_msg["fg"]   = clr_error

	def set_stat(self, stat):
		success_cnt = stat[0]
		max_success = stat[1]
		error_cnt   = stat[2]
		self.lbl_stat_success["text"] = "%i %s %i/" % (success_cnt, _("of"), max_success)
		self.lbl_stat_error["text"]   = "%i" % error_cnt

	def on_check_translate(self, event):
		if self.show_answer:
			user_answer = self.edit_translate.get()
			if user_answer.strip() == "":
				return
			self.edit_translate["state"] = "readonly"
			self.end_practice(user_answer)
		else:
			self.edit_translate["state"] = "normal"
			self.new_practice()
		self.show_answer = not self.show_answer