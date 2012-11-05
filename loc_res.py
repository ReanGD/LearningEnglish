# -*- coding: utf-8 -*-

import unittest

_str_dict = {
	 "end_lesson"           : "Завершить текущий урок"
	,"end_program"          : "Закрыть программу"
	,"correct_incorrect"    : "Верно/Неверно"
	,"correct"              : "Верно"
	,"incorrect"            : "Неверно"
	,"reiterate"            : "Повторим еще раз"
	,"of"                   : "из"
	,"win_learning_english" : "Изучаем английский"
	,"win_statistic_title"  : "Статистика ответов"
	,"win_critical_error"   : u"Критическая ошибка"
	,"err_dict_version"     : u"Версия файла со статистикой не верная. Установите последнюю версию программы. Продолжение работы не возможно."
	,"btn_ru_en"            : "Ru->En"
	,"btn_en_ru"            : "En->Ru"
	,"btn_common_stat"      : "Общая статистика"
	,"st_learn"             : u"учить"
	,"st_learned"           : u"выучено"
	,"st_study"             : u"изучаем"
	,"row_learn"            : u"учить"
	,"row_learned"          : u"выучено"
	,"row_study"            : u"изучаем"
	,"row_total"            : u"всего"
	,"clm_word"             : u"Слово"
	,"clm_transcription"    : u"Транскрипция"
	,"clm_translate"        : u"Перевод"
	,"clm_cnt_suc"          : u"Верных"
	,"clm_cnt_err"          : u"Не верных"
	,"clm_pers_suc"         : u"% верных"
	,"clm_state"            : u"Статус"
	,"clm_name"             : u"Наименование"
	,"clm_ru_en_cnt"        : u"Ru->En"
	,"clm_ru_en_pers"       : u"Ru->En (%)"
	,"clm_en_ru_cnt"        : u"En->Ru"
	,"clm_en_ru_pers"       : u"En->Ru (%)"
}

def _(name):
	return _str_dict[name]

class LocResTestCase(unittest.TestCase):
	def test_init(self):
		self.assertEqual(_str_dict["end_lesson"], _("end_lesson"))

if __name__=="__main__":
	suite = unittest.TestLoader().loadTestsFromTestCase(LocResTestCase)
	unittest.TextTestRunner(verbosity=2).run(suite)