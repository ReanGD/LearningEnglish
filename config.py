# -*- coding: utf-8 -*-

import re
import json
import os.path
import unittest

reg_cmnt = re.compile(r"/\*.*?\*/", re.DOTALL)


class Config:
	"Работа с конфигурационным файлом"

	def __init__(self, path):
		self.path     = path
		self.cfg_dict = {}

	def __getitem__(self, key):
		return self.cfg_dict[key]

	def __len__(self):
		return len(self.cfg_dict)

	def reload(self):
		if os.path.exists(self.path):
			txt = open(self.path).read()
			txt = reg_cmnt.sub("", txt)  # remove comments
			self.cfg_dict = json.loads(txt)
		else:
			self.cfg_dict = {}
		self.cfg_dict["path_to_dict"]         = self.cfg_dict.get("path_to_dict", "dict.json")
		self.cfg_dict["path_to_stat"]         = self.cfg_dict.get("path_to_stat", "statistic.json")
		self.cfg_dict["words_per_lesson"]     = int(self.cfg_dict.get("words_per_lesson", 5))
		self.cfg_dict["CntStudyWords"]        = int(self.cfg_dict.get("CntStudyWords", 50))
		self.cfg_dict["MinPercent"]           = float(self.cfg_dict.get("MinPercent", 97.0))
		self.cfg_dict["MinSuccessCnt"]        = int(self.cfg_dict.get("MinSuccessCnt", 10))
		self.cfg_dict["retry_time"]           = int(self.cfg_dict.get("retry_time", 1800))
		self.cfg_dict["hide_transcription"]   = self.cfg_dict.get("hide_transcription", "no")
		self.cfg_dict["start_time_delay"]     = int(self.cfg_dict.get("start_time_delay", 1))
		self.cfg_dict["stat_count_row"]       = int(self.cfg_dict.get("stat_count_row", 200))
		self.cfg_dict["right_answer_percent"] = float(self.cfg_dict.get("right_answer_percent", 10.0))
		self.cfg_dict["wrong_answer_percent"] = float(self.cfg_dict.get("wrong_answer_percent", 40.0))

		return self.cfg_dict

	def get_dict(self):
		return self.cfg_dict


class ConfigTestCase(unittest.TestCase):
	"Набор тестов для класса Config"

	def test_exists(self):
		"Тестирование загрузки реального файла с конфигурацией"

		cfg = Config("config.json")
		cfg.reload()

		self.assertEqual(cfg["path_to_dict"], "dict.json")
		self.assertEqual(cfg["path_to_stat"], "statistic.json")
		self.assertEqual(cfg["words_per_lesson"], 5)
		self.assertEqual(cfg["CntStudyWords"], 50)
		self.assertEqual(cfg["MinPercent"], 97.0)
		self.assertEqual(cfg["MinSuccessCnt"], 10)
		self.assertEqual(cfg["retry_time"], 1800)
		self.assertEqual(cfg["hide_transcription"], "no")
		self.assertEqual(cfg["start_time_delay"], 1)
		self.assertEqual(cfg["stat_count_row"], 200)
		self.assertEqual(cfg["right_answer_percent"], 10.0)
		self.assertEqual(cfg["wrong_answer_percent"], 40.0)

		self.assertEqual(len(cfg), 12)

	def test_not_exists(self):
		"Тестирование загрузки несуществующего файла с конфигурацией"

		cfg = Config("fake_config.json")
		cfg.reload()

		self.assertEqual(cfg["path_to_dict"], "dict.json")
		self.assertEqual(cfg["path_to_stat"], "statistic.json")
		self.assertEqual(cfg["words_per_lesson"], 5)
		self.assertEqual(cfg["CntStudyWords"], 50)
		self.assertEqual(cfg["MinPercent"], 97.0)
		self.assertEqual(cfg["MinSuccessCnt"], 10)
		self.assertEqual(cfg["retry_time"], 1800)
		self.assertEqual(cfg["hide_transcription"], "no")
		self.assertEqual(cfg["start_time_delay"], 1)
		self.assertEqual(cfg["stat_count_row"], 200)
		self.assertEqual(cfg["right_answer_percent"], 10.0)
		self.assertEqual(cfg["wrong_answer_percent"], 40.0)

		self.assertEqual(len(cfg), 12)

if __name__ == "__main__":
	suite = unittest.TestLoader().loadTestsFromTestCase(ConfigTestCase)
	unittest.TextTestRunner(verbosity=2).run(suite)
