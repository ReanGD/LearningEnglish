# -*- coding: utf-8 -*-

import sys
import lesson
import config
import dictionary
from GUI import MainWindow
from oper_factory import OperationFactory
import error_dialog


class App(MainWindow):
    def __init__(self):
        self.lesson = None
        self.practice = None
        self.cfg = config.Config()
        self.cfg.create_default_user_config()
        self.factory = OperationFactory()
        MainWindow.__init__(self, self.factory)
        self.new_lesson()
        self.mainloop()

    def new_lesson(self):
        self.cfg.reload()
        try:
            self.lesson = lesson.Lesson(self.cfg)
        except dictionary.ErrDict as err:
            error_dialog.show_critical_error(err.loc_res_msg)
            sys.exit(0)

        self.factory.create(self.lesson.get_dict(), self.cfg)
        self.practice = None
        self.new_practice()
        self.show()

    def end_lesson(self):
        try:
            self.lesson.end_lesson()
        except dictionary.ErrDict as err:
            error_dialog.show_critical_error(err.loc_res_msg)
            sys.exit(0)
        self.hide()
        retry_time = self.cfg["retry_time"] * 1000
        self.after(retry_time, self.new_lesson)

    def new_practice(self):
        if self.lesson.is_end_lesson():
            self.end_lesson()
        else:
            is_first_question = (self.practice is None or self.practice.is_end())
            if is_first_question:
                self.practice = self.lesson.get_next_practice()
            new_word = self.practice.question_data()
            is_new_word = self.practice.is_new()
            self.set_statistic(self.lesson.get_lesson_stat())
            self.set_question(new_word)
            if is_first_question:
                if is_new_word:
                    self.set_new_word()
            else:
                self.set_repeat()

    def end_practice(self, user_answer):
        is_success, right_answer = self.practice.check(user_answer)
        if is_success:
            self.set_right_answer(right_answer)
        else:
            self.set_wrong_answer(right_answer)

    def rename_word(self):
        cur_word = self.practice.question_data()
        self.set_question(cur_word)
        is_success, right_answer = self.practice.last_result()
        if is_success:
            self.set_right_answer(right_answer)
        else:
            self.set_wrong_answer(right_answer)

    def get_source_info(self):
        return self.practice.get_source_info()
