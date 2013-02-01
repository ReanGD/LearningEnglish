# -*- coding: utf-8 -*-

import os
import os.path
import json
import json.encoder
import word
import global_stat
import unittest
import codecs


class ErrDict(Exception):
    def __init__(self, value, loc_res_msg):
        self.value = value
        self.loc_res_msg = loc_res_msg

    def __str__(self):
        return repr(self.value)


def statistic_v1_to_v2(data, min_percent, min_success_cnt):
    def calc_percent(success_answer, error_answer):
        if success_answer == 0:
            return 0.0
        else:
            multiplier = 1.0 if success_answer >= min_success_cnt else 0.9
            cnt = (success_answer if success_answer >= min_success_cnt else min_success_cnt) + error_answer
            abs_percent = float(success_answer) / float(cnt) * 100.0
            percent = abs_percent / min_percent if min_percent > 0 else 1.0
            return min(percent, multiplier) * 100.0

    min_success_cnt = max(min_success_cnt, 10)
    for it_word in data.values():
        for stat_key in it_word:
            success_answer = it_word[stat_key][0]
            error_answer = it_word[stat_key][1]
            it_word[stat_key].append(calc_percent(success_answer, error_answer))
    return data


class DictJSONEncoder(json.JSONEncoder):

    def __init__(self, skipkeys, ensure_ascii, check_circular, allow_nan, indent, separators, encoding, default):
        json.JSONEncoder.__init__(self, skipkeys=False, ensure_ascii=False, check_circular=False, allow_nan=True,
                                  sort_keys=False, indent=4, separators=(", ", ": "), encoding="utf-8", default=None)

    def _iterencode_list_lvl2(self, lst, max_len_lst):
        if len(lst) not in (2, 3):
            return "[]"

        if len(lst) == 2:
            sp_len0 = max_len_lst[0] + max_len_lst[1] - len(lst[0]) + 3
            arr = [lst[0], " " * sp_len0 + lst[1]]
        else:
            sp_len0 = max_len_lst[0] - len(lst[0]) + 1
            sp_len1 = max_len_lst[1] - len(lst[1]) + 1
            arr = [lst[0],
                   " " * sp_len0 + lst[1],
                   " " * sp_len1 + lst[2]]

        return "[%s]" % ",".join(arr)

    def iterencode(self, lst):
        if not lst:
            yield "[]"
            return

        self.current_indent_level = 1
        newline_indent = "\n    "
        separator = "," + newline_indent

        max_len_lst = [0, 0]
        str_lst = map(lambda row: [json.encoder.encode_basestring(it) for it in row if it.strip() != ""], lst)
        for row in str_lst:
            max_len_lst[0] = max(max_len_lst[0], len(row[0]))
            if len(row) == 3:
                max_len_lst[1] = max(max_len_lst[1], len(row[1]))

        yield "[" + newline_indent

        first = True
        for value in str_lst:
            if first:
                first = False
            else:
                yield separator
            yield self._iterencode_list_lvl2(value, max_len_lst)

        yield "\n]"


