# -*- coding: utf-8 -*-

import random
import unittest


class LessonWords:
    """ Назначение класса:
        выдача слов из набора по рейтингу (чем выше рейтинг, тем выше шанс, что класс вернет это слово)
        слова в выдаче должны повторяться минимальное кол-во раз
    """

    def __init__(self, words):
        self.all_words = words
        self.remaining_words = self.all_words[:]

    def get_any_word(self):
        cnt_word = len(self.remaining_words)
        if cnt_word == 0:
            self.remaining_words = self.all_words[:]
            cnt_word = len(self.remaining_words)

        if cnt_word == 1:
            wrd = self.remaining_words[0]
            self.remaining_words.remove(wrd)
        else:
            max_rating = max([wrd.get_rating() for wrd in self.remaining_words])
            it_cnt = 0
            while True:
                wrd = random.choice(self.remaining_words)
                it_cnt += 1
                if it_cnt > 1000:
                    self.remaining_words.remove(wrd)
                    break
                if wrd.get_rating() > random.random() * max_rating:
                    self.remaining_words.remove(wrd)
                    break
        return wrd


class WordMock:
    def __init__(self, rating):
        self.rating = rating

    def get_rating(self):
        return self.rating


class LessonWordsTestCase(unittest.TestCase):
    def get_any_word(self, wrd):
        self.assertTrue(wrd in self.words)
        self.assertFalse(wrd in self.used_words)
        self.used_words.append(wrd)

    def test_get_any_word(self):
        self.words = [WordMock(1), WordMock(2), WordMock(3)]
        self.used_words = []
        lw = LessonWords(self.words)

        self.get_any_word(lw.get_any_word())
        self.get_any_word(lw.get_any_word())
        self.get_any_word(lw.get_any_word())
        self.used_words = []
        self.get_any_word(lw.get_any_word())
        self.get_any_word(lw.get_any_word())
        self.get_any_word(lw.get_any_word())

if __name__ == "__main__":
    import os
    import os.path
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    suite = unittest.TestLoader().loadTestsFromTestCase(LessonWordsTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
