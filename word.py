# -*- coding: utf-8 -*-

import re
import unittest
import statistic

en_to_ru_write = 0
ru_to_en_write = 1

reg_cmnt         = re.compile("\(.*?\)")
reg_no_sign_part = re.compile("\[.*?\]")


class WordInfo:
	def __init__(self, word, transcription):
		self.word          = word
		self.transcription = transcription

	def __eq__(self, other):
		return self.word == other.word and self.transcription == other.transcription


class Word:
	"""	Хранение информации по одному слову:
		английский вариант, перевод, транскрипция + статистика и рейтинг
		Умеет:
		-парсить сырые данные (те, что сохранены в словаре) во внутренний формат
		-проверять правильность ответа и в зависимости от результата обновлять статистику
		-сериализовать/десериализовать статистику по слову
	"""
	def __init__(self):
		self.en_word       = ""  # Английское слово, которое будет отображаться пользователю
		self.en_word_list  = []  # Распарсенное английское слово
		self.transcription = ""  # Транскрипция
		self.ru_source     = []  # Вспомогательный массив русских слов используемый только на этапе загрузки
		self.ru_word       = ""  # Русское слово, которое будет отображаться пользователю
		self.ru_word_list  = []  # Распарсенное русское слово
		self.rating        = 0   # Рейтинг слова, влияет на вероятность появления его в упражнении
		self.stat          = {en_to_ru_write: statistic.Statistic(), ru_to_en_write: statistic.Statistic()}  # Ссылка на статистику по слову
		self.first         = False  # Указывает на то, что слово еще ни разу не изучалось

	@staticmethod
	def convert_spec_chars(s):
		return s.replace(u"ё", u"е")

	@staticmethod
	def prepare_show_words(word_list):
		filtered_list = []
		norm_list     = []
		for it in map(lambda x: x.replace("[", "").replace("]", ""), word_list):
			norm_word = Word.convert_spec_chars(it.lower())
			if norm_word not in norm_list:
				norm_list.append(norm_word)
				filtered_list.append(it)
		return ", ".join(filtered_list)

	def add_value(self, en_word, transcription, ru_word):
		if self.en_word == "":
			en_source = map(lambda x: x.strip(), en_word.split(","))
			self.en_word = Word.prepare_show_words(en_source)
			self.en_word_list = map(lambda x: reg_no_sign_part.sub(".*?", reg_cmnt.sub("", x.lower()).strip()), en_source)
		if self.transcription == "":
			self.transcription = "[%s]" % transcription.strip()
		self.ru_source += map(lambda x: x.strip(), ru_word.split(","))

		self.ru_word = Word.prepare_show_words(self.ru_source)
		self.ru_word_list = map(lambda x: Word.convert_spec_chars(reg_no_sign_part.sub(".*?", reg_cmnt.sub("", x.lower()).strip())), self.ru_source)

	def set_rating(self, value):
		self.rating = value

	def get_rating(self):
		return self.rating

	def set_first(self):
		self.first = True

	def is_first(self):
		return self.first

	def source_data(self, type_pr):
		if type_pr == en_to_ru_write:
			return WordInfo(self.en_word, self.transcription)
		else:
			return WordInfo(self.ru_word, "")

	def check_ru(self, answer):
		answer = Word.convert_spec_chars(answer)
		for it in self.ru_word_list:
			if re.match(it + "\Z", answer) != None:
				return True
		return False

	def check_en(self, answer):
		for it in self.en_word_list:
			if re.match(it + "\Z", answer) != None:
				return True
		return False

	def check(self, answer, type_pr):
		answer = answer.strip().lower()
		if type_pr == en_to_ru_write:
			is_success = self.check_ru(answer)
			return is_success, WordInfo(self.ru_word, "")
		else:
			is_success = self.check_en(answer)
			return is_success, WordInfo(self.en_word, self.transcription)

	def update_stat(self, is_success, dt, type_pr):
		self.stat[type_pr].update(is_success, dt, self.first)

	def get_show_info(self):
		return (self.en_word, self.transcription, self.ru_word)

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
	"Набор тестов по классу Word"

	def setUp(self):
		self.word = Word()
		self.hello_tr = u"\'he\'ləu"
		self.hello_tr_out = u"[\'he\'ləu]"

	def test_init(self):
		self.assertEqual(self.word.en_word,       u"")
		self.assertEqual(self.word.en_word_list,  [])
		self.assertEqual(self.word.transcription, u"")
		self.assertEqual(self.word.ru_word,       u"")
		self.assertEqual(self.word.ru_word_list,  [])
		self.assertEqual(self.word.rating,        0)
		self.assertEqual(len(self.word.stat),     2)
		self.assertEqual(self.word.stat[en_to_ru_write], statistic.Statistic())
		self.assertEqual(self.word.stat[ru_to_en_write], statistic.Statistic())

	def test_add_value(self):
		en_word       = u"Hello"
		ru_word0      = u"привет"
		self.word.add_value(u"  " + en_word + u"  ", u"  " + self.hello_tr + u"  ", u"  " + ru_word0 + u"  ")
		self.assertEqual(self.word.en_word,       en_word)
		self.assertEqual(self.word.en_word_list,  [en_word.lower()])
		self.assertEqual(self.word.transcription, self.hello_tr_out)
		self.assertEqual(self.word.ru_word,       ru_word0)
		self.assertEqual(self.word.ru_word_list,  [ru_word0])

		ru_word1 = u"приветствие"
		self.word.add_value(u"  " + en_word + u"  ", u"  " + self.hello_tr + u"  ", u"  " + ru_word1 + u"  ")
		self.assertEqual(self.word.en_word,       en_word)
		self.assertEqual(self.word.en_word_list,  [en_word.lower()])
		self.assertEqual(self.word.transcription, self.hello_tr_out)
		self.assertEqual(self.word.ru_word,       ru_word0 + u", " + ru_word1)
		self.assertEqual(self.word.ru_word_list,  [ru_word0, ru_word1])

	def test_add_value_double_ru(self):
		en_word       = u"Hello"
		ru_word0      = u"привет"
		ru_word1      = u"алло"

		self.word.add_value(u"  " + en_word + u"  ", u"  " + self.hello_tr + u"  ", u"  " + ru_word0 + u", " + ru_word1 + u"  ")
		self.assertEqual(self.word.en_word,       en_word)
		self.assertEqual(self.word.en_word_list,  [en_word.lower()])
		self.assertEqual(self.word.transcription, self.hello_tr_out)
		self.assertEqual(self.word.ru_word,       ru_word0 + u", " + ru_word1)
		self.assertEqual(self.word.ru_word_list,  [ru_word0, ru_word1])

		ru_word2 = u"приветствие"
		ru_word3 = u"оклик"
		self.word.add_value(u"  " + en_word + u"  ", None, u"  " + ru_word2 + u", " + ru_word3 + u"  ")
		self.assertEqual(self.word.en_word,       en_word)
		self.assertEqual(self.word.en_word_list,  [en_word.lower()])
		self.assertEqual(self.word.transcription, self.hello_tr_out)
		self.assertEqual(self.word.ru_word,       ru_word0 + u", " + ru_word1 + u", " + ru_word2 + u", " + ru_word3)
		self.assertEqual(self.word.ru_word_list,  [ru_word0, ru_word1, ru_word2, ru_word3])

	def test_add_value_cmnt(self):
		"Тест на наличие комментариев в английском и русском словах"

		self.word.add_value(u"  Hello (Comment) ,  Hi  ", u"  \'he\'ləu  ", u"  привет (Здоровается) ,  алло  ")
		self.assertEqual(self.word.en_word,       u"Hello (Comment), Hi")
		self.assertEqual(self.word.en_word_list,  [u"hello", u"hi"])
		self.assertEqual(self.word.transcription, u"[\'he\'ləu]")
		self.assertEqual(self.word.ru_word,       u"привет (Здоровается), алло")
		self.assertEqual(self.word.ru_word_list,  [u"привет", u"алло"])

	def test_add_value_no_sign_part(self):
		"Тест на присутствие необязательных частей в англиском и русском словах"

		self.word.add_value(u"  He[llo], H[al]l[o]  ", u"  \'he\'ləu  ", u"привет[ствие],ок[лик]ат[ь]")
		self.assertEqual(self.word.en_word,       u"Hello, Hallo")
		self.assertEqual(self.word.en_word_list,  [u"he.*?", u"h.*?l.*?"])
		self.assertEqual(self.word.transcription, u"[\'he\'ləu]")
		self.assertEqual(self.word.ru_word,       u"приветствие, окликать")
		self.assertEqual(self.word.ru_word_list,  [u"привет.*?", u"ок.*?ат.*?"])

	def test_add_value_with_duplicate(self):
		en_word       = u"Hello"

		self.word.add_value(en_word, self.hello_tr, u"привет")
		self.word.add_value(en_word, self.hello_tr, u"привет")
		self.word.add_value(en_word, self.hello_tr, u"пРивет")
		self.word.add_value(en_word, self.hello_tr, u"пРиВет")
		self.word.add_value(en_word, self.hello_tr, u"пРи[Вет]")
		self.word.add_value(en_word, self.hello_tr, u"пРиВет(1)")
		self.word.add_value(en_word, self.hello_tr, u"пРиВет(1)")
		self.assertEqual(self.word.en_word,       en_word)
		self.assertEqual(self.word.en_word_list,  [en_word.lower()])
		self.assertEqual(self.word.transcription, self.hello_tr_out)
		self.assertEqual(self.word.ru_word,       u"привет, пРиВет(1)")
		self.assertEqual(self.word.ru_word_list,  [u"привет", u"привет", u"привет", u"привет", u"при.*?", u"привет", u"привет"])

	def test_rating(self):
		rating = 51.879
		self.word.set_rating(rating)
		self.assertEqual(self.word.get_rating(), rating)

	def test_source_data(self):
		en_word       = u"Hello"
		ru_word       = u"привет"
		self.word.add_value(en_word, self.hello_tr, ru_word)
		self.assertEqual(self.word.source_data(en_to_ru_write), WordInfo(en_word, self.hello_tr_out))
		self.assertEqual(self.word.source_data(ru_to_en_write), WordInfo(ru_word, u""))

	def test_check(self):
		"Тест на то, что многовариантные слова на аглийском и русском, правильно проходят проверку"

		self.word.add_value(u"Hello, Hallo", u"  \'he\'ləu  ", u"привет,алло")

		ru_ans = WordInfo(u"привет, алло", u"")
		self.assertEqual(self.word.check(u"  ПРИВЕТ    ", en_to_ru_write), (True, ru_ans))
		self.assertEqual(self.word.check(u"  АЛЛО      ", en_to_ru_write), (True, ru_ans))
		self.assertEqual(self.word.check(u"error_answer", en_to_ru_write), (False, ru_ans))

		en_ans = WordInfo(u"Hello, Hallo", u"[\'he\'ləu]")
		self.assertEqual(self.word.check(u"  HELLO     ", ru_to_en_write), (True, en_ans))
		self.assertEqual(self.word.check(u"  HALLO     ", ru_to_en_write), (True, en_ans))
		self.assertEqual(self.word.check(u"error_answer", ru_to_en_write), (False, en_ans))

	def test_check_cmnt(self):
		"Тест на то, что слова на аглийском и русском с комментариями, правильно проходят проверку"

		self.word.add_value(u"Hello(Comment), Hallo", u"  \'he\'ləu  ", u"привет(Здоровается),алло")

		ru_ans = WordInfo(u"привет(Здоровается), алло", u"")
		self.assertEqual(self.word.check(u"  ПРИВЕТ    ", en_to_ru_write), (True, ru_ans))
		self.assertEqual(self.word.check(u"  АЛЛО      ", en_to_ru_write), (True, ru_ans))
		self.assertEqual(self.word.check(u"error_answer", en_to_ru_write), (False, ru_ans))

		en_ans = WordInfo(u"Hello(Comment), Hallo", u"[\'he\'ləu]")
		self.assertEqual(self.word.check(u"  HELLO     ", ru_to_en_write), (True, en_ans))
		self.assertEqual(self.word.check(u"  HALLO     ", ru_to_en_write), (True, en_ans))
		self.assertEqual(self.word.check(u"error_answer", ru_to_en_write), (False, en_ans))

	def test_check_no_sign_part(self):
		"Тест на то, что слова на аглийском и русском с необязательными частями, правильно проходят проверку"

		self.word.add_value(u"  He[llo], H[al]l[o]  ", u"  \'he\'ləu  ", u"привет[ствие],ок[лик]ат[ь]")

		ru_ans = WordInfo(u"приветствие, окликать", u"")
		self.assertEqual(self.word.check(u"привет        ", en_to_ru_write), (True, ru_ans))
		self.assertEqual(self.word.check(u"приветaddtext ", en_to_ru_write), (True, ru_ans))
		self.assertEqual(self.word.check(u"окат          ", en_to_ru_write), (True, ru_ans))
		self.assertEqual(self.word.check(u"окликaddатadd]", en_to_ru_write), (True, ru_ans))
		self.assertEqual(self.word.check(u"привит        ", en_to_ru_write), (False, ru_ans))
		self.assertEqual(self.word.check(u"окар          ", en_to_ru_write), (False, ru_ans))

		en_ans = WordInfo(u"Hello, Hallo", u"[\'he\'ləu]")
		self.assertEqual(self.word.check(u"HELLO    ", ru_to_en_write), (True, en_ans))
		self.assertEqual(self.word.check(u"HELLO123 ", ru_to_en_write), (True, en_ans))
		self.assertEqual(self.word.check(u"HE123    ", ru_to_en_write), (True, en_ans))
		self.assertEqual(self.word.check(u"HALLO    ", ru_to_en_write), (True, en_ans))
		self.assertEqual(self.word.check(u"HL       ", ru_to_en_write), (True, en_ans))
		self.assertEqual(self.word.check(u"H123     ", ru_to_en_write), (False, en_ans))
		self.assertEqual(self.word.check(u"123l123  ", ru_to_en_write), (False, en_ans))

	def test_check_special_char_in_word(self):
		en_word   = u"Yellow"
		return_ru = u"жёлтый"
		self.word.add_value(en_word, u"", return_ru)

		ru_ans = WordInfo(return_ru, u"")
		self.assertEqual(self.word.check(u"желтый", en_to_ru_write), (True, ru_ans))
		self.assertEqual(self.word.check(u"жёлтый", en_to_ru_write), (True, ru_ans))

	def test_check_special_char_in_answer(self):
		en_word   = u"Yellow"
		return_ru = u"желтый"
		self.word.add_value(en_word, u"", return_ru)

		ru_ans = WordInfo(return_ru, u"")
		self.assertEqual(self.word.check(u"желтый", en_to_ru_write), (True, ru_ans))
		self.assertEqual(self.word.check(u"жёлтый", en_to_ru_write), (True, ru_ans))

	def test_is_load(self):
		self.assertEqual(self.word.is_load(), False)

		en_word       = u"Hello"
		ru_word       = u"привет"
		self.word.add_value(en_word, self.hello_tr, ru_word)
		self.assertEqual(self.word.is_load(), True)

	def test_unpack(self):
		statistic_in = {str(en_to_ru_write): [3, 2, "01.02.2010", False], str(ru_to_en_write): [3, 1, "02.03.2011", False]}

		st0 = statistic.Statistic()
		st0.update(True, "01.02.2010", False)
		st0.update(False, "01.02.2010", False)
		st0.update(False, "01.02.2010", True)
		st0.update(True, "01.02.2010", True)
		st0.update(False, "01.02.2010", False)

		st1 = statistic.Statistic()
		st1.update(True, "02.03.2011", False)
		st1.update(False, "02.03.2011", False)
		st1.update(True, "02.03.2011", True)
		st1.update(False, "02.03.2011", True)

		self.word.unpack(statistic_in)
		self.assertEqual(self.word.stat[en_to_ru_write], st0)
		self.assertEqual(self.word.stat[ru_to_en_write], st1)

	def test_pack(self):
		statistic_out = {en_to_ru_write: [1, 2, "01.02.2010", False], ru_to_en_write: [2, 1, "02.03.2011", True]}
		self.word.update_stat(True, "01.02.2010", en_to_ru_write)
		self.word.update_stat(False, "01.02.2010", en_to_ru_write)
		self.word.update_stat(False, "01.02.2010", en_to_ru_write)
		self.word.update_stat(False, "02.03.2011", ru_to_en_write)
		self.word.update_stat(True, "02.03.2011", ru_to_en_write)
		self.word.update_stat(True, "02.03.2011", ru_to_en_write)
		self.assertEqual(self.word.pack(), statistic_out)

if __name__ == "__main__":
	suite = unittest.TestLoader().loadTestsFromTestCase(WordTestCase)
	unittest.TextTestRunner(verbosity=2).run(suite)
