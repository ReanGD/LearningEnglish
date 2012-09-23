# -*- coding: utf-8 -*-

import math
from tkFont import Font
from Tkinter import *
from loc_res import _
import tkSimpleDialog

clr_stat_frame    = "#E9F6FE"
clr_word_frame    = "#FFFFE0"
clr_answer_frame  = "#E9F6FE"
clr_success       = "#348000"
clr_error         = "#FC0039"
clr_black         = "#000000"
clr_tbl_bg        = ["#E9F6FE", "#FFFFE0"]
clr_stat          = ["#7B7B00", "#007B00", "#7B7B7B"]

LEFT  = 0
RIGHT = 1

class AutoScrollbar(Scrollbar):
	def set(self, lo, hi):
		if float(lo) <= 0.0 and float(hi) >= 1.0:
			self.tk.call("grid", "remove", self)
		else:
			self.grid()
		Scrollbar.set(self, lo, hi)

class ScrollCanvas(Canvas):
	def __init__(self, parent):
		delta_scr  = 1
		delta_page = 10
		
		self.vscrollbar = AutoScrollbar(parent)
		Canvas.__init__(self, parent, yscrollcommand=self.vscrollbar.set, bg=clr_tbl_bg[0], highlightthickness=0)
		self.vscrollbar.config(command=self.yview)

		parent.bind("<MouseWheel>", lambda event=None: self.move(-int(math.copysign(delta_scr, event.delta))))
		parent.bind("<Button-4>",   lambda event=None: self.move(-delta_scr))
		parent.bind("<Button-5>",   lambda event=None: self.move(delta_scr))
		parent.bind("<Prior>",      lambda event=None: self.move(-delta_page))
		parent.bind("<Next>",       lambda event=None: self.move(delta_page))
		parent.bind("<Up>",         lambda event=None: self.move(-delta_scr))
		parent.bind("<Down>",       lambda event=None: self.move(delta_scr))
		parent.bind("<Home>",       lambda event=None: self.yview_moveto(0))
		parent.bind("<End>",        lambda event=None: self.yview_moveto(1))

	def move(self, delta):
		self.yview_scroll(delta, "units")

	def grid(self, row, column, columnspan):
		self.vscrollbar.grid(row=row, column=column+columnspan-1, sticky=N+S)
		Canvas.grid(self,row=row, column=column, columnspan=columnspan-1, sticky=N+S+E+W)

	def clear(self):
		self.delete(ALL)
		self.yview_moveto(0)

	def create_table(self, rc_left, rc_top, row_height, row_cnt, clms_width):
		self.tbl_rc_top     = rc_top
		self.tbl_row_height = row_height
		self.tbl_column_pos = clms_width + [0]

		sm = rc_left
		for i, it in enumerate(self.tbl_column_pos):
			self.tbl_column_pos[i], sm = sm, sm+it

		rc_right  = self.tbl_column_pos[-1]
		rc_bottom = rc_top + row_cnt*row_height
		
		self.clear()

		self.create_line(rc_left, rc_top, rc_right, rc_top)
		if row_cnt % 2 == 1:
			self.create_line(rc_left, rc_bottom, rc_right+1, rc_bottom)
		for i in range(1, row_cnt, 2):
			sm = rc_top+row_height*i
			self.create_rectangle(rc_left, sm, rc_right, sm+row_height, fill=clr_tbl_bg[1], outline=clr_black)

		for i in self.tbl_column_pos:
			self.create_line(i, rc_top, i, rc_bottom)

	def fill_cell(self, column, row, text, clr, font, alignment):
		if alignment not in (LEFT, RIGHT):
			alignment = LEFT
		if alignment == LEFT:
			anchor  = W
			clm_pos = self.tbl_column_pos[column] + 5
		else:
			anchor  = E
			clm_pos = self.tbl_column_pos[column+1] - 5
		row_pos = self.tbl_rc_top + (self.tbl_row_height+1)//2 + self.tbl_row_height*row
		self.create_text(clm_pos, row_pos, text=text, anchor=anchor, font=font, fill=clr)

