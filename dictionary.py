# -*- coding: utf-8 -*-

import json
import os.path
import word
import global_stat
import unittest


class ErrDict(Exception):
	def __init__(self, value, loc_res_msg):
		self.value = value
		self.loc_res_msg = loc_res_msg

	def __str__(self):
		return repr(self.value)


class Dict:
	def __init__(self, cfg):
		self.words = {}
		self.cfg   = cfg

	def get_word_by_key(self, en):
		w = self.words.get(en)
		if not w:
			w = self.words[en] = word.Word()
		return w

	def reload_dict_s(self, text):
		self.words = {}
		for it in json.loads(text):
			en = it[0]
			tr = it[1]
			ru = it[2]
			self.get_word_by_key(en).add_value(en, tr, ru)

	def reload_dict(self, path):
		self.reload_dict_s(open(path).read())

	def reload_stat_s(self, text):
		stat_json = json.loads(text)
		version   = stat_json["version"]
		if version != 1:
			raise ErrDict("Error stat file version", "err_stat_version")
		data      = stat_json["data"]
		for it in data:
			self.get_word_by_key(it).unpack(data[it])

	def reload_stat(self, path):
		if os.path.exists(path):
			self.reload_stat_s(open(path).read())

	def loaded_words(self, type_pr):
		return [(it, it.get_stat(type_pr)) for it in self.words.values() if it.is_load()]

	def global_statistic(self, min_percent, min_success_cnt):
		stat = global_stat.GlobalStatistic(min_percent, min_success_cnt)
		for it in self.words.values():
			if it.is_load():
				stat.add_word(it, it.get_stat(word.en_to_ru_write), it.get_stat(word.ru_to_en_write))
		return stat

	def _rename_check(self, old_en, new_en, new_ru):
		if len(new_en) == 0:
			raise ErrDict("Error word is empty", "err_en_word_empty")

		if len(new_ru) == 0:
			raise ErrDict("Error word is empty", "err_ru_word_empty")

		if old_en not in self.words.keys():
			raise ErrDict("Error find word", "err_find_en_word")

		new_en = new_en.lower()
		if old_en.strip().lower() != new_en:
			if new_en in map(lambda x: x.strip().lower(), self.words.keys()):
				raise ErrDict("Dublicate in load dict", "err_dublicate_en_word")

	def _rename_in_json_dict(self, old_en, new_en, new_tr, new_ru, json_dict):
		is_find = False
		old_en = old_en.strip().lower()
		lower_en = new_en.lower()
		for it in json_dict:
			en = it[0].strip().lower()
			if en == old_en:
				it[0], it[1], it[2] = new_en, new_tr, new_ru
				is_find = True
			elif en == lower_en:
				raise ErrDict("Dublicate in file dict", "err_dublicate_en_word")
		if not is_find:
			json_dict.append([new_en, new_tr, new_ru])
		return json_dict

	def _rename_in_dict(self, old_en, new_en, new_tr, new_ru):
		w = self.words.pop(old_en)
		w.rename(new_en, new_tr, new_ru)
		self.words[new_en] = w

	def rename_word(self, old_en, new_en, new_tr, new_ru):
		new_en = new_en.strip()
		new_tr = new_tr.strip()
		new_ru = new_ru.strip()
		self._rename_check(old_en, new_en, new_ru)

		cfg_dict = self.cfg.reload()

		import codecs
		json_dict = json.load(codecs.open(cfg_dict["path_to_dict"], "rt", "utf-8"))
		json_dict = self._rename_in_json_dict(old_en, new_en, new_tr, new_ru, json_dict)
		self.reload_stat(cfg_dict["path_to_stat"])
		self._rename_in_dict(old_en, new_en, new_tr, new_ru)
		json.dump(json_dict, codecs.open(cfg_dict["path_to_dict"], "wt", "utf-8"), indent=2, ensure_ascii=False)
		self.save_stat(cfg_dict["path_to_stat"])

	def words_for_lesson(self, cnt_study_words, min_percent, min_success_cnt, type_pr):
		learned_words = []
		studied_words = []
		for wrd, stat in self.loaded_words(type_pr):
			if stat.get_total_answer() > 0:
				if stat.get_success_persent() >= min_percent and stat.get_total_answer() >= min_success_cnt:
					learned_words.append(wrd)
				else:
					studied_words.append(wrd)

		# дополняем изучаемыми/изученными словами из другого направления перевода
		if len(studied_words) < cnt_study_words:
			inv_type_pr = word.ru_to_en_write if type_pr == word.en_to_ru_write else word.en_to_ru_write
			for wrd, stat in self.loaded_words(inv_type_pr):
				if stat.get_total_answer() > 0 and wrd not in (learned_words + studied_words):
					studied_words.append(wrd)
					if len(studied_words) == cnt_study_words:
						break

		# дополняем ни разу не изучаемыми словами
		if len(studied_words) < cnt_study_words:
			for wrd, stat in self.loaded_words(type_pr):
				if stat.get_total_answer() == 0 and wrd not in (learned_words + studied_words):
					wrd.set_first()
					studied_words.append(wrd)
					if len(studied_words) == cnt_study_words:
						break

		studied_words.sort(key=lambda it: it.get_stat(type_pr).get_success_persent())
		studied_words = studied_words[:cnt_study_words]

		lesson_words = learned_words + studied_words
		for it in lesson_words:
			rating = it.get_stat(type_pr).calc_rating(min_percent, min_success_cnt)
			it.set_rating(rating)
		return lesson_words

	def save_stat(self, path_to_stat):
		data = {}
		for it in self.words:
			data[it] = self.words[it].pack()
		stat_json = {"version": 1, "data": data}
		json.dump(stat_json, open(path_to_stat, "wb"), indent=2)


