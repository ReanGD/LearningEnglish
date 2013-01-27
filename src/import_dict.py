# -*- coding: utf-8 -*-

import codecs
from config import Config
from dictionary import Dict


class ImportDict:

	def _lingualeo(self, path):
		json_dict = []
		for line in codecs.open(path, "rt", "utf-8"):
			json_dict.append(map(lambda x: x.strip().strip("[]"), line.split("\t")[1:]))
		return json_dict

	def import_dict(self, path, type_import):
		if type_import not in ("lingualeo"):
			return

		cfg = Config()
		cfg.reload()
		dictionary = Dict(cfg)
		json_dict = dictionary.load_dict_as_json(cfg["path_to_dict"])

		if type_import == "lingualeo":
			json_add_dict = self._lingualeo(path)

		new_keys = [it[0] for it in json_add_dict]
		old_keys = [it[0] for it in json_dict if it[0] not in new_keys]

		dictionary.reload_dict_from_json(json_dict + json_add_dict)
		json_dict = dictionary.make_json_from_dict(old_keys + new_keys)
		dictionary.save_dict(cfg["path_to_dict"], json_dict)
