# -*- coding: utf-8 -*-

import math
import datetime
import unittest

class Statistic:
	def __init__(self):
		self.success_answer     = 0
		self.error_answer       = 0
		self.last_lesson_date   = None
		self.last_lesson_result = None

	def get_total_answer(self):
		return self.success_answer+self.error_answer

	def get_success_persent(self):
		total = self.get_total_answer()
		if total > 0:
			return float(self.success_answer)/total*100.0
		else:
			return 0.0

	def calc_rating(self, min_percent, min_success_cnt):
		pers  = self.get_success_persent()
		total = self.get_total_answer()
		
		rating = 100.0 - pers
		# пока не достигли необходимого числа правильных ответов, рейтинг выше
		rest_sa = (min_success_cnt - self.success_answer)
		if rest_sa < 0:
			rest_sa = 0
		rating += float(rest_sa)/min_success_cnt*100.0
		# для изученных слов уменьшаем рейтинг
		if pers >= min_percent and total >= min_success_cnt:
			rating /= 3.0
		# чем чаще слово повторяли, тем меньше рейтинг
		rating *= math.exp(-total*0.07)
		# если последний ответ был неправильным увеличиваем рейтинг
		if self.last_lesson_result == False:
			rating *= 1.5
		# чем дольше слово не повторяли, тем выше рейтинг
		days = 0
		if self.last_lesson_date != None:
			days = (datetime.date.today() - datetime.datetime.strptime(self.last_lesson_date, "%Y.%m.%d").date()).days
		rating *= math.log10(days+1.0)+1.0

		return rating

	def update(self, is_success, dt):
		self.last_lesson_date   = dt
		self.last_lesson_result = is_success
		if is_success:
			self.success_answer += 1
		else:
			self.error_answer += 1

	def pack(self):
		return [self.success_answer, self.error_answer, self.last_lesson_date, self.last_lesson_result]

	def unpack(self, statistic):
		self.success_answer, self.error_answer, self.last_lesson_date, self.last_lesson_result = statistic

class StatisticCase(unittest.TestCase):
	def setUp(self):
		self.stat = Statistic()

	def test_init(self):
		self.assertEqual(self.stat.success_answer,        0)
		self.assertEqual(self.stat.error_answer,          0)
		self.assertEqual(self.stat.last_lesson_date,      None)
		self.assertEqual(self.stat.last_lesson_result,    None)		

	def test_get_total_answer(self):
		self.assertEqual(self.stat.get_total_answer(), 0)
		self.stat.update(True, "")
		self.assertEqual(self.stat.get_total_answer(), 1)
		self.stat.update(True, "")
		self.assertEqual(self.stat.get_total_answer(), 2)
		self.stat.update(False, "")
		self.assertEqual(self.stat.get_total_answer(), 3)

	def test_get_success_persent(self):
		self.assertEqual(self.stat.get_success_persent(), 0.0)
		self.stat.update(True, "")
		self.assertEqual(self.stat.get_success_persent(), 100.0)
		self.stat.update(False, "")
		self.assertEqual(self.stat.get_success_persent(), 50.0)
		self.stat.update(True, "")
		self.stat.update(True, "")
		self.assertEqual(self.stat.get_success_persent(), 75.0)

	def test_calc_rating(self):
		today = datetime.date.today()
		dt0   = today.strftime("%Y.%m.%d")
		dt1   = (today - datetime.timedelta(1)).strftime("%Y.%m.%d")

		self.assertAlmostEqual(self.stat.calc_rating(97.0, 10), 200.000, 2)

		self.stat.update(True, dt0)
		self.assertAlmostEqual(self.stat.calc_rating(97.0, 10), 83.915, 2)

		self.stat.update(False, dt0)
		self.assertAlmostEqual(self.stat.calc_rating(97.0, 10), 182.565, 2)

		self.stat.update(True, dt0)
		self.assertAlmostEqual(self.stat.calc_rating(97.0, 10), 91.866, 2)

		self.stat.update(True, dt1)
		self.assertAlmostEqual(self.stat.calc_rating(97.0, 10), 93.413, 2)

		for it in range(0, 7):
			self.stat.update(True, dt1)
		self.assertAlmostEqual(self.stat.calc_rating(97.0, 10), 5.476, 2)

		for it in range(0, 25):
			self.stat.update(True, dt1)
		self.assertAlmostEqual(self.stat.calc_rating(97.0, 10), 0.099, 2)

	def test_update(self):
		dt = "01.02.2010"
		self.stat.update(True, dt)
		self.assertEqual(self.stat.success_answer,        1)
		self.assertEqual(self.stat.error_answer,          0)
		self.assertEqual(self.stat.last_lesson_date,      dt)
		self.assertEqual(self.stat.last_lesson_result,    True)

		self.stat.update(False, dt)
		self.assertEqual(self.stat.success_answer,        1)
		self.assertEqual(self.stat.error_answer,          1)
		self.assertEqual(self.stat.last_lesson_date,      dt)
		self.assertEqual(self.stat.last_lesson_result,    False)

		self.stat.update(False, dt)
		self.assertEqual(self.stat.success_answer,        1)
		self.assertEqual(self.stat.error_answer,          2)
		self.assertEqual(self.stat.last_lesson_date,      dt)
		self.assertEqual(self.stat.last_lesson_result,    False)

	def test_pack_unpack(self):
		self.assertEqual(self.stat.pack(), [0, 0, None, None])
		statistic = (1, 2, "01.02.2010", False)
		self.stat.unpack(statistic)
		self.assertEqual(self.stat.pack(), list(statistic))		

if __name__=="__main__":
	suite = unittest.TestLoader().loadTestsFromTestCase(StatisticCase)
	unittest.TextTestRunner(verbosity=2).run(suite)