class DictTestCase(unittest.TestCase):
	def setUp(self):
		self.dict_obj = Dict(None)

	def create_word_data(self, num):
		return ["en" + str(num), "tr" + str(num), "ru" + str(num)]

	def create_word_stat(self, num):
		key   = "en" + str(num)
		date  = "2012.01"
		stat1 = [num * 1,  num * 10, date + str(num),     num % 2 == 0]
		stat2 = [num * 20, num * 30, date + str(num + 1), num % 2 == 1]
		return [key, {"0": stat1, "1": stat2}]

	def json_dict(self, interval_from, interval_to):
		return [self.create_word_data(i) for i in range(interval_from, interval_to)]

	def load_dict(self, interval_from, interval_to):
		txt_dict = json.dumps(self.json_dict(interval_from, interval_to))
		self.dict_obj.reload_dict_s(txt_dict)

	def load_stat(self, interval_from, interval_to, version):
		json_data = dict([self.create_word_stat(i) for i in range(interval_from, interval_to)])
		json_stat = {"version": version, "data": json_data}
		self.dict_obj.reload_stat_s(json.dumps(json_stat))

	def assertLoad(self, num):
		dt = self.create_word_data(num)
		wrd_info = self.dict_obj.get_word_by_key("en" + str(num)).get_show_info()
		self.assertEqual((dt[0], "[%s]" % dt[1], dt[2]), wrd_info)

	def assertNotLoad(self, num):
		wrd_info = self.dict_obj.get_word_by_key("en" + str(num)).get_show_info()
		self.assertEqual(("", "", ""), wrd_info)

	def assertLoadStat(self, num):
		wrd1 = word.Word()
		wrd1.unpack(self.create_word_stat(num)[1])
		wrd2 = self.dict_obj.get_word_by_key("en" + str(num))
		self.assertEqual(wrd1.get_stat(0), wrd2.get_stat(0))
		self.assertEqual(wrd1.get_stat(1), wrd2.get_stat(1))

	def test_reload_dict(self):
		interval_from = 0
		interval_to   = 5
		self.load_dict(interval_from, interval_to)

		for i in range(interval_from, interval_to):
			self.assertLoad(i)

	def test_reload_dict_err_key(self):
		interval_from = 0
		interval_to   = 5
		self.load_dict(interval_from, interval_to)

		for i in range(interval_to, interval_to * 2):
			self.assertNotLoad(i)

	def test_reload_dict_double_reload(self):
		interval_from1 = 0
		interval_to1   = 5
		self.load_dict(interval_from1, interval_to1)
		interval_from2 = 3
		interval_to2   = 8
		self.load_dict(interval_from2, interval_to2)

		for i in range(interval_from1, interval_from2):
			self.assertNotLoad(i)

		for i in range(interval_from2, interval_to2):
			self.assertLoad(i)

	def test_reload_stat(self):
		interval_from = 0
		interval_to   = 5
		self.load_dict(interval_from, interval_to)
		self.load_stat(interval_from, interval_to, 1)

		for i in range(interval_from, interval_to):
			self.assertLoad(i)
			self.assertLoadStat(i)

	def test_reload_stat_without_word(self):
		interval_from = 0
		interval_to   = 5
		self.load_stat(interval_from, interval_to, 1)

		for i in range(interval_from, interval_to):
			self.assertLoadStat(i)

	def test_reload_stat_double(self):
		interval_from1 = 0
		interval_to1   = 5
		self.load_stat(interval_from1, interval_to1, 1)
		interval_from2 = 3
		interval_to2   = 8
		self.load_stat(interval_from2, interval_to2, 1)

		for i in range(interval_from1, interval_to2):
			self.assertLoadStat(i)

	def test_loaded_words(self):
		interval_from1 = 0
		interval_to1   = 5
		self.load_dict(interval_from1, interval_to1)
		interval_from2 = 3
		interval_to2   = 9
		self.load_stat(interval_from2, interval_to2, 1)

		loaded_words = self.dict_obj.loaded_words(0)
		self.assertEqual(len(loaded_words), len(range(interval_from1, interval_to1)))

		for i, it in enumerate(loaded_words):
			self.assertEqual(it[0].get_show_info()[0], "en" + str(i))

	def test_load_error_dict_ver(self):
		try:
			self.load_stat(0, 1, 2)
			self.fail("except not found")
		except ErrDict:
			pass

	def test_rename_check(self):
		"Тест на то, что корректно проходит проверка перед переименованием"

		self.load_dict(0, 2)

		try:
			# пустое новое английское слово
			self.dict_obj._rename_check("en0", "", "new_ru")
			self.fail("except not found")
		except ErrDict:
			pass

		try:
			# пустое новое русское слово
			self.dict_obj._rename_check("en0", "new_en", "")
			self.fail("except not found")
		except ErrDict:
			pass

		try:
			# старое слово не в списке ключей
			self.dict_obj._rename_check("en10", "new_en", "new_ru")
			self.fail("except not found")
		except ErrDict:
			pass

		try:
			# новое слово имеет дубликаты
			self.dict_obj._rename_check("en0", "EN1", "new_ru")
			self.fail("except not found")
		except ErrDict:
			pass

		# Корректное переименование
		self.dict_obj._rename_check("en0", "en0", "new_ru")
		self.dict_obj._rename_check("en0", "new_en", "new_ru")

	def test_rename_in_json_dict(self):
		"Проверим корректность переименования в словаре, который загрузили из файла"
		j_dict = self.json_dict(0, 2)

		import copy

		# Старое слово не в базе
		new_dict = self.dict_obj._rename_in_json_dict("en10", "new_en", "new_tr", "new_ru", copy.deepcopy(j_dict))
		self.assertEqual(new_dict, [["en0", "tr0", "ru0"], ["en1", "tr1", "ru1"], ["new_en", "new_tr", "new_ru"]])

		# Старое слово в базе
		new_dict = self.dict_obj._rename_in_json_dict("  en0 ", "new_en", "new_tr", "new_ru", copy.deepcopy(j_dict))
		self.assertEqual(new_dict, [["new_en", "new_tr", "new_ru"], ["en1", "tr1", "ru1"]])

		# Старое слово в базе
		new_dict = self.dict_obj._rename_in_json_dict(" En1 ", "new_en", "new_tr", "new_ru", copy.deepcopy(j_dict))
		self.assertEqual(new_dict, [["en0", "tr0", "ru0"], ["new_en", "new_tr", "new_ru"]])

		# Старое слово в базе и равно новому
		new_dict = self.dict_obj._rename_in_json_dict(" En1 ", "EN1", "new_tr", "new_ru", copy.deepcopy(j_dict))
		self.assertEqual(new_dict, [["en0", "tr0", "ru0"], ["EN1", "new_tr", "new_ru"]])

		# # английское слово имеет дубликаты не равные старому слову
		try:
			self.dict_obj._rename_in_json_dict("en1", "EN0", "new_tr", "new_ru", copy.deepcopy(j_dict))
			self.fail("except not found")
		except ErrDict:
			pass

	def test_rename_in_dict(self):
		"Проверим корректность переименования в загруженных данных"
		self.load_dict(0, 2)
		old_word = self.dict_obj.get_word_by_key("en0")

		self.dict_obj._rename_in_dict("en0", "new_en", "new_tr", "new_ru")

		new_word = self.dict_obj.get_word_by_key("new_en")
		self.assertEqual(("new_en", "[%s]" % "new_tr", "new_ru"), new_word.get_show_info())
		self.assertLoad(1)
		self.assertEqual(len(self.dict_obj.words), 2)
		self.assertEqual(old_word is new_word, True)

if __name__ == "__main__":
	suite = unittest.TestLoader().loadTestsFromTestCase(DictTestCase)
	unittest.TextTestRunner(verbosity=2).run(suite)