class StatisticDialog(Toplevel):
	def __init__(self, parent, statistic):
		Toplevel.__init__(self, parent, bg=clr_tbl_bg[0])
		
		self.transient(parent)
		self.parent    = parent
		self.statistic = statistic

		self.body()

		self.wait_visibility() # window needs to be visible for the grab
		self.grab_set()

		width  = 850
		height = 750
		x = (self.winfo_screenwidth() - width) / 2
		y = (self.winfo_screenheight() - height) / 2
		self.title(_("win_statistic_title"))
		self.resizable(False, True)
		self.wm_geometry("%dx%d+%d+%d" % (width, height, x, y))
		self.focus_set()
		self.protocol("WM_DELETE_WINDOW", self.on_destroy)
		self.wait_window(self)

	def on_destroy(self, event=None):
		self.parent.focus_set()
		self.destroy()

	def get_header_text(self):
		return (_("clm_word"), _("clm_transcription"), _("clm_translate"), _("clm_cnt_suc"), _("clm_cnt_err"), _("clm_pers_suc"), _("clm_state"))

	def body(self):
		fnt = Font(family="Arial", size=10)
		self.tbl_fnt = fnt
				
		num_len       = max(fnt.measure(_("clm_num")), fnt.measure("9999"))
		word_len      = max(fnt.measure(_("clm_word")), fnt.measure(_("clm_transcription")), fnt.measure(_("clm_translate")))
		cnt_len       = max(fnt.measure("9999"), fnt.measure(_("clm_cnt_suc")), fnt.measure(_("clm_cnt_err")))
		prs_len       = max(fnt.measure("100.0%"), fnt.measure(_("clm_pers_suc")))
		state_len     = max(fnt.measure(_("st_learn")), fnt.measure(_("st_learned")), fnt.measure(_("st_study")), fnt.measure(_("clm_state")))
		self.len_clmn = [num_len, word_len, word_len, word_len, cnt_len, cnt_len, prs_len, state_len]

		# Находим слова с большей длинной, чем умолчательная
		for stat in self.statistic.get_ru_en():
			for it in range(0, 3):
				if len(stat[it]) > 10:
					self.len_clmn[it+1] = max(self.len_clmn[it+1], fnt.measure(stat[it]))

		self.len_clmn = [i+20 for i in self.len_clmn]

		Label(self, text="", bg=clr_tbl_bg[0]).grid(row=0, column=0, sticky=W+E, padx=2)
		self.btRuEn = Button(self, text=_("btn_ru_en"), command=self.show_ru_en)
		self.btRuEn.grid(row=0, column=1, sticky=W+E, pady=5, padx=1)
		self.btEnRu = Button(self, text=_("btn_en_ru"), command=self.show_en_ru)
		self.btEnRu.grid(row=0, column=2, sticky=W+E, pady=5, padx=1)
		self.btCmnStat = Button(self, text=_("btn_common_stat"), command=self.show_common_stat)
		self.btCmnStat.grid(row=0, column=3, sticky=W+E, pady=5, padx=1)

		self.canvas = ScrollCanvas(self)
		self.canvas.grid(row=1, column=1, columnspan=5)

		self.grid_rowconfigure(1, weight=1)
		self.grid_columnconfigure(1, weight=1)
		self.grid_columnconfigure(2, weight=1)
		self.grid_columnconfigure(3, weight=1)

		self.show_ru_en()

		self.canvas.config(scrollregion=self.canvas.bbox("all"))

	def draw_stat(self, stat_table):
		rc_left   = 0
		rc_top    = 1
		row_height = self.tbl_fnt.metrics("linespace")+1
		self.canvas.create_table(rc_left, rc_top, row_height, len(stat_table)+1, self.len_clmn)

		state_str  = (_("st_learned"), _("st_study"), _("st_learn"))
		for i, stat in enumerate([self.get_header_text()]+stat_table):
			for it in range(0, len(self.len_clmn)):
				stat_it = it-1
				alignment = LEFT
				if it == 0:
					if i == 0:
						txt = _("clm_num")
					else:
						txt = str(i)
						alignment = RIGHT
					clr = clr_black
				elif it == 7 and i!=0:
					txt = state_str[stat[stat_it]]
					clr = clr_stat[stat[stat_it]]
				else:
					txt = stat[stat_it]
					clr = clr_black
					if i > 0 and it >= 4:
						alignment = RIGHT
				self.canvas.fill_cell(it, i, txt, clr, self.tbl_fnt, alignment)

	def draw_common_stat(self):
		row_name = [[_("row_learned")], [_("row_study")], [_("row_learn")], [_("row_total")]]
		table = [row_name[i] + it for i, it in enumerate(self.statistic.get_common_stat())]
		table = [["", _("clm_ru_en_cnt"), _("clm_en_ru_cnt"), _("clm_ru_en_pers"), _("clm_en_ru_pers")]] + table

		len_clmn = [0, 0, 0, 0, 0]
		for row in table:
			for i, text in enumerate(row):
				len_clmn[i] = max(len_clmn[i], self.tbl_fnt.measure(text))
		len_clmn = [i+20 for i in len_clmn]

		rc_left    = 0
		rc_top     = 1
		row_height = self.tbl_fnt.metrics("linespace")+1
		self.canvas.create_table(rc_left, rc_top, row_height, 5, len_clmn)

		for i, row in enumerate(table):
			for j, text in enumerate(row):
				if i>0 and j>0:
					alignment = RIGHT
				else:
					alignment = LEFT
				self.canvas.fill_cell(j, i, text, clr_black, self.tbl_fnt, alignment)

	def show_ru_en(self):
		self.btRuEn["relief"]    = "sunken"
		self.btEnRu["relief"]    = "raised"
		self.btCmnStat["relief"] = "raised"
		self.draw_stat(self.statistic.get_ru_en())

	def show_en_ru(self):
		self.btRuEn["relief"]    = "raised"
		self.btEnRu["relief"]    = "sunken"
		self.btCmnStat["relief"] = "raised"
		self.draw_stat(self.statistic.get_en_ru())

	def show_common_stat(self):
		self.btRuEn["relief"]    = "raised"
		self.btEnRu["relief"]    = "raised"
		self.btCmnStat["relief"] = "sunken"
		self.draw_common_stat()

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
		StatisticDialog(self, self.global_statistic())

	def set_word(self, new_word, is_new):
		if is_new:
			self.lbl_result_msg["text"]  = ""
		else:
			self.lbl_result_msg["text"]  = _("reiterate")
			self.lbl_result_msg["fg"]    = clr_error
		self.lbl_word["text"]            = new_word.word
		self.lbl_transcription["text"]   = new_word.transcription
		self.lbl_correct_word["text"]    = ""
		self.lbl_correct_word_tr["text"] = ""
		self.edit_translate.delete(0, END)

	def set_practice_result(self, is_success, right_answer):
		self.lbl_correct_word["text"]    = right_answer.word
		self.lbl_correct_word_tr["text"] = right_answer.transcription
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