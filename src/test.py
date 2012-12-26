# -*- coding: utf-8 -*-


class A:
	def foo(self, a):
		print self, a

	def call(self):
		b = B()
		b.foo(self.foo)


class B:
	def foo(self, callback):
		self.callback = callback
		self.callback(1)

a = A()
a.call()
print a.__class__

import base64
print "icon='''\\\n" + base64.encodestring(open("img\\info.gif", "rb").read()) + "'''"
