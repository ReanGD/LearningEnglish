# -*- coding: utf-8 -*-

import re
import json
import os.path
import unittest

class Config:
	def __init__(self, path):
		self.path = path

	def reload(self):
		if os.path.exists(self.path):
			txt = open(self.path).read()
			txt = re.compile(r"/\*.*?\*/", re.DOTALL).sub("", txt) # remove comments
			cfg_dict = json.loads(txt)
		else:
			cfg_dict = {}
		cfg_dict["path_to_dict"]     = cfg_dict.get("path_to_dict","dict.json")
		cfg_dict["path_to_stat"]     = cfg_dict.get("path_to_stat","statistic.json")
		cfg_dict["words_per_lesson"] = int(cfg_dict.get("words_per_lesson",5))
		cfg_dict["CntStudyWords"]    = int(cfg_dict.get("CntStudyWords",50))
		cfg_dict["MinPercent"]       = float(cfg_dict.get("MinPercent",97.0))
		cfg_dict["MinSuccessCnt"]    = int(cfg_dict.get("MinSuccessCnt",10))
		cfg_dict["retry_time"]       = int(cfg_dict.get("retry_time",1800))
		return cfg_dict

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

		self.assertEqual(len(cfg_dict), 7)

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

		self.assertEqual(len(cfg_dict), 7)

if __name__=="__main__":
	suite = unittest.TestLoader().loadTestsFromTestCase(ConfigTestCase)
	unittest.TextTestRunner(verbosity=2).run(suite)