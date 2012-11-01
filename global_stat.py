# -*- coding: utf-8 -*-

class GlobalStatistic:
	def __init__(self, min_percent, min_success_cnt):
		self.stat_en_ru = []
		self.stat_ru_en = []
		self.min_percent     = min_percent
		self.min_success_cnt = min_success_cnt

	def calc_stat(self, word, stat_info):
		en_word, transcription, ru_word = word.get_show_info()
		total       = stat_info.get_total_answer()
		success_cnt = stat_info.get_success_answer()
		error_cnt   = total - success_cnt
		pers        = stat_info.get_success_persent()

		if pers >= self.min_percent and total >= self.min_success_cnt:
			state = 0
		elif total > 0:
			state = 1
		else:
			state = 2
		return (en_word, transcription, ru_word, unicode(success_cnt), unicode(error_cnt), unicode(round(pers, 2)), unicode(state))

	def add_word(self, word, stat_en_ru, stat_ru_en):
		self.stat_en_ru.append(self.calc_stat(word, stat_en_ru))
		self.stat_ru_en.append(self.calc_stat(word, stat_ru_en))

	def get_en_ru(self):
		return self.stat_en_ru

	def get_ru_en(self):
		return self.stat_ru_en

	def get_common_stat(self):
		table = []
		total_ru_en = len(self.stat_ru_en)
		total_en_ru = len(self.stat_en_ru)
		for i in range(0, 3):
			cnt_ru_en  = sum(1 for j in self.stat_ru_en if j[6] == unicode(i))
			pers_ru_en = round(float(cnt_ru_en)*100.0/float(total_ru_en), 2)
			cnt_en_ru  = sum(1 for j in self.stat_en_ru if j[6] == unicode(i))
			pers_en_ru = round(float(cnt_en_ru)*100.0/float(total_en_ru), 2)
			table.append([unicode(cnt_ru_en), unicode(cnt_en_ru), unicode(pers_ru_en), unicode(pers_en_ru)])
		table.append([unicode(total_ru_en), unicode(total_en_ru), u"100.0", u"100.0"])
		return table