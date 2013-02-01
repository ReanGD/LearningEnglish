# -*- coding: utf-8 -*-

import unittest

_str_dict = {
    "end_lesson": u"Завершить текущий урок",
    "end_program": u"Закрыть программу",
    "correct_incorrect": u"Верно/Неверно",
    "correct": u"Верно",
    "incorrect": u"Неверно",
    "reiterate": u"Повторим еще раз",
    "of": u"из",
    "lbl_edit_en": u"Английский вариант",
    "lbl_edit_tr": u"Транскрипция",
    "lbl_edit_ru": u"Русский вариант",
    "lbl_new_word": u"Новое слово",
    "win_learning_english": u"Изучаем английский",
    "win_statistic_title": u"Статистика ответов",
    "win_editword_title": u"Редактирование слова",
    "win_critical_error": u"Критическая ошибка",
    "win_error": u"Ошибка",
    "win_confirm_title": u"Подтверждение",
    "err_stat_version": u"Версия файла со статистикой не верная. Установите последнюю версию программы. "
                        + u"Продолжение работы не возможно.",
    "err_dublicate_en_word": u"Такое английское слово уже присутствует в базе.",
    "err_ru_word_empty": u"Русское слово не может быть пустым.",
    "err_en_word_empty": u"Английское слово не может быть пустым.",
    "err_find_en_word": u"Внутренняя ошибка целостности, изменяемое слово не найдено.",
    "err_oper_not_found": u"Данная операция недоступна.",
    "msg_confirm_rename": u"Вы действительно хотите изменить слово?",
    "btn_ru_en": u"Ru->En",
    "btn_en_ru": u"En->Ru",
    "btn_common_stat": u"Общая статистика",
    "row_learn": u"учить",
    "row_learned": u"выучено",
    "row_study": u"изучаем",
    "row_total": u"всего",
    "clm_word": u"Слово",
    "clm_transcription": u"Транскрипция",
    "clm_translate": u"Перевод",
    "clm_cnt_suc": u"Верных",
    "clm_cnt_err": u"Не верных",
    "clm_study_perсent": u"% изучения",
    "clm_name": u"Наименование",
    "clm_ru_en_cnt": u"Ru->En",
    "clm_ru_en_perc": u"Ru->En (%)",
    "clm_en_ru_cnt": u"En->Ru",
    "clm_en_ru_perc": u"En->Ru (%)"
}


def _(name):
    return _str_dict[name]


class LocResTestCase(unittest.TestCase):
    "Тестирование модуля loc_res.py"

    def test_init(self):
        "Тест получения значения лок. ресурса"
        self.assertEqual(_str_dict["end_lesson"], _("end_lesson"))

if __name__ == "__main__":
    import os
    import os.path
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    suite = unittest.TestLoader().loadTestsFromTestCase(LocResTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
