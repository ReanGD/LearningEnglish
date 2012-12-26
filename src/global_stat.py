# -*- coding: utf-8 -*-

import unittest


class GlobalStatistic:
	"Расчет данных для отображения статистики пользователю"

	def __init__(self):
		self.stat_en_ru = []
		self.stat_ru_en = []

	def _calc_stat(self, word, stat_info):
		en_word, transcription, ru_word = word.get_show_info()
		total                           = stat_info.get_total_answer()
		success_cnt                     = stat_info.get_success_answer()
		error_cnt                       = total - success_cnt
		study_percent                   = stat_info.get_study_percent()

		if total <= 0:
			study_percent = -100.0  # что бы отличать те, что начали изучать от неначатых
		return (en_word, transcription, ru_word, unicode(success_cnt), unicode(error_cnt), unicode(round(study_percent, 2)))

	def add_word(self, word, stat_en_ru, stat_ru_en):
		self.stat_en_ru.append((self._calc_stat(word, stat_en_ru), word))
		self.stat_ru_en.append((self._calc_stat(word, stat_ru_en), word))

	def get_en_ru(self):
		return self.stat_en_ru

	def get_ru_en(self):
		return self.stat_ru_en

	def get_common_stat(self):
		def type_if(row, type_num):
			if type_num == 0:
				return float(row[5]) == 100.0
			elif type_num == 1:
				return 0.0 < float(row[5]) < 100.0
			else:
				return float(row[5]) < 0.0

		table = []
		total_ru_en = len(self.stat_ru_en)
		total_en_ru = len(self.stat_en_ru)
		for i in range(0, 3):
			cnt_ru_en  = sum(1 for row, w in self.stat_ru_en if type_if(row, i))
			perc_ru_en = round(float(cnt_ru_en) * 100.0 / float(total_ru_en), 2)
			cnt_en_ru  = sum(1 for row, w in self.stat_en_ru if type_if(row, i))
			perc_en_ru = round(float(cnt_en_ru) * 100.0 / float(total_en_ru), 2)
			table.append([unicode(cnt_ru_en), unicode(cnt_en_ru), unicode(perc_ru_en), unicode(perc_en_ru)])
		table.append([unicode(total_ru_en), unicode(total_en_ru), u"100.0", u"100.0"])
		return table


class WordMock:
	"Эмуляция класса Word для тестирования"

	def __init__(self, en_word, transcription, ru_word):
		self.en_word = en_word
		self.transcription = transcription
		self.ru_word = ru_word

	def get_show_info(self):
		return self.en_word, self.transcription, self.ru_word


class StatisticMock:
	"Эмуляция класса Statistic для тестирования"

	def __init__(self, total_answer, success_answer, study_percent):
		self.total_answer = total_answer
		self.success_answer = success_answer
		self.study_percent = study_percent

	def get_total_answer(self):
		return self.total_answer

	def get_success_answer(self):
		return self.success_answer

	def get_study_percent(self):
		return self.study_percent


class GlobalStatisticTestCase(unittest.TestCase):
	"Набор тестов для класса GlobalStatistic"

	def test_calc(self):
		"Тестирование результатов расчета глобальной статистики по словам"
		obj = GlobalStatistic()
		w0 = WordMock("en0", "tr0", "ru0")
		obj.add_word(w0, StatisticMock(3, 1, 100.0), StatisticMock(30, 10, 100.0))
		w1 = WordMock("en1", "tr1", "ru1")
		obj.add_word(w1, StatisticMock(6, 2, 50.0), StatisticMock(60, 20, 60.0))
		w2 = WordMock("en2", "tr2", "ru2")
		obj.add_word(w2, StatisticMock(9, 3, -100.0), StatisticMock(90, 30, -100.0))

		self.assertEqual(obj.get_en_ru(),
			[(("en0", "tr0", "ru0", unicode(1), unicode(2), unicode(100.0)), w0),
			(("en1", "tr1", "ru1", unicode(2), unicode(4), unicode(50.0)), w1),
			(("en2", "tr2", "ru2", unicode(3), unicode(6), unicode(-100.0)), w2)])

		self.assertEqual(obj.get_ru_en(),
			[(("en0", "tr0", "ru0", unicode(10), unicode(20), unicode(100.0)), w0),
			(("en1", "tr1", "ru1", unicode(20), unicode(40), unicode(60.0)), w1),
			(("en2", "tr2", "ru2", unicode(30), unicode(60), unicode(-100.0)), w2)])

		self.assertEqual(obj.get_common_stat(),
			[[unicode(1), unicode(1), unicode(33.33), unicode(33.33)],
			[unicode(1), unicode(1), unicode(33.33), unicode(33.33)],
			[unicode(1), unicode(1), unicode(33.33), unicode(33.33)],
			[unicode(3), unicode(3), unicode(100.0), unicode(100.0)]])

if __name__ == "__main__":
	suite = unittest.TestLoader().loadTestsFromTestCase(GlobalStatisticTestCase)
	unittest.TextTestRunner(verbosity=2).run(suite)
