# -*- coding: utf-8 -*-

from Tkinter import *
import json
import tkFont
import random
import re

class Word:
	def __init__(self, en_word, transcription, ru_word):
		self.en_word		= en_word
		self.transcription	= '[%s]' % transcription
		self.ru_word		= ru_word

	def check(self, answer, is_en_to_ru):
		if is_en_to_ru:
			success_answer = self.ru_word
		else:
			success_answer = self.en_word
		return answer.strip().lower() == success_answer.strip().lower()

class Window(Tk):
	def __init__(self, next_word_callback):
		Tk.__init__(self)
		self.next_word_callback = next_word_callback
		self.show_answer = False
		self.word = None
		self.lbl_word = None
		self.is_success = None
		self.is_en_to_ru = True
		self.lbl_transcription = None
		self.lbl_result_msg = None
		self.lbl_correct_word = None
		self.lbl_correct_word_tr = None

	def init_window(self):
		fnt_stat          = tkFont.Font(family="Arial", size=9)
		fnt_msg           = tkFont.Font(family="Arial", size=10, weight='bold')
		fnt_word          = tkFont.Font(family="Arial", size=14)
		fnt_transcription = tkFont.Font(family="Arial", size=10)
		fnt_translate     = tkFont.Font(family="Arial", size=12)

		clr_stat_frame   = "#E9F6FE"
		clr_word_frame   = "#FFFFE0"
		clr_answer_frame = "#E9F6FE"
		clr_success      = "#348000"
		clr_error        = "#FC0039"

		########################################################

		frm_stat = Frame(self, bg=clr_stat_frame, bd=5)
		frm_stat.pack(fill="both")

		Label(frm_stat, font=fnt_stat, bg=clr_stat_frame, text="Верно/Неверно").pack(side="left")

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
		self.title("Изучаем английский")
		self.resizable(False, False)
		self.wm_geometry("+%d+%d" % (x, y))

	def set_word(self, word, is_en_to_ru):
		self.word = word
		self.is_en_to_ru = is_en_to_ru

		if is_en_to_ru:
			self.lbl_word["text"] = word.en_word
			self.lbl_transcription["text"] = word.transcription			
		else:
			self.lbl_word["text"] = word.ru_word
			self.lbl_transcription["text"] = ""

		self.lbl_result_msg["text"] = ""
		self.lbl_correct_word["text"] = ""
		self.lbl_correct_word_tr["text"] = ""
		self.edit_translate.delete(0, END)

	def set_stat(self, success_cnt, max_success, error_cnt):
		self.lbl_stat_success['text'] = "%i из %i/" % (success_cnt, max_success)
		self.lbl_stat_error['text'] = "%i" % error_cnt
	
	def on_check_translate(self, event):
		self.show_answer = not self.show_answer
		if not self.show_answer:
			self.next_word_callback(self.is_success)
			return

		user_answer = event.widget.get()
		if self.is_en_to_ru:
			self.lbl_correct_word["text"] = self.word.ru_word
			self.lbl_correct_word_tr["text"] = ''
		else:
			self.lbl_correct_word["text"] = self.word.en_word
			self.lbl_correct_word_tr["text"] = self.word.transcription

		if self.word.check(user_answer, self.is_en_to_ru):
			self.is_success = True
			self.lbl_result_msg["text"] = "Верно"
			self.lbl_result_msg["fg"] = "#348000"
		else:
			self.is_success = False
			self.lbl_result_msg["text"] = "Неверно"
			self.lbl_result_msg["fg"] = "#FC0039"

class App:
	def __init__(self):
		config_txt		 = re.compile(r"/\*.*?\*/", re.DOTALL).sub("", open("config.json").read()) # удаляем комментарии
		config_params	 = json.loads(config_txt)
		self.max_success = config_params["words_per_lesson"]
		self.words		 = self.load_dict(config_params["path_to_dict"])

		self.win = Window(self.get_next)
		self.win.init_window()
		self.success_cnt = 0
		self.error_cnt = 0
		self.get_next(None)
		self.win.mainloop()

	def load_dict(self, path):
		words = []
		raw_dict = json.loads(open(path).read())
		for it in raw_dict:
			words.append(Word(it[0],it[1],it[2]))
		return words

	def update_stat(self, is_success):
		if is_success != None:
			if is_success:
				self.success_cnt += 1
			else:
				self.error_cnt += 1
		self.win.set_stat(self.success_cnt, self.max_success, self.error_cnt)

	def get_next(self, is_success):
		self.update_stat(is_success)
		if self.max_success == self.success_cnt:
			self.win.destroy()
		else:
			num = random.randint(0, len(self.words)-1)
			is_en_to_ru = random.randint(0, 1) == 1
			self.win.set_word(self.words[num], is_en_to_ru)

if __name__=="__main__":
	App()