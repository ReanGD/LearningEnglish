# -*- coding: utf-8 -*-


class BaseOperation:

	def __init__(self):
		self._callback = None

	def set_callback(self, func):
		self._callback = func
		return self

	def callback(self):
		if self._callback is not None:
			self._callback()

	def execute(self, parent, args=None):
		import error_dialog
		error_dialog.show_error("err_oper_not_found")
