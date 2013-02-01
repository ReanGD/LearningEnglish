# -*- coding: utf-8 -*-

import os
import re
import json
import os.path
import unittest

reg_cmnt = re.compile(r"/\*.*?\*/", re.DOTALL)


class Config:
    "Работа с конфигурационным файлом"

    def __init__(self, main_path=None, user_path=None):
        if main_path is None:
            self._main_path = "config.json"
        else:
            self._main_path = main_path
        if user_path is None:
            self._user_path = "config_user.json"
        else:
            self._user_path = user_path
        self._cfg_dict = {}

    def __getitem__(self, key):
        return self._cfg_dict[key]

    def __len__(self):
        return len(self._cfg_dict)

    def _load_json(self, path):
        data = {}
        if os.path.exists(path):
            txt = open(path).read()
            txt = reg_cmnt.sub("", txt)  # remove comments
            data = json.loads(txt)
        return data

    def _set_default(self, cfg):
        cfg["path_to_dict"] = cfg.get("path_to_dict", "dict.json")
        cfg["path_to_stat"] = cfg.get("path_to_stat", "statistic.json")
        cfg["words_per_lesson"] = int(cfg.get("words_per_lesson", 5))
        cfg["CntStudyWords"] = int(cfg.get("CntStudyWords", 50))
        cfg["MinPercent"] = float(cfg.get("MinPercent", 97.0))
        cfg["MinSuccessCnt"] = int(cfg.get("MinSuccessCnt", 10))
        cfg["retry_time"] = int(cfg.get("retry_time", 1800))
        cfg["hide_transcription"] = cfg.get("hide_transcription", "no")
        cfg["start_time_delay"] = int(cfg.get("start_time_delay", 1))
        cfg["stat_count_row"] = int(cfg.get("stat_count_row", 200))
        cfg["right_answer_percent"] = float(cfg.get("right_answer_percent", 10.0))
        cfg["wrong_answer_percent"] = float(cfg.get("wrong_answer_percent", 40.0))
        cfg["empty_answer_is_error"] = cfg.get("empty_answer_is_error", "no")

    def create_default_user_config(self):
        if not os.path.isfile(self._user_path):
            txt = "{\n    /*\n        User config\n    */\n\n}"
            open(self._user_path, "wt").write(txt)

    def reload(self):
        self._cfg_dict = {}
        self._cfg_dict.update(self._load_json(self._main_path))
        self._cfg_dict.update(self._load_json(self._user_path))
        self._set_default(self._cfg_dict)
        return self._cfg_dict

    def get_dict(self):
        return self._cfg_dict


class ConfigTestCase(unittest.TestCase):
    "Набор тестов для класса Config"

    def setUp(self):
        if os.path.isfile("test_config_user.json"):
            os.remove("test_config_user.json")

    def tearDown(self):
        if os.path.isfile("test_config_user.json"):
            os.remove("test_config_user.json")

    def equal_cfg(self, cfg, test_dict):
        for key, val in test_dict.items():
            self.assertEqual(cfg[key], val)
        self.assertEqual(len(cfg), 13)

    def test_main(self):
        "Тестирование загрузки основного файла с конфигурацией"

        test_dict = {
            "path_to_dict": "dict.json",
            "path_to_stat": "statistic.json",
            "words_per_lesson": 5,
            "CntStudyWords": 50,
            "MinPercent": 97.0,
            "MinSuccessCnt": 10,
            "retry_time": 1800,
            "hide_transcription": "no",
            "start_time_delay": 1,
            "stat_count_row": 200,
            "right_answer_percent": 10.0,
            "wrong_answer_percent": 40.0,
            "empty_answer_is_error": "no"}

        cfg = Config("config.json", "fake_config_user.json")
        cfg.reload()
        self.equal_cfg(cfg, test_dict)

    def test_user(self):
        "Тестирование загрузки пользовательского файла с конфигурацией"

        test_dict = {
            "path_to_dict": "dict1.json",
            "path_to_stat": "statistic1.json",
            "words_per_lesson": 6,
            "CntStudyWords": 60,
            "MinPercent": 98.0,
            "MinSuccessCnt": 11,
            "retry_time": 1801,
            "hide_transcription": "yes",
            "start_time_delay": 2,
            "stat_count_row": 300,
            "right_answer_percent": 20.0,
            "wrong_answer_percent": 50.0,
            "empty_answer_is_error": "yes"}

        json.dump(test_dict, open("test_config_user.json", "w"))
        cfg = Config("config.json", "test_config_user.json")
        cfg.reload()
        self.equal_cfg(cfg, test_dict)

    def test_user_part(self):
        "Тестирование загрузки пользовательского файла с конфигурацией, который перекрывает только часть настроек"

        test_dict = {
            "path_to_dict": "dict1.json",
            "path_to_stat": "statistic1.json",
            "words_per_lesson": 6,
            "CntStudyWords": 60,
            "MinPercent": 98.0,
            "MinSuccessCnt": 11}

        json.dump(test_dict, open("test_config_user.json", "w"))

        test_dict.update({
            "retry_time": 1800,
            "hide_transcription": "no",
            "start_time_delay": 1,
            "stat_count_row": 200,
            "right_answer_percent": 10.0,
            "wrong_answer_percent": 40.0,
            "empty_answer_is_error": "no"})

        cfg = Config("config.json", "test_config_user.json")
        cfg.reload()
        self.equal_cfg(cfg, test_dict)

    def test_not_exists(self):
        "Тестирование выставления дефолтных настроек"

        test_dict = {
            "path_to_dict": "dict.json",
            "path_to_stat": "statistic.json",
            "words_per_lesson": 5,
            "CntStudyWords": 50,
            "MinPercent": 97.0,
            "MinSuccessCnt": 10,
            "retry_time": 1800,
            "hide_transcription": "no",
            "start_time_delay": 1,
            "stat_count_row": 200,
            "right_answer_percent": 10.0,
            "wrong_answer_percent": 40.0,
            "empty_answer_is_error": "no"}

        cfg = Config("config.json", "fake_config_user.json")
        cfg.reload()
        self.equal_cfg(cfg, test_dict)

        cfg = Config("fake_config.json", "fake_config_user.json")
        cfg.reload()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    suite = unittest.TestLoader().loadTestsFromTestCase(ConfigTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
