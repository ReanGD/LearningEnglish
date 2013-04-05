# -*- coding: utf-8 -*-

import random
import word
import dictionary
import lesson_words


class Practice:
    def __init__(self, lesson, word, type_pr):
        self.lesson = lesson
        self.word = word
        self.type_pr = type_pr
        self.result = None
        self.is_answer = False

    def question_data(self):
        return self.word.question_data(self.type_pr)

    def is_new(self):
        return self.word.is_new(self.type_pr)

    def is_rur(self):
        return self.type_pr == word.ru_to_en_write

    def get_source_info(self):
        return self.word.get_source_info()

    def update_stat(self, right_answer_percent, wrong_answer_percent):
        if self.result is not None:
            add_percent = right_answer_percent if self.result else -wrong_answer_percent
            self.word.update_stat(self.result, add_percent, self.type_pr)

    def is_end(self):
        return self.is_answer

    def check(self, user_answer):
        is_success, right_answer = self.word.check(user_answer, self.type_pr)
        self.is_answer = is_success
        if self.result is None:
            self.result = is_success
            self.lesson.update_stat(is_success)
        return is_success, right_answer

    def last_result(self):
        type_pr = word.ru_to_en_write if self.type_pr == word.en_to_ru_write else word.en_to_ru_write
        return self.is_answer, self.word.question_data(type_pr)


class Lesson:
    def __init__(self, cfg):
        random.seed()
        self.type_pr = random.choice([word.en_to_ru_write, word.ru_to_en_write])
        self.dict = dictionary.Dict(cfg)
        self.right_answer_percent = cfg["right_answer_percent"]
        self.wrong_answer_percent = cfg["wrong_answer_percent"]
        self.max_success = cfg["words_per_lesson"]
        self.cnt_success = 0
        self.cnt_error = 0
        self.path_to_stat = cfg["path_to_stat"]
        self.practice_list = []
        self.dict.reload_dict(cfg["path_to_dict"])
        self.dict.reload_stat(self.path_to_stat)
        words = self.dict.words_for_lesson(cfg["CntStudyWords"], self.type_pr)
        self.lsn_words = lesson_words.LessonWords(words)

    def get_dict(self):
        return self.dict

    def update_stat(self, is_success):
        if is_success:
            self.cnt_success += 1
        else:
            self.cnt_error += 1

    def end_lesson(self):
        self.dict.reload_stat(self.path_to_stat)

        for it in self.practice_list:
            it.update_stat(self.right_answer_percent, self.wrong_answer_percent)

        self.dict.save_stat(self.path_to_stat)

    def get_next_practice(self):
        pr = Practice(self, self.lsn_words.get_any_word(), self.type_pr)
        self.practice_list.append(pr)
        return pr

    def get_lesson_stat(self):
        return (self.cnt_success, self.max_success, self.cnt_error)

    def is_end_lesson(self):
        return self.max_success == self.cnt_success
