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

	def __repr__(self):
		fmt = "Statistic(success_answer = {0}; error_answer = {1}; last_lesson_date = {2}; last_lesson_result = {3})"
		return fmt.format(self.success_answer, self.error_answer, self.last_lesson_date, self.last_lesson_result)

	def __eq__(self, other):
		return self.success_answer == other.success_answer and \
				self.error_answer == other.error_answer and \
				self.last_lesson_date == other.last_lesson_date and \
				self.last_lesson_result == other.last_lesson_result

	def get_total_answer(self):
		return self.success_answer + self.error_answer

	def get_success_answer(self):
		return self.success_answer

	def get_success_persent(self):
		total = self.get_total_answer()
		if total > 0:
			return float(self.success_answer) / total * 100.0
		else:
			return 0.0

	def calc_rating(self, min_percent, min_success_cnt):
		pers  = self.get_success_persent()
		total = self.get_total_answer()

		# Базовый рейтинг от 1 до 101
		rating = 101.0 - pers
		# пока не достигли необходимого числа правильных ответов, рейтинг выше
		rest_sa = (min_success_cnt - self.success_answer)
		if rest_sa < 0:
			rest_sa = 0
		rating += float(rest_sa) / min_success_cnt * 100.0
		# для изученных слов уменьшаем рейтинг
		if pers >= min_percent and total >= min_success_cnt:
			rating /= 3.0
		# чем чаще слово повторяли, тем меньше рейтинг
		rating *= math.exp(-total * 0.07)
		# если последний ответ был неправильным увеличиваем рейтинг
		if self.last_lesson_result == False:
			rating *= 1.5
		# чем дольше слово не повторяли, тем выше рейтинг
		days = 0
		if self.last_lesson_date != None:
			days = (datetime.date.today() - datetime.datetime.strptime(self.last_lesson_date, "%Y.%m.%d").date()).days
		rating *= math.log10(days + 1.0) + 1.0

		return max(rating, 0.1)

	def update(self, is_success, dt, first):
		self.last_lesson_date   = dt
		self.last_lesson_result = is_success
		if first or is_success:
			self.success_answer += 1
		else:
			self.error_answer += 1

	def pack(self):
		return [self.success_answer, self.error_answer, self.last_lesson_date, self.last_lesson_result]

	def unpack(self, statistic):
		self.success_answer, self.error_answer, self.last_lesson_date, self.last_lesson_result = statistic


class StatisticTestCase(unittest.TestCase):
	def setUp(self):
		self.stat = Statistic()

	def test_init(self):
		self.assertEqual(self.stat.success_answer,        0)
		self.assertEqual(self.stat.error_answer,          0)
		self.assertEqual(self.stat.last_lesson_date,      None)
		self.assertEqual(self.stat.last_lesson_result,    None)

	def test_eq(self):
		other = Statistic()
		self.assertEqual(self.stat, other)

	def test_get_total_answer(self):
		self.assertEqual(self.stat.get_total_answer(), 0)
		self.stat.update(True, "", False)
		self.assertEqual(self.stat.get_total_answer(), 1)
		self.stat.update(True, "", True)
		self.assertEqual(self.stat.get_total_answer(), 2)
		self.stat.update(False, "", True)
		self.assertEqual(self.stat.get_total_answer(), 3)

	def test_get_success_persent(self):
		self.assertEqual(self.stat.get_success_persent(), 0.0)
		self.stat.update(True, "", False)
		self.assertEqual(self.stat.get_success_persent(), 100.0)
		self.stat.update(False, "", True)
		self.assertEqual(self.stat.get_success_persent(), 100.0)
		self.stat.update(False, "", False)
		self.stat.update(True, "", False)
		self.assertEqual(self.stat.get_success_persent(), 75.0)
		self.stat.update(False, "", False)
		self.assertEqual(self.stat.get_success_persent(), 60.0)

	def test_calc_rating(self):
		today = datetime.date.today()
		dt0   = today.strftime("%Y.%m.%d")
		dt1   = (today - datetime.timedelta(1)).strftime("%Y.%m.%d")

		self.assertAlmostEqual(self.stat.calc_rating(97.0, 10), 201.000, 2)

		self.stat.update(True, dt0, True)
		self.assertAlmostEqual(self.stat.calc_rating(97.0, 10), 84.847, 2)

		self.stat.update(False, dt0, False)
		self.assertAlmostEqual(self.stat.calc_rating(97.0, 10), 183.869, 2)

		self.stat.update(True, dt0, False)
		self.assertAlmostEqual(self.stat.calc_rating(97.0, 10), 92.676, 2)

		self.stat.update(True, dt1, False)
		self.assertAlmostEqual(self.stat.calc_rating(97.0, 10), 94.396, 2)

		for it in range(0, 7):
			self.stat.update(True, dt1, False)
		self.assertAlmostEqual(self.stat.calc_rating(97.0, 10), 6.078, 2)

		for it in range(0, 25):
			self.stat.update(True, dt1, False)
		self.assertAlmostEqual(self.stat.calc_rating(97.0, 10), 0.131, 2)

	def test_calc_rating_not_zero(self):
		today = datetime.date.today()
		dt1   = (today - datetime.timedelta(1)).strftime("%Y.%m.%d")

		for it in range(0, 10):
			self.stat.update(True, dt1, False)
		self.assertAlmostEqual(self.stat.calc_rating(97.0, 10), 0.215, 2)

		for it in range(0, 100):
			self.stat.update(True, dt1, False)
		self.assertAlmostEqual(self.stat.calc_rating(97.0, 10), 0.1, 2)

	def test_update(self):
		dt = "01.02.2010"
		self.stat.update(False, dt, True)
		self.assertEqual(self.stat.success_answer,        1)
		self.assertEqual(self.stat.error_answer,          0)
		self.assertEqual(self.stat.last_lesson_date,      dt)
		self.assertEqual(self.stat.last_lesson_result,    False)

		self.stat.update(False, dt, False)
		self.assertEqual(self.stat.success_answer,        1)
		self.assertEqual(self.stat.error_answer,          1)
		self.assertEqual(self.stat.last_lesson_date,      dt)
		self.assertEqual(self.stat.last_lesson_result,    False)

		self.stat.update(False, dt, False)
		self.assertEqual(self.stat.success_answer,        1)
		self.assertEqual(self.stat.error_answer,          2)
		self.assertEqual(self.stat.last_lesson_date,      dt)
		self.assertEqual(self.stat.last_lesson_result,    False)

	def test_pack_unpack(self):
		self.assertEqual(self.stat.pack(), [0, 0, None, None])
		statistic = (1, 2, "01.02.2010", False)
		self.stat.unpack(statistic)
		self.assertEqual(self.stat.pack(), list(statistic))

if __name__ == "__main__":
	suite = unittest.TestLoader().loadTestsFromTestCase(StatisticTestCase)
	unittest.TextTestRunner(verbosity=2).run(suite)
