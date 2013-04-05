# -*- coding: utf-8 -*-

import webbrowser
from operation import BaseOperation


class OperationFindInWeb(BaseOperation):

    def __init__(self, cfg):
        BaseOperation.__init__(self)
        self._cfg = cfg

    def execute(self, word, is_rur):
        options = self._cfg["internet_dictionary_url"]
        template = options["RU_EN"] if is_rur else options["EN_RU"]
        url = template.replace("{word}", word)
        webbrowser.open(url)


def _test_run():
    from config import Config
    cfg = Config()
    cfg.reload()
    OperationFindInWeb(cfg).execute(u"hello", False)
    OperationFindInWeb(cfg).execute(u"привет", True)

if __name__ == '__main__':
    _test_run()
