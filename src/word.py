# -*- coding: utf-8 -*-

import re
import unittest
import statistic

en_to_ru_write = 0
ru_to_en_write = 1

reg_cmnt = re.compile("\(.*?\)")
reg_no_sign_part = re.compile("\[.*?\]")


class WordInfo:
    def __init__(self, word, transcription):
        self.word = word
        self.transcription = transcription

    def __eq__(self, other):
        return self.word == other.word and self.transcription == other.transcription


class Word:
    """ Хранение информации по одному слову:
        английский вариант, перевод, транскрипция + статистика и рейтинг
        Умеет:
        -парсить сырые данные (те, что сохранены в словаре) во внутренний формат
        -проверять правильность ответа и в зависимости от результата обновлять статистику
        -сериализовать/десериализовать статистику по слову
    """
    def __init__(self):
        # Английское слово, которое будет отображаться пользователю
        self.en_word = ""
        # Исходное английское слово, без преобразований
        self.en_source = ""
        # Распарсенное английское слово
        self.en_word_list = []
        # Транскрипция
        self.transcription = ""
        # Массив русских слов, без преобразований
        self.ru_source = []
        # Русское слово, которое будет отображаться пользователю
        self.ru_word = ""
        # Распарсенное русское слово
        self.ru_word_list = []
        # Рейтинг слова, влияет на вероятность появления его в упражнении
        self.rating = 0
        # Ссылка на статистику по слову
        self.stat = {en_to_ru_write: statistic.Statistic(), ru_to_en_write: statistic.Statistic()}

    @staticmethod
    def _convert_spec_chars(s):
        return s.replace(u"ё", u"е")

    @staticmethod
    def _prepare_show_words(word_list):
        filtered_list = []
        norm_list = []
        for it in map(lambda x: x.replace("[", "").replace("]", ""), word_list):
            norm_word = Word._convert_spec_chars(it.lower())
            if norm_word not in norm_list:
                norm_list.append(norm_word)
                filtered_list.append(it)
        return ", ".join(filtered_list)

    def add_value(self, en_word, transcription, ru_word):
        def prepare_word(w):
            return reg_no_sign_part.sub(".*?", reg_cmnt.sub("", w.lower()).strip())

        if self.en_word == "":
            self.en_source = en_word
            en_split = map(lambda x: x.strip(), en_word.split(","))
            self.en_word = Word._prepare_show_words(en_split)
            self.en_word_list = map(lambda x: prepare_word(x), en_split)
        if self.transcription == "" and transcription is not None and transcription.strip() != "":
            self.transcription = "[%s]" % transcription.strip()
        self.ru_source += map(lambda x: x.strip(), ru_word.split(","))

        self.ru_word = Word._prepare_show_words(self.ru_source)
        self.ru_word_list = map(lambda x: Word._convert_spec_chars(prepare_word(x)), self.ru_source)

    def rename(self, en_word, transcription, ru_word):
        "Переименовать слово, не касаясь статистики, рейтинга и др. служебных данных"
        self.en_word = ""
        self.en_word_list = []
        self.transcription = ""
        self.ru_source = []
        self.ru_word = ""
        self.ru_word_list = []
        self.add_value(en_word, transcription, ru_word)

    def set_rating(self, value):
        self.rating = value

    def get_rating(self):
        return self.rating

    def question_data(self, type_pr):
        "Получение отображаемых в вопросе данных по слову"
        if type_pr == en_to_ru_write:
            return WordInfo(self.en_word, self.transcription)
        else:
            return WordInfo(self.ru_word, "")

    def is_new(self, type_pr):
        "Возвращает True, если слово еще не изучалось"
        return self.stat[type_pr].is_new()

    def _check_ru(self, answer):
        answer = Word._convert_spec_chars(answer)
        for it in self.ru_word_list:
            if re.match(it + "\Z", answer) is not None:
                return True
        return False

    def _check_en(self, answer):
        for it in self.en_word_list:
            if re.match(it + "\Z", answer) is not None:
                return True
        return False

    def check(self, answer, type_pr):
        answer = answer.strip().lower()
        if type_pr == en_to_ru_write:
            is_success = self._check_ru(answer)
            return is_success, WordInfo(self.ru_word, "")
        else:
            is_success = self._check_en(answer)
            return is_success, WordInfo(self.en_word, self.transcription)

    def update_stat(self, is_success, add_percent, type_pr):
        self.stat[type_pr].update(is_success, add_percent)

    def get_show_info(self):
        "Отображаемая информация в глобальной статистике по слову"
        return (self.en_word, self.transcription, self.ru_word)

    def get_source_info(self):
        "Исходные данные слова, наиболее приближенные к виду в словаре"
        s = set()
        s_add = s.add
        # убираем из self.ru_source неуникальные элементы, сохраняя порядок
        ru_source = ", ".join([x for x in self.ru_source if x not in s and not s_add(x)])
        return (self.en_source, self.transcription.strip("[]"), ru_source)

    def is_load(self):
        return self.en_word != ""

    def get_stat(self, type_pr):
        return self.stat[type_pr]

    def unpack(self, statistic):
        for it in statistic:
            it_int = int(it)
            if it_int not in self.stat.keys():
                self.stat[it_int] = statistic.Statistic()
            self.stat[it_int].unpack(statistic[it])

    def pack(self):
        data = {}
        for it in self.stat:
            data[it] = self.stat[it].pack()
        return data


class WordTestCase(unittest.TestCase):
    "Набор тестов для класса Word"

    def setUp(self):
        self.word = Word()

    def test_init(self):
        "Тест работы конструктора"

        self.assertEqual(self.word.en_word, u"")
        self.assertEqual(self.word.en_source, u"")
        self.assertEqual(self.word.en_word_list, [])
        self.assertEqual(self.word.transcription, u"")
        self.assertEqual(self.word.ru_word, u"")
        self.assertEqual(self.word.ru_word_list, [])
        self.assertEqual(self.word.rating, 0)
        self.assertEqual(len(self.word.stat), 2)
        self.assertEqual(self.word.stat[en_to_ru_write], statistic.Statistic())
        self.assertEqual(self.word.stat[ru_to_en_write], statistic.Statistic())

    def test_add_value(self):
        "Тест на добавление слова два раза подряд"

        self.word.add_value(u"  Hello  ", u"  \'he\'ləu  ", u"  привет  ")
        self.assertEqual(self.word.en_word, u"Hello")
        self.assertEqual(self.word.en_source, u"  Hello  ")
        self.assertEqual(self.word.en_word_list, [u"hello"])
        self.assertEqual(self.word.transcription, u"[\'he\'ləu]")
        self.assertEqual(self.word.ru_word, u"привет")
        self.assertEqual(self.word.ru_word_list, [u"привет"])

        self.word.add_value(u"  Hello  ", u"  \'he\'ləu  ", u"  приветствие  ")
        self.assertEqual(self.word.en_word, u"Hello")
        self.assertEqual(self.word.en_source, u"  Hello  ")
        self.assertEqual(self.word.en_word_list, [u"hello"])
        self.assertEqual(self.word.transcription, u"[\'he\'ləu]")
        self.assertEqual(self.word.ru_word, u"привет, приветствие")
        self.assertEqual(self.word.ru_word_list, [u"привет", u"приветствие"])

    def test_add_value_with_empty_transcription(self):
        "Тест на добавление слова с пустой транскрипцией"

        self.word.add_value(u"  Hello  ", u"", u"  привет  ")
        self.assertEqual(self.word.en_word, u"Hello")
        self.assertEqual(self.word.en_source, u"  Hello  ")
        self.assertEqual(self.word.en_word_list, [u"hello"])
        self.assertEqual(self.word.transcription, u"")
        self.assertEqual(self.word.ru_word, u"привет")
        self.assertEqual(self.word.ru_word_list, [u"привет"])

    def test_add_value_double_ru(self):
        "Тест на добавление слова с двойным русским переводом два раза подряд (во второй раз с пустой транскрипцией)"

        self.word.add_value(u"  Hello  ", u"  \'he\'ləu  ", u"  привет, алло  ")
        self.assertEqual(self.word.en_word, u"Hello")
        self.assertEqual(self.word.en_source, u"  Hello  ")
        self.assertEqual(self.word.en_word_list, [u"hello"])
        self.assertEqual(self.word.transcription, u"[\'he\'ləu]")
        self.assertEqual(self.word.ru_word, u"привет, алло")
        self.assertEqual(self.word.ru_word_list, [u"привет", u"алло"])

        self.word.add_value(u"  Hello  ", None, u"  приветствие, оклик  ")
        self.assertEqual(self.word.en_word, u"Hello")
        self.assertEqual(self.word.en_source, u"  Hello  ")
        self.assertEqual(self.word.en_word_list, [u"hello"])
        self.assertEqual(self.word.transcription, u"[\'he\'ləu]")
        self.assertEqual(self.word.ru_word, u"привет, алло, приветствие, оклик")
        self.assertEqual(self.word.ru_word_list, [u"привет", u"алло", u"приветствие", u"оклик"])

    def test_add_value_cmnt(self):
        "Тест на корректную обработку комментариев в английском и русском словах"

        self.word.add_value(u"  Hello (Comment) ,  Hi  ", u"  \'he\'ləu  ", u"  привет (Здоровается) ,  алло  ")
        self.assertEqual(self.word.en_word, u"Hello (Comment), Hi")
        self.assertEqual(self.word.en_source, u"  Hello (Comment) ,  Hi  ")
        self.assertEqual(self.word.en_word_list, [u"hello", u"hi"])
        self.assertEqual(self.word.transcription, u"[\'he\'ləu]")
        self.assertEqual(self.word.ru_word, u"привет (Здоровается), алло")
        self.assertEqual(self.word.ru_word_list, [u"привет", u"алло"])

    def test_add_value_no_sign_part(self):
        "Тест на корректную обработку необязательных частей в англиском и русском словах"

        self.word.add_value(u"  He[llo], H[al]l[o]  ", u"  \'he\'ləu  ", u"привет[ствие],ок[лик]ат[ь]")
        self.assertEqual(self.word.en_word, u"Hello, Hallo")
        self.assertEqual(self.word.en_source, u"  He[llo], H[al]l[o]  ")
        self.assertEqual(self.word.en_word_list, [u"he.*?", u"h.*?l.*?"])
        self.assertEqual(self.word.transcription, u"[\'he\'ləu]")
        self.assertEqual(self.word.ru_word, u"приветствие, окликать")
        self.assertEqual(self.word.ru_word_list, [u"привет.*?", u"ок.*?ат.*?"])

    def test_add_value_with_duplicate(self):
        "Тест на добавление слова множество раз, причем русские перевод - дублируются"

        self.word.add_value(u"Hello", u"  \'he\'ləu  ", u"привет")
        self.word.add_value(u"Hello", u"  \'he\'ləu  ", u"привет")
        self.word.add_value(u"Hello", u"  \'he\'ləu  ", u"пРивет")
        self.word.add_value(u"Hello", u"  \'he\'ləu  ", u"пРиВет")
        self.word.add_value(u"Hello", u"  \'he\'ləu  ", u"пРи[Вет]")
        self.word.add_value(u"Hello", u"  \'he\'ləu  ", u"пРиВет(1)")
        self.word.add_value(u"Hello", u"  \'he\'ləu  ", u"пРиВет(1)")
        self.assertEqual(self.word.en_word, u"Hello")
        self.assertEqual(self.word.en_source, u"Hello")
        self.assertEqual(self.word.en_word_list, [u"hello"])
        self.assertEqual(self.word.transcription, u"[\'he\'ləu]")
        self.assertEqual(self.word.ru_word, u"привет, пРиВет(1)")
        self.assertEqual(self.word.ru_word_list, [u"привет", u"привет", u"привет",
                                                  u"привет", u"при.*?", u"привет", u"привет"])

    def test_rename(self):
        "Тест на переименование слова"

        self.word.add_value(u"Hello", u"\'he\'ləu", u"привет")
        self.word.rating = 5
        self.word.update_stat(True, 50, en_to_ru_write)
        self.word.update_stat(False, -10, en_to_ru_write)
        self.word.update_stat(True, 40, ru_to_en_write)
        self.word.update_stat(False, -20, ru_to_en_write)
        import copy
        old_stat_en = copy.deepcopy(self.word.stat[en_to_ru_write])
        old_stat_ru = copy.deepcopy(self.word.stat[ru_to_en_write])

        self.word.rename(u"Cup", u"kʌp", u"Чашка")
        self.assertEqual(self.word.en_word, u"Cup")
        self.assertEqual(self.word.en_source, u"Cup")
        self.assertEqual(self.word.en_word_list, [u"cup"])
        self.assertEqual(self.word.transcription, u"[kʌp]")
        self.assertEqual(self.word.ru_word, u"Чашка")
        self.assertEqual(self.word.ru_word_list, [u"чашка"])
        self.assertEqual(self.word.rating, 5)
        self.assertEqual(self.word.stat[en_to_ru_write], old_stat_en)
        self.assertEqual(self.word.stat[ru_to_en_write], old_stat_ru)

    def test_rating(self):
        "Тест на установку рейтинга слова"

        rating = 51.879
        self.word.set_rating(rating)
        self.assertEqual(self.word.get_rating(), rating)

    def test_question_data(self):
        "Тест на работу функции question_data"

        self.word.add_value(u"Hello", u"\'he\'ləu", u"привет")
        self.assertEqual(self.word.question_data(en_to_ru_write), WordInfo(u"Hello", u"[\'he\'ləu]"))
        self.assertEqual(self.word.question_data(ru_to_en_write), WordInfo(u"привет", u""))

    def test_check(self):
        "Тест на то, что многовариантные слова на аглийском и русском, правильно проходят проверку"

        self.word.add_value(u"Hello, Hallo", u"  \'he\'ləu  ", u"привет,алло")

        ru_ans = WordInfo(u"привет, алло", u"")
        self.assertEqual(self.word.check(u"  ПРИВЕТ    ", en_to_ru_write), (True, ru_ans))
        self.assertEqual(self.word.check(u"  АЛЛО      ", en_to_ru_write), (True, ru_ans))
        self.assertEqual(self.word.check(u"error_answer", en_to_ru_write), (False, ru_ans))

        en_ans = WordInfo(u"Hello, Hallo", u"[\'he\'ləu]")
        self.assertEqual(self.word.check(u"  HELLO     ", ru_to_en_write), (True, en_ans))
        self.assertEqual(self.word.check(u"  HALLO     ", ru_to_en_write), (True, en_ans))
        self.assertEqual(self.word.check(u"error_answer", ru_to_en_write), (False, en_ans))

    def test_check_cmnt(self):
        "Тест на то, что слова на аглийском и русском с комментариями, правильно проходят проверку"

        self.word.add_value(u"Hello(Comment), Hallo", u"  \'he\'ləu  ", u"привет(Здоровается),алло")

        ru_ans = WordInfo(u"привет(Здоровается), алло", u"")
        self.assertEqual(self.word.check(u"  ПРИВЕТ    ", en_to_ru_write), (True, ru_ans))
        self.assertEqual(self.word.check(u"  АЛЛО      ", en_to_ru_write), (True, ru_ans))
        self.assertEqual(self.word.check(u"error_answer", en_to_ru_write), (False, ru_ans))

        en_ans = WordInfo(u"Hello(Comment), Hallo", u"[\'he\'ləu]")
        self.assertEqual(self.word.check(u"  HELLO     ", ru_to_en_write), (True, en_ans))
        self.assertEqual(self.word.check(u"  HALLO     ", ru_to_en_write), (True, en_ans))
        self.assertEqual(self.word.check(u"error_answer", ru_to_en_write), (False, en_ans))

    def test_check_no_sign_part(self):
        "Тест на то, что слова на аглийском и русском с необязательными частями, правильно проходят проверку"

        self.word.add_value(u"  He[llo], H[al]l[o]  ", u"  \'he\'ləu  ", u"привет[ствие],ок[лик]ат[ь]")

        ru_ans = WordInfo(u"приветствие, окликать", u"")
        self.assertEqual(self.word.check(u"привет        ", en_to_ru_write), (True, ru_ans))
        self.assertEqual(self.word.check(u"приветaddtext ", en_to_ru_write), (True, ru_ans))
        self.assertEqual(self.word.check(u"окат          ", en_to_ru_write), (True, ru_ans))
        self.assertEqual(self.word.check(u"окликaddатadd]", en_to_ru_write), (True, ru_ans))
        self.assertEqual(self.word.check(u"привит        ", en_to_ru_write), (False, ru_ans))
        self.assertEqual(self.word.check(u"окар          ", en_to_ru_write), (False, ru_ans))

        en_ans = WordInfo(u"Hello, Hallo", u"[\'he\'ləu]")
        self.assertEqual(self.word.check(u"HELLO    ", ru_to_en_write), (True, en_ans))
        self.assertEqual(self.word.check(u"HELLO123 ", ru_to_en_write), (True, en_ans))
        self.assertEqual(self.word.check(u"HE123    ", ru_to_en_write), (True, en_ans))
        self.assertEqual(self.word.check(u"HALLO    ", ru_to_en_write), (True, en_ans))
        self.assertEqual(self.word.check(u"HL       ", ru_to_en_write), (True, en_ans))
        self.assertEqual(self.word.check(u"H123     ", ru_to_en_write), (False, en_ans))
        self.assertEqual(self.word.check(u"123l123  ", ru_to_en_write), (False, en_ans))

    def test_check_special_char_in_word(self):
        "Тест на то, что слова со спец. символами в переводе правильно проходят проверку"

        self.word.add_value(u"Yellow", u"", u"жёлтый")
        ru_ans = WordInfo(u"жёлтый", u"")
        self.assertEqual(self.word.check(u"желтый", en_to_ru_write), (True, ru_ans))
        self.assertEqual(self.word.check(u"жёлтый", en_to_ru_write), (True, ru_ans))

    def test_check_special_char_in_answer(self):
        "Тест на то, что слова со спец. символами в ответе правильно проходят проверку"

        self.word.add_value(u"Yellow", u"", u"желтый")
        ru_ans = WordInfo(u"желтый", u"")
        self.assertEqual(self.word.check(u"желтый", en_to_ru_write), (True, ru_ans))
        self.assertEqual(self.word.check(u"жёлтый", en_to_ru_write), (True, ru_ans))

    def test_get_show_info(self):
        "Тест функции get_show_info"

        self.word.add_value(u"Hel[lo]", u"\'he\'ləu", u"привет, приветствие")
        self.assertEqual(self.word.get_show_info(), (u"Hello", u"[\'he\'ləu]", u"привет, приветствие"))

    def test_get_source_info(self):
        "Тест функции get_source_info"

        self.word.add_value(u"Hel[lo]", u"\'he\'ləu", u"привет, приветствие")
        self.assertEqual(self.word.get_source_info(), (u"Hel[lo]", u"\'he\'ləu", u"привет, приветствие"))

    def test_is_load(self):
        "Тест на работу функции is_load"

        self.assertEqual(self.word.is_load(), False)

        self.word.add_value(u"Hello", u"", u"привет")
        self.assertEqual(self.word.is_load(), True)

    def test_unpack(self):
        "Тест на работу функции unpack"

        import datetime
        today = datetime.date.today().strftime("%Y.%m.%d")
        statistic_in = {str(en_to_ru_write): [2, 3, today, False, 30], str(ru_to_en_write): [2, 2, today, False, 40]}

        st0 = statistic.Statistic()
        st0.update(True, 50)
        st0.update(False, -10)
        st0.update(False, -10)
        st0.update(True, 10)
        st0.update(False, -10)

        st1 = statistic.Statistic()
        st1.update(True, 50)
        st1.update(False, -10)
        st1.update(True, 10)
        st1.update(False, -10)

        self.word.unpack(statistic_in)
        self.assertEqual(self.word.stat[en_to_ru_write], st0)
        self.assertEqual(self.word.stat[ru_to_en_write], st1)

    def test_pack(self):
        "Тест на работу функции pack"

        import datetime
        today = datetime.date.today().strftime("%Y.%m.%d")
        statistic_out = {en_to_ru_write: [1, 2, today, False, 30], ru_to_en_write: [2, 1, today, True, 20]}
        self.word.update_stat(True, 50, en_to_ru_write)
        self.word.update_stat(False, -10, en_to_ru_write)
        self.word.update_stat(False, -10, en_to_ru_write)
        self.word.update_stat(False, -10, ru_to_en_write)
        self.word.update_stat(True, 10, ru_to_en_write)
        self.word.update_stat(True, 10, ru_to_en_write)
        self.assertEqual(self.word.pack(), statistic_out)

if __name__ == "__main__":
    import os
    import os.path
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    suite = unittest.TestLoader().loadTestsFromTestCase(WordTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
