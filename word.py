# -*- coding: utf-8 -*-

import re
import unittest
import statistic

en_to_ru_write = 0
ru_to_en_write = 1

reg_cmnt = re.compile("\(.*?\)")

class Word:
	def __init__(self):
		self.en_word		= ""
		self.transcription	= ""
		self.ru_word		= ""
		self.ru_word_list	= []
		self.rating			= 0
		self.stat 			= {en_to_ru_write : statistic.Statistic(), ru_to_en_write : statistic.Statistic()}

	def add_value(self, en_word, transcription, ru_word):
		if self.en_word == "":
			self.en_word		= en_word.strip()
		if self.transcription == "":
			self.transcription	= "[%s]" % transcription.strip()
		if self.ru_word != "":
			ru_word = self.ru_word + "," + ru_word
		word_list = map(lambda x : x.strip(), ru_word.split(","))
		self.ru_word = ", ".join(word_list)
		self.ru_word_list = map(lambda x : reg_cmnt.sub("", x.lower()).strip(), word_list)		

	def set_rating(self, value):
		self.rating = value

	def get_rating(self):
		return self.rating

	def source_data(self, type_pr):
		if type_pr == en_to_ru_write:
			return self.en_word, self.transcription
		else:
			return self.ru_word, ""

	def check(self, answer, type_pr):
		answer = answer.strip().lower()
		if type_pr == en_to_ru_write:
			is_success = (answer in self.ru_word_list)
			return is_success, self.ru_word, ""
		else:
			is_success = (answer == self.en_word.strip().lower())
			return is_success, self.en_word, self.transcription

	def update_stat(self, is_success, dt, type_pr):
		self.stat[type_pr].update(is_success, dt)

	def is_load(self):
		return self.transcription != ""

	def get_stat(self, type_pr):
		return self.stat[type_pr]

	def unpack(self, statistic):
		for it in statistic:
			it_int = int(it)
			if it_int not in self.stat.keys():
				self.stat[it_int] = statistic.Statistic()
			self.stat[it_int].unpack(statistic[it])

	def pack(self):
		data = {}
		for it in self.stat:
			data[it] = self.stat[it].pack()
		return data