class Dict:
    def __init__(self, cfg):
        self.words = {}
        self.cfg = cfg

    def get_word_by_key(self, en):
        w = self.words.get(en)
        if not w:
            w = self.words[en] = word.Word()
        return w

    def reload_dict_from_json(self, json_dict):
        self.words = {}
        for it in json_dict:
            if len(it) == 3:
                en, tr, ru = it
            else:
                en, ru = it
                tr = ""
            self.get_word_by_key(en).add_value(en, tr, ru)

    def load_dict_as_json(self, path):
        return json.load(codecs.open(path, "rt", "utf-8"))

    def reload_dict(self, path):
        self.reload_dict_from_json(self.load_dict_as_json(path))

    def save_dict(self, path, json_dict):
        json.dump(json_dict, codecs.open(path, "wt", "utf-8"), cls=DictJSONEncoder)

    def make_json_from_dict(self, keys):
        if keys is None:
            keys = self.words.keys()
        words = [self.words.get(key, None) for key in keys]
        return [list(w.get_source_info()) for w in words if w]

    def _reload_stat_from_json(self, json_stat):
        version = json_stat["version"]
        data = json_stat["data"]

        if version == 1:
            data = statistic_v1_to_v2(data, self.cfg["MinPercent"], self.cfg["MinSuccessCnt"])
        elif version != 2:
            raise ErrDict("Error stat file version", "err_stat_version")

        for it in data:
            self.get_word_by_key(it).unpack(data[it])

    def reload_stat(self, path):
        if os.path.exists(path):
            self._reload_stat_from_json(json.load(open(path)))

    def save_stat(self, path):
        data = {}
        for it in self.words:
            data[it] = self.words[it].pack()
        stat_json = {"version": 2, "data": data}
        json.dump(stat_json, open(path, "wb"), indent=2)

    def global_statistic(self):
        stat = global_stat.GlobalStatistic()
        for it in self.words.values():
            if it.is_load():
                stat.add_word(it, it.get_stat(word.en_to_ru_write), it.get_stat(word.ru_to_en_write))
        return stat

    def _rename_check(self, old_en, new_en, new_ru):
        if len(new_en) == 0:
            raise ErrDict("Error word is empty", "err_en_word_empty")

        if len(new_ru) == 0:
            raise ErrDict("Error word is empty", "err_ru_word_empty")

        if old_en not in self.words.keys():
            raise ErrDict("Error find word", "err_find_en_word")

        new_en = new_en.lower()
        if old_en.strip().lower() != new_en:
            if new_en in map(lambda x: x.strip().lower(), self.words.keys()):
                raise ErrDict("Dublicate in load dict", "err_dublicate_en_word")

    def _rename_in_json_dict(self, old_en, new_en, new_tr, new_ru, json_dict):
        is_find = False
        old_en = old_en.strip().lower()
        lower_en = new_en.lower()
        for it in json_dict:
            en = it[0].strip().lower()
            if en == old_en:
                if len(it) == 2:
                    it.append("")
                it[0], it[1], it[2] = new_en, new_tr, new_ru
                is_find = True
            elif en == lower_en:
                raise ErrDict("Dublicate in file dict", "err_dublicate_en_word")
        if not is_find:
            json_dict.append([new_en, new_tr, new_ru])
        return json_dict

    def _rename_in_dict(self, old_en, new_en, new_tr, new_ru):
        w = self.words.pop(old_en)
        w.rename(new_en, new_tr, new_ru)
        self.words[new_en] = w

    def rename_word(self, old_en, new_en, new_tr, new_ru):
        new_en = new_en.strip()
        new_tr = new_tr.strip()
        new_ru = new_ru.strip()
        self._rename_check(old_en, new_en, new_ru)

        self.cfg.reload()

        json_dict = json.load(codecs.open(self.cfg["path_to_dict"], "rt", "utf-8"))
        json_dict = self._rename_in_json_dict(old_en, new_en, new_tr, new_ru, json_dict)
        self.reload_stat(self.cfg["path_to_stat"])
        self._rename_in_dict(old_en, new_en, new_tr, new_ru)
        self.save_dict(self.cfg["path_to_dict"], json_dict)
        self.save_stat(self.cfg["path_to_stat"])

    def _loaded_words(self, type_pr):
        return [(it, it.get_stat(type_pr)) for it in self.words.values() if it.is_load()]

    def words_for_lesson(self, cnt_study_words, type_pr):
        learned_words = []
        studied_words = []
        for wrd, stat in self._loaded_words(type_pr):
            if stat.get_total_answer() > 0:
                if stat.get_study_percent() >= 100.0:
                    learned_words.append(wrd)
                else:
                    studied_words.append(wrd)

        # дополняем изучаемыми/изученными словами из другого направления перевода
        if len(studied_words) < cnt_study_words:
            inv_type_pr = word.ru_to_en_write if type_pr == word.en_to_ru_write else word.en_to_ru_write
            for wrd, stat in self._loaded_words(inv_type_pr):
                if stat.get_total_answer() > 0 and wrd not in (learned_words + studied_words):
                    studied_words.append(wrd)
                    if len(studied_words) == cnt_study_words:
                        break

        # дополняем ни разу не изучаемыми словами
        if len(studied_words) < cnt_study_words:
            for wrd, stat in self._loaded_words(type_pr):
                if stat.get_total_answer() == 0 and wrd not in (learned_words + studied_words):
                    studied_words.append(wrd)
                    if len(studied_words) == cnt_study_words:
                        break

        studied_words.sort(key=lambda it: it.get_stat(type_pr).get_success_percent())
        studied_words = studied_words[:cnt_study_words]

        lesson_words = learned_words + studied_words
        for it in lesson_words:
            rating = it.get_stat(type_pr).calc_rating()
            it.set_rating(rating)
        return lesson_words


