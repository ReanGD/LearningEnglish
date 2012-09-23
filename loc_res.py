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
	,"st_learn"             : "учить"
	,"st_learned"           : "выучено"
	,"st_study"             : "изучаем"
	,"btn_ru_en"            : "Ru->En"
	,"btn_en_ru"            : "En->Ru"
	,"btn_common_stat"      : "Общая статистика"
	,"row_learn"            : "учить"
	,"row_learned"          : "выучено"
	,"row_study"            : "изучаем"
	,"row_total"            : "всего"
	,"clm_num"              : "№"
	,"clm_word"             : "Слово"
	,"clm_transcription"    : "Транскрипция"
	,"clm_translate"        : "Перевод"
	,"clm_cnt_suc"          : "Верных"
	,"clm_cnt_err"          : "Не верных"
	,"clm_pers_suc"         : "% верных"
	,"clm_state"            : "Статус"
	,"clm_ru_en_cnt"        : "Ru->En"
	,"clm_ru_en_pers"       : "Ru->En (%)"
	,"clm_en_ru_cnt"        : "En->Ru"
	,"clm_en_ru_pers"       : "En->Ru (%)"
}

def _(name):
	return _str_dict[name]

class LocResTestCase(unittest.TestCase):
	def test_init(self):
		self.assertEqual(_str_dict["end_lesson"], _("end_lesson"))

if __name__=="__main__":
	suite = unittest.TestLoader().loadTestsFromTestCase(LocResTestCase)
	unittest.TextTestRunner(verbosity=2).run(suite)