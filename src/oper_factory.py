# -*- coding: utf-8 -*-

from operation import BaseOperation
from edit_word_dialog import OperationEditWord
from statistic_dialog import OperationShowStatistic


class OperationFactory:
	def __init__(self):
		self._dictionary = None
		self._cfg = None

	def create(self, dictionary, cfg):
		self._dictionary = dictionary
		self._cfg = cfg

	def get_operation(self, name):
		if name == "EditWord" and self._dictionary is not None:
			op = OperationEditWord(self._dictionary)
		elif name == "ShowStatistic" and self._dictionary is not None and self._cfg is not None:
			op = OperationShowStatistic(self._dictionary, self._cfg, self)
		else:
			op = BaseOperation()
		return op
