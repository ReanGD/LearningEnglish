# -*- coding: utf-8 -*-

import re
import json
import os.path
import unittest

class Config:
	def __init__(self, path):
		self.path     = path
		self.cfg_dict = {}

	def reload(self):
		if os.path.exists(self.path):
			txt = open(self.path).read()
			txt = re.compile(r"/\*.*?\*/", re.DOTALL).sub("", txt) # remove comments
			self.cfg_dict = json.loads(txt)
		else:
			self.cfg_dict = {}
		self.cfg_dict["path_to_dict"]       = self.cfg_dict.get("path_to_dict","dict.json")
		self.cfg_dict["path_to_stat"]       = self.cfg_dict.get("path_to_stat","statistic.json")
		self.cfg_dict["words_per_lesson"]   = int(self.cfg_dict.get("words_per_lesson",5))
		self.cfg_dict["CntStudyWords"]      = int(self.cfg_dict.get("CntStudyWords",50))
		self.cfg_dict["MinPercent"]         = float(self.cfg_dict.get("MinPercent",97.0))
		self.cfg_dict["MinSuccessCnt"]      = int(self.cfg_dict.get("MinSuccessCnt",10))
		self.cfg_dict["retry_time"]         = int(self.cfg_dict.get("retry_time",1800))
		self.cfg_dict["hide_transcription"] = self.cfg_dict.get("hide_transcription","no")
		self.cfg_dict["start_time_delay"]   = int(self.cfg_dict.get("start_time_delay",1))
		
		return self.cfg_dict

	def get_dict(self):
		return self.cfg_dict

class ConfigTestCase(unittest.TestCase):

	def test_exists(self):
		cfg = Config("config.json")
		cfg_dict = cfg.reload()

		self.assertEqual(cfg_dict["path_to_dict"],"dict.json")
		self.assertEqual(cfg_dict["path_to_stat"],"statistic.json")
		self.assertEqual(cfg_dict["words_per_lesson"], 5)
		self.assertEqual(cfg_dict["CntStudyWords"], 50)
		self.assertEqual(cfg_dict["MinPercent"], 97.0)
		self.assertEqual(cfg_dict["MinSuccessCnt"], 10)
		self.assertEqual(cfg_dict["retry_time"], 1800)
		self.assertEqual(cfg_dict["hide_transcription"], "no")
		self.assertEqual(cfg_dict["start_time_delay"], 1)

		self.assertEqual(len(cfg_dict), 9)

	def test_not_exists(self):
		cfg = Config("fake_config.json")
		cfg_dict = cfg.reload()

		self.assertEqual(cfg_dict["path_to_dict"],"dict.json")
		self.assertEqual(cfg_dict["path_to_stat"],"statistic.json")
		self.assertEqual(cfg_dict["words_per_lesson"], 5)
		self.assertEqual(cfg_dict["CntStudyWords"], 50)
		self.assertEqual(cfg_dict["MinPercent"], 97.0)
		self.assertEqual(cfg_dict["MinSuccessCnt"], 10)
		self.assertEqual(cfg_dict["retry_time"], 1800)
		self.assertEqual(cfg_dict["hide_transcription"], "no")
		self.assertEqual(cfg_dict["start_time_delay"], 1)

		self.assertEqual(len(cfg_dict), 9)

if __name__=="__main__":
	suite = unittest.TestLoader().loadTestsFromTestCase(ConfigTestCase)
	unittest.TextTestRunner(verbosity=2).run(suite)