class DictTestCase(unittest.TestCase):
    "Набор тестов для класса Dict"

    def setUp(self):
        self.dict_obj = Dict(None)

    def create_word_data(self, num):
        return ["en" + str(num), "tr" + str(num), "ru" + str(num)]

    def create_word_stat(self, num):
        key = "en" + str(num)
        date = "2012.01"
        stat1 = [num * 1, num * 10, date + str(num), num % 2 == 0, float(num)]
        stat2 = [num * 20, num * 30, date + str(num + 1), num % 2 == 1, float(num * 2)]
        return [key, {"0": stat1, "1": stat2}]

    def json_dict(self, interval_from, interval_to):
        return [self.create_word_data(i) for i in range(interval_from, interval_to)]

    def load_dict(self, interval_from, interval_to):
        json_obj = self.json_dict(interval_from, interval_to)
        self.dict_obj.reload_dict_from_json(json_obj)

    def load_stat(self, interval_from, interval_to, version):
        json_data = dict([self.create_word_stat(i) for i in range(interval_from, interval_to)])
        json_stat = {"version": version, "data": json_data}
        self.dict_obj._reload_stat_from_json(json_stat)

    def assertLoad(self, num):
        dt = self.create_word_data(num)
        wrd_info = self.dict_obj.get_word_by_key("en" + str(num)).get_show_info()
        self.assertEqual((dt[0], "[%s]" % dt[1], dt[2]), wrd_info)

    def assertNotLoad(self, num):
        wrd_info = self.dict_obj.get_word_by_key("en" + str(num)).get_show_info()
        self.assertEqual(("", "", ""), wrd_info)

    def assertLoadStat(self, num):
        wrd1 = word.Word()
        wrd1.unpack(self.create_word_stat(num)[1])
        wrd2 = self.dict_obj.get_word_by_key("en" + str(num))
        self.assertEqual(wrd1.get_stat(0), wrd2.get_stat(0))
        self.assertEqual(wrd1.get_stat(1), wrd2.get_stat(1))

    def test_reload_dict(self):
        "Тест на загрузку словаря"
        interval_from = 0
        interval_to = 5
        self.load_dict(interval_from, interval_to)

        for i in range(interval_from, interval_to):
            self.assertLoad(i)

    def test_reload_dict_empty_tr(self):
        "Тест на загрузку словаря, в котором отсутствует или пустая транскрипция"
        json_obj = [["en0", "ru0"], ["en1", "", "ru1"], ["en2", "tr2", "ru2"]]
        self.dict_obj.reload_dict_from_json(json_obj)

        self.assertEqual(("en0", "", "ru0"), self.dict_obj.get_word_by_key("en0").get_show_info())
        self.assertEqual(("en1", "", "ru1"), self.dict_obj.get_word_by_key("en1").get_show_info())
        self.assertEqual(("en2", "[tr2]", "ru2"), self.dict_obj.get_word_by_key("en2").get_show_info())

    def test_reload_dict_err_key(self):
        "Тест на обращение к несуществующим словам"
        interval_from = 0
        interval_to = 5
        self.load_dict(interval_from, interval_to)

        for i in range(interval_to, interval_to * 2):
            self.assertNotLoad(i)

    def test_reload_dict_double_reload(self):
        "Тест на загрузку словаря дважды"
        interval_from1 = 0
        interval_to1 = 5
        self.load_dict(interval_from1, interval_to1)
        interval_from2 = 3
        interval_to2 = 8
        self.load_dict(interval_from2, interval_to2)

        for i in range(interval_from1, interval_from2):
            self.assertNotLoad(i)

        for i in range(interval_from2, interval_to2):
            self.assertLoad(i)

    def test_reload_stat(self):
        "Тест на загрузку статистики"
        interval_from = 0
        interval_to = 5
        self.load_dict(interval_from, interval_to)
        self.load_stat(interval_from, interval_to, 2)

        for i in range(interval_from, interval_to):
            self.assertLoad(i)
            self.assertLoadStat(i)

    def test_reload_stat_without_word(self):
        "Тест на загрузку статистики без словаря"
        interval_from = 0
        interval_to = 5
        self.load_stat(interval_from, interval_to, 2)

        for i in range(interval_from, interval_to):
            self.assertLoadStat(i)

    def test_reload_stat_double(self):
        "Тест на загрузку статистики дважды подряд"
        interval_from1 = 0
        interval_to1 = 5
        self.load_stat(interval_from1, interval_to1, 2)
        interval_from2 = 3
        interval_to2 = 8
        self.load_stat(interval_from2, interval_to2, 2)

        for i in range(interval_from1, interval_to2):
            self.assertLoadStat(i)

    def test_loaded_words(self):
        "Тест функции _loaded_words"
        interval_from1 = 0
        interval_to1 = 5
        self.load_dict(interval_from1, interval_to1)
        interval_from2 = 3
        interval_to2 = 9
        self.load_stat(interval_from2, interval_to2, 2)

        loaded_words = self.dict_obj._loaded_words(0)
        self.assertEqual(len(loaded_words), len(range(interval_from1, interval_to1)))

        for i, it in enumerate(loaded_words):
            self.assertEqual(it[0].get_show_info()[0], "en" + str(i))

    def test_words_for_lesson(self):
        "Тест выборки слов для изучения в текущем уроке"
        interval_from1 = 0
        interval_to1 = 5
        self.load_dict(interval_from1, interval_to1)

        w0 = self.dict_obj.get_word_by_key("en0")
        w1 = self.dict_obj.get_word_by_key("en1")
        w2 = self.dict_obj.get_word_by_key("en2")
        w3 = self.dict_obj.get_word_by_key("en3")

        w0.update_stat(False, 10, word.ru_to_en_write)
        w1.update_stat(True, 10, word.en_to_ru_write)
        w2.update_stat(True, 100, word.en_to_ru_write)

        words_list = self.dict_obj.words_for_lesson(3, word.en_to_ru_write)
        self.assertEqual(words_list, [w2, w0, w3, w1])
        self.assertEqual(len(words_list), 4)

    def test_load_error_stat_ver(self):
        "Тест на то, что генерируется исключение на неправильную версию файла со статистикой"
        try:
            self.load_stat(0, 1, 999)
            self.fail("except not found")
        except ErrDict:
            pass

    def test_convert_stat_v1_to_v2(self):
        "Тест на конвертацию формата статистики из v1 в v2"
        data = {
            "hello0": {"0": [0, 0, "any", "any"], "1": [0, 0, "any", "any"]},
            "hello1": {"0": [1, 0, "any", "any"], "1": [1, 1, "any", "any"]},
            "hello2": {"0": [9, 0, "any", "any"], "1": [9, 9, "any", "any"]},
            "hello3": {"0": [10, 0, "any", "any"], "1": [10, 10, "any", "any"]},
            "hello4": {"0": [20, 0, "any", "any"], "1": [20, 10, "any", "any"]}
        }
        data = statistic_v1_to_v2(data, 85.0, 10.0)
        self.assertEqual(data["hello0"]["0"], [0, 0, "any", "any", 0.0])
        self.assertEqual(data["hello0"]["1"], [0, 0, "any", "any", 0])

        self.assertAlmostEqual(data["hello1"]["0"][-1], 11.7647, 2)  # ((1 / 10) * 100 / 85) *100
        self.assertAlmostEqual(data["hello1"]["1"][-1], 10.6951, 2)  # ((1 / 11) * 100 / 85) *100

        self.assertAlmostEqual(data["hello2"]["0"][-1], 90.0000, 2)  # ((9 / 10) * 100 / 85) *100
        self.assertAlmostEqual(data["hello2"]["1"][-1], 55.7275, 2)  # ((9 / 19) * 100 / 85) *100

        self.assertAlmostEqual(data["hello3"]["0"][-1], 100.0000, 2)  # ((10 / 10) * 100 / 85) *100
        self.assertAlmostEqual(data["hello3"]["1"][-1], 58.8235, 2)  # ((10 / 20) * 100 / 85) *100

        self.assertAlmostEqual(data["hello4"]["0"][-1], 100.0000, 2)  # ((20 / 10) * 100 / 85) *100
        self.assertAlmostEqual(data["hello4"]["1"][-1], 78.4313, 2)  # ((20 / 30) * 100 / 85) *100

        data = {"hello0": {"0": [1, 0, "any", "any"], "1": [1, 1, "any", "any"]}}
        data = statistic_v1_to_v2(data, 85.0, 0.0)
        self.assertAlmostEqual(data["hello0"]["0"][-1], 11.7647, 2)  # ((1 / 10) * 100 / 85) *100
        self.assertAlmostEqual(data["hello0"]["1"][-1], 10.6951, 2)  # ((1 / 11) * 100 / 85) *100

        data = {"hello0": {"0": [1, 0, "any", "any"], "1": [10, 1, "any", "any"]}}
        data = statistic_v1_to_v2(data, 0.0, 10.0)
        self.assertAlmostEqual(data["hello0"]["0"][-1], 90.0000, 2)  # ((1 / 10) * 100 / 85) *100
        self.assertAlmostEqual(data["hello0"]["1"][-1], 100.0000, 2)  # ((1 / 11) * 100 / 85) *100

    def test_rename_check(self):
        "Тест на то, что корректно проходит проверка перед переименованием"

        self.load_dict(0, 2)

        try:
            # пустое новое английское слово
            self.dict_obj._rename_check("en0", "", "new_ru")
            self.fail("except not found")
        except ErrDict:
            pass

        try:
            # пустое новое русское слово
            self.dict_obj._rename_check("en0", "new_en", "")
            self.fail("except not found")
        except ErrDict:
            pass

        try:
            # старое слово не в списке ключей
            self.dict_obj._rename_check("en10", "new_en", "new_ru")
            self.fail("except not found")
        except ErrDict:
            pass

        try:
            # новое слово имеет дубликаты
            self.dict_obj._rename_check("en0", "EN1", "new_ru")
            self.fail("except not found")
        except ErrDict:
            pass

        # Корректное переименование
        self.dict_obj._rename_check("en0", "en0", "new_ru")
        self.dict_obj._rename_check("en0", "new_en", "new_ru")

    def test_rename_in_json_dict(self):
        "Тест на корректность переименования в словаре, который загрузили из файла"
        j_dict = self.json_dict(0, 2)

        import copy

        # Старое слово не в базе
        new_dict = self.dict_obj._rename_in_json_dict("en10", "new_en", "new_tr", "new_ru", copy.deepcopy(j_dict))
        self.assertEqual(new_dict, [["en0", "tr0", "ru0"], ["en1", "tr1", "ru1"], ["new_en", "new_tr", "new_ru"]])

        # Старое слово в базе
        new_dict = self.dict_obj._rename_in_json_dict("  en0 ", "new_en", "new_tr", "new_ru", copy.deepcopy(j_dict))
        self.assertEqual(new_dict, [["new_en", "new_tr", "new_ru"], ["en1", "tr1", "ru1"]])

        # Старое слово в базе
        new_dict = self.dict_obj._rename_in_json_dict(" En1 ", "new_en", "new_tr", "new_ru", copy.deepcopy(j_dict))
        self.assertEqual(new_dict, [["en0", "tr0", "ru0"], ["new_en", "new_tr", "new_ru"]])

        # Старое слово в базе и равно новому
        new_dict = self.dict_obj._rename_in_json_dict(" En1 ", "EN1", "new_tr", "new_ru", copy.deepcopy(j_dict))
        self.assertEqual(new_dict, [["en0", "tr0", "ru0"], ["EN1", "new_tr", "new_ru"]])

        # # английское слово имеет дубликаты не равные старому слову
        try:
            self.dict_obj._rename_in_json_dict("en1", "EN0", "new_tr", "new_ru", copy.deepcopy(j_dict))
            self.fail("except not found")
        except ErrDict:
            pass

    def test_rename_in_dict(self):
        "Тест на корректность переименования в загруженных данных"
        self.load_dict(0, 2)
        old_word = self.dict_obj.get_word_by_key("en0")

        self.dict_obj._rename_in_dict("en0", "new_en", "new_tr", "new_ru")

        new_word = self.dict_obj.get_word_by_key("new_en")
        self.assertEqual(("new_en", "[%s]" % "new_tr", "new_ru"), new_word.get_show_info())
        self.assertLoad(1)
        self.assertEqual(len(self.dict_obj.words), 2)
        self.assertEqual(old_word is new_word, True)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    suite = unittest.TestLoader().loadTestsFromTestCase(DictTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