class WordTestCase(unittest.TestCase):
	def setUp(self):
		self.word = Word()
		self.hello_tr = "\'he\'ləu"
		self.hello_tr_out = "[\'he\'ləu]"

	def test_init(self):
		self.assertEqual(self.word.en_word,       "")
		self.assertEqual(self.word.transcription, "")
		self.assertEqual(self.word.ru_word,       "")
		self.assertEqual(self.word.ru_word_list,  [])
		self.assertEqual(self.word.rating,        0)
		self.assertEqual(len(self.word.stat),     2)
		self.assertEqual(self.word.stat[en_to_ru_write], statistic.Statistic())
		self.assertEqual(self.word.stat[ru_to_en_write], statistic.Statistic())

	def test_add_value(self):
		en_word       = "Hello"
		ru_word0      = "привет"
		self.word.add_value("  "+en_word+"  ", "  "+self.hello_tr+"  ", "  "+ru_word0+"  ")
		self.assertEqual(self.word.en_word,       en_word)
		self.assertEqual(self.word.transcription, self.hello_tr_out)
		self.assertEqual(self.word.ru_word,       ru_word0)
		self.assertEqual(self.word.ru_word_list,  [ru_word0])
		
		ru_word1 = "приветствие"
		self.word.add_value("  "+en_word+"  ", "  "+self.hello_tr+"  ", "  "+ru_word1+"  ")
		self.assertEqual(self.word.en_word,       en_word)
		self.assertEqual(self.word.transcription, self.hello_tr_out)
		self.assertEqual(self.word.ru_word,       ru_word0+", "+ru_word1)
		self.assertEqual(self.word.ru_word_list,  [ru_word0, ru_word1])

	def test_add_value_double_ru(self):
		en_word       = "Hello"
		ru_word0      = "привет"
		ru_word1      = "алло"
		
		self.word.add_value("  "+en_word+"  ", "  "+self.hello_tr+"  ", "  "+ru_word0+", "+ru_word1+"  ")
		self.assertEqual(self.word.en_word,       en_word)
		self.assertEqual(self.word.transcription, self.hello_tr_out)
		self.assertEqual(self.word.ru_word,       ru_word0+", "+ru_word1)
		self.assertEqual(self.word.ru_word_list,  [ru_word0, ru_word1])
		
		ru_word2 = "приветствие"
		ru_word3 = "оклик"
		self.word.add_value("  "+en_word+"  ", None, "  "+ru_word2+", "+ru_word3+"  ")
		self.assertEqual(self.word.en_word,       en_word)
		self.assertEqual(self.word.transcription, self.hello_tr_out)
		self.assertEqual(self.word.ru_word,       ru_word0+", "+ru_word1+", "+ru_word2+", "+ru_word3)
		self.assertEqual(self.word.ru_word_list,  [ru_word0, ru_word1, ru_word2, ru_word3])

	def test_add_value_cmnt(self):
		en_word       = "Hello"
		ru_word0      = "привет"
		ru_word0_cmnt = "(Здоровается)"
		ru_word1      = "алло"
		
		self.word.add_value("  "+en_word+"  ", "  "+self.hello_tr+"  ", "  "+ru_word0+" "+ru_word0_cmnt+" , "+ru_word1+"  ")
		self.assertEqual(self.word.en_word,       en_word)
		self.assertEqual(self.word.transcription, self.hello_tr_out)
		self.assertEqual(self.word.ru_word,       ru_word0+" "+ru_word0_cmnt+", "+ru_word1)
		self.assertEqual(self.word.ru_word_list,  [ru_word0, ru_word1])		

	def test_rating(self):
		rating = 51.879
		self.word.set_rating(rating)
		self.assertEqual(self.word.get_rating(), rating)

	def test_source_data(self):
		en_word       = "Hello"
		ru_word       = "привет"
		self.word.add_value(en_word, self.hello_tr, ru_word)
		self.assertEqual(self.word.source_data(en_to_ru_write), (en_word, self.hello_tr_out))
		self.assertEqual(self.word.source_data(ru_to_en_write), (ru_word, ""))

	def test_check(self):
		en_word       = "Hello"
		ru_word0      = "привет"
		ru_word1      = "алло"		
		self.word.add_value(en_word, self.hello_tr, ru_word0+","+ru_word1)

		self.assertEqual(self.word.check("  "+ru_word0.upper()+"  ", en_to_ru_write), (True, ru_word0+", "+ru_word1, ""))
		self.assertEqual(self.word.check("  "+ru_word1.upper()+"  ", en_to_ru_write), (True, ru_word0+", "+ru_word1, ""))
		self.assertEqual(self.word.check("error_answer", en_to_ru_write), (False, ru_word0+", "+ru_word1, ""))

		self.assertEqual(self.word.check("  "+en_word.upper()+"  ", ru_to_en_write), (True, en_word, self.hello_tr_out))
		self.assertEqual(self.word.check("error_answer", ru_to_en_write), (False, en_word, self.hello_tr_out))

	def test_is_load(self):
		self.assertEqual(self.word.is_load(), False)

		en_word       = "Hello"
		ru_word       = "привет"
		self.word.add_value(en_word, self.hello_tr, ru_word)
		self.assertEqual(self.word.is_load(), True)

	def test_unpack(self):
		statistic_in = {str(en_to_ru_write) : [1, 2, "01.02.2010", False], str(ru_to_en_write) : [2, 1, "02.03.2011", True]}

		st0 = statistic.Statistic()
		st0.update(True, "01.02.2010")
		st0.update(False, "01.02.2010")
		st0.update(False, "01.02.2010")

		st1 = statistic.Statistic()
		st1.update(True, "02.03.2011")
		st1.update(False, "02.03.2011")
		st1.update(True, "02.03.2011")

		self.word.unpack(statistic_in)
		self.assertEqual(self.word.stat[en_to_ru_write], st0)
		self.assertEqual(self.word.stat[ru_to_en_write], st1)

	def test_pack(self):
		statistic_out = {en_to_ru_write : [1, 2, "01.02.2010", False], ru_to_en_write : [2, 1, "02.03.2011", True]}
		self.word.update_stat(True, "01.02.2010", en_to_ru_write)
		self.word.update_stat(False, "01.02.2010", en_to_ru_write)
		self.word.update_stat(False, "01.02.2010", en_to_ru_write)
		self.word.update_stat(False, "02.03.2011", ru_to_en_write)
		self.word.update_stat(True, "02.03.2011", ru_to_en_write)
		self.word.update_stat(True, "02.03.2011", ru_to_en_write)
		self.assertEqual(self.word.pack(), statistic_out)

if __name__=="__main__":
	suite = unittest.TestLoader().loadTestsFromTestCase(WordTestCase)
	unittest.TextTestRunner(verbosity=2).run(suite)