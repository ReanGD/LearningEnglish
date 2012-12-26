# -*- coding: utf-8 -*-

import math
import datetime
import unittest


class Statistic:
	""" Хранение статистики по одному типу упражнения у слова
		Умеет:
		-расчитывать рейтинг слова
		-сериализовать/десериализовать свои данные
	"""
	def __init__(self):
		self.success_answer     = 0  # Кол-во правильных ответов
		self.error_answer       = 0  # Кол-во ошибочных ответов
		self.last_lesson_date   = None  # Дата последнего ответа
		self.last_lesson_result = None  # Результат последнего ответа
		self.study_percent      = 0  # Процент изучения [0; 100]

	def __repr__(self):
		fmt = "Statistic(success_answer = {0}; error_answer = {1}; last_lesson_date = {2}; last_lesson_result = {3}; study_percent={4})"
		return fmt.format(self.success_answer, self.error_answer, self.last_lesson_date, self.last_lesson_result, self.study_percent)

	def __eq__(self, other):
		return self.success_answer == other.success_answer and \
				self.error_answer == other.error_answer and \
				self.last_lesson_date == other.last_lesson_date and \
				self.last_lesson_result == other.last_lesson_result and \
				self.study_percent == other.study_percent

	def get_total_answer(self):
		return self.success_answer + self.error_answer

	def get_success_answer(self):
		return self.success_answer

	def get_success_percent(self):
		total = self.get_total_answer()
		if total > 0:
			return float(self.success_answer) / total * 100.0
		else:
			return 0.0

	def get_study_percent(self):
		return self.study_percent

	def is_new(self):
		return self.get_total_answer() == 0

	def calc_rating(self):
		perc = self.get_success_percent()

		# Базовый рейтинг от 1 до 101
		rating = 101.0 - self.get_study_percent()
		# чем больше процент не правильных ответов, тем выше рейтинг
		rating *= (1.01 - min(max(perc / 100.0, 0.0), 1.0))
		# чем чаще слово повторяли, тем меньше рейтинг
		rating *= math.exp(-self.get_total_answer() * 0.07)
		# если последний ответ был неправильным увеличиваем рейтинг
		if self.last_lesson_result == False:
			rating *= 1.5
		# чем дольше слово не повторяли, тем выше рейтинг
		days = 0
		if self.last_lesson_date != None:
			days = (datetime.date.today() - datetime.datetime.strptime(self.last_lesson_date, "%Y.%m.%d").date()).days
		rating *= math.log10(days + 1.0) + 1.0

		return max(rating, 0.1)

	def update(self, is_success, add_percent):
		self.last_lesson_date   = datetime.date.today().strftime("%Y.%m.%d")
		self.last_lesson_result = is_success
		self.study_percent      = max(min(self.study_percent + add_percent, 100), 0)
		if is_success:
			self.success_answer += 1
		else:
			self.error_answer += 1

	def unpack(self, statistic):
		self.success_answer, self.error_answer, self.last_lesson_date, self.last_lesson_result, self.study_percent = statistic

	def pack(self):
		return [self.success_answer, self.error_answer, self.last_lesson_date, self.last_lesson_result, self.study_percent]


class StatisticTestCase(unittest.TestCase):
	"Набор тестов для класса Statistic"

	def setUp(self):
		self.stat = Statistic()

	def test_init(self):
		"Тест конструктора"

		self.assertEqual(self.stat.success_answer,     0)
		self.assertEqual(self.stat.error_answer,       0)
		self.assertEqual(self.stat.last_lesson_date,   None)
		self.assertEqual(self.stat.last_lesson_result, None)
		self.assertEqual(self.stat.study_percent,      0)

	def test_eq(self):
		"Тест оператора сравнения"

		other = Statistic()
		self.assertEqual(self.stat, other)

	def test_get_total_answer(self):
		"Тест на расчет общего кол-ва ответов"

		self.assertEqual(self.stat.get_total_answer(), 0)
		self.stat.update(True, 0)
		self.assertEqual(self.stat.get_total_answer(), 1)
		self.stat.update(True, 0)
		self.assertEqual(self.stat.get_total_answer(), 2)
		self.stat.update(False, 0)
		self.assertEqual(self.stat.get_total_answer(), 3)

	def test_get_success_percent(self):
		"Тест на расчет процента положительных ответов"

		self.assertEqual(self.stat.get_success_percent(), 0.0)
		self.stat.update(True, 0)
		self.assertEqual(self.stat.get_success_percent(), 100.0)
		self.stat.update(False, 0)
		self.stat.update(True, 0)
		self.stat.update(True, 0)
		self.assertEqual(self.stat.get_success_percent(), 75.0)
		self.stat.update(False, 0)
		self.assertEqual(self.stat.get_success_percent(), 60.0)

	def test_get_study_percent(self):
		"Тест на расчет процента изучения слова"

		self.assertEqual(self.stat.get_study_percent(), 0.0)
		self.stat.update(True, 0)
		self.assertEqual(self.stat.get_study_percent(), 0.0)
		self.stat.update(True, 10)
		self.assertEqual(self.stat.get_study_percent(), 10.0)
		self.stat.update(True, 100)
		self.assertEqual(self.stat.get_study_percent(), 100.0)
		self.stat.update(True, -10)
		self.assertEqual(self.stat.get_study_percent(), 90.0)
		self.stat.update(True, -100)
		self.assertEqual(self.stat.get_study_percent(), 0.0)

	def test_is_new(self):
		"Тест функции is_new"

		self.assertEqual(self.stat.is_new(), True)
		self.stat.update(True, 0)
		self.assertEqual(self.stat.is_new(), False)

	def test_calc_rating(self):
		"Тест функции расчета рейтинга"

		yesterday = (datetime.date.today() - datetime.timedelta(1)).strftime("%Y.%m.%d")

		self.assertAlmostEqual(self.stat.calc_rating(), 102.010, 2)

		self.stat.update(True, 10)
		self.assertAlmostEqual(self.stat.calc_rating(), 0.848, 2)

		self.stat.update(False, -30)
		self.assertAlmostEqual(self.stat.calc_rating(), 67.170, 2)

		self.stat.update(True, 10)
		self.assertAlmostEqual(self.stat.calc_rating(), 25.325, 2)

		self.stat.update(True, 10)
		self.stat.last_lesson_date = yesterday
		self.assertAlmostEqual(self.stat.calc_rating(), 20.708, 2)

		for it in range(0, 7):
			self.stat.update(True, 10)
			self.stat.last_lesson_date = yesterday
		self.assertAlmostEqual(self.stat.calc_rating(), 0.668, 2)

		for it in range(0, 25):
			self.stat.update(True, 10)
			self.stat.last_lesson_date = yesterday
		self.assertAlmostEqual(self.stat.calc_rating(), 0.100, 2)

		self.stat.update(False, -30)
		self.assertAlmostEqual(self.stat.calc_rating(), 0.223, 2)

	def test_calc_rating_not_zero(self):
		"Тест на то, что функция расчета рейтинга не возвращает ноль"

		for it in range(0, 10):
			self.stat.update(True, 10)
		self.assertAlmostEqual(self.stat.calc_rating(), 0.1, 2)

		for it in range(0, 100):
			self.stat.update(True, 10)
		self.assertAlmostEqual(self.stat.calc_rating(), 0.1, 2)

	def test_update(self):
		"Тест функции обновления статистики"

		dt = datetime.date.today().strftime("%Y.%m.%d")
		self.stat.update(True, 10)
		self.assertEqual(self.stat.success_answer,        1)
		self.assertEqual(self.stat.error_answer,          0)
		self.assertEqual(self.stat.last_lesson_date,      dt)
		self.assertEqual(self.stat.last_lesson_result,    True)
		self.assertEqual(self.stat.study_percent,         10)

		self.stat.update(False, -50)
		self.assertEqual(self.stat.success_answer,        1)
		self.assertEqual(self.stat.error_answer,          1)
		self.assertEqual(self.stat.last_lesson_date,      dt)
		self.assertEqual(self.stat.last_lesson_result,    False)
		self.assertEqual(self.stat.study_percent,         0)

		self.stat.update(False, -50)
		self.assertEqual(self.stat.success_answer,        1)
		self.assertEqual(self.stat.error_answer,          2)
		self.assertEqual(self.stat.last_lesson_date,      dt)
		self.assertEqual(self.stat.last_lesson_result,    False)
		self.assertEqual(self.stat.study_percent,         0)

	def test_pack_unpack(self):
		"Тест функции упаковки и распаковки класса"

		self.assertEqual(self.stat.pack(), [0, 0, None, None, 0])
		statistic = (1, 2, "01.02.2010", False, 10)
		self.stat.unpack(statistic)
		self.assertEqual(self.stat.pack(), list(statistic))

if __name__ == "__main__":
	suite = unittest.TestLoader().loadTestsFromTestCase(StatisticTestCase)
	unittest.TextTestRunner(verbosity=2).run(suite)
