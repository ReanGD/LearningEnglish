# -*- coding: utf-8 -*-

from Tkinter import *
from loc_res import _
from GUI_config import *
from top_dialog import TopDialog
from operation import BaseOperation
from tkintertable.Tables import TableCanvas
from tkintertable.TableModels import TableModel


class _StatisticDialog(TopDialog):
    def __init__(self, parent, factory, statistic, stat_count_row):
        TopDialog.__init__(self, parent, (statistic, stat_count_row))
        self.factory = factory
        self.title(_("win_statistic_title"))
        self.wait_visibility()
        self.set_size(self.table_detailed_stat.get_totalWidth(), 750)
        self.resizable(True, True)
        self.grab_set()
        self.run()

    def init_common_stat(self, statistic):
        self.frame_common_stat = Frame(self)
        self.frame_common_stat.grid(row=1, column=0, sticky=N + S + E + W)

        model_common_stat = TableModel(10, False)
        model_common_stat.add_column(_("clm_name"), typedata='text', align='left')
        model_common_stat.add_column(_("clm_ru_en_cnt"), typedata='number', align='right', max_val=u"99999")
        model_common_stat.add_column(_("clm_en_ru_cnt"), typedata='number', align='right', max_val=u"99999")
        model_common_stat.add_column(_("clm_ru_en_perc"), typedata='percent', align='right', max_val=u"100.0 %")
        model_common_stat.add_column(_("clm_en_ru_perc"), typedata='percent', align='right', max_val=u"100.0 %")

        row_name = [[_("row_learned")], [_("row_study")], [_("row_learn")], [_("row_total")]]
        for row in [row_name[i] + it for i, it in enumerate(statistic.get_common_stat())]:
            model_common_stat.add_row(row)

        self.table_common_stat = TableCanvas(self.frame_common_stat, model_common_stat, sort_enable=False)
        self.table_common_stat.createTableFrame()
        self.frame_common_stat.grid_forget()

    def init_detailed_stat(self, statistic, stat_count_row):
        self.frame_detailed_stat = Frame(self)
        self.frame_detailed_stat.grid(row=1, column=0, sticky=N + S + E + W)

        self.model_ru_en = TableModel(stat_count_row, True)
        self.model_ru_en.add_column(_("clm_word"), typedata='text', align='left')
        self.model_ru_en.add_column(_("clm_transcription"), typedata='text', align='left')
        self.model_ru_en.add_column(_("clm_translate"), typedata='text', align='left')
        self.model_ru_en.add_column(_("clm_cnt_suc"), typedata='number', align='right', max_val=u"999")
        self.model_ru_en.add_column(_("clm_cnt_err"), typedata='number', align='right', max_val=u"999")
        self.model_ru_en.add_column(_("clm_study_perсent"), typedata='percent', align='right', max_val=u"100.0 %")

        for row, word in statistic.get_ru_en():
            self.model_ru_en.add_row(row, word)
        self.model_ru_en.sort(5, True)

        self.table_detailed_stat = TableCanvas(self.frame_detailed_stat, self.model_ru_en, sort_enable=True,
                                               callback=self.draw_callback, dbl_click_callback=self.rename_dlg)
        self.table_detailed_stat.createTableFrame()

        self.model_en_ru = TableModel(stat_count_row, True)
        self.model_en_ru.add_column(_("clm_word"), typedata='text', align='left')
        self.model_en_ru.add_column(_("clm_transcription"), typedata='text', align='left')
        self.model_en_ru.add_column(_("clm_translate"), typedata='text', align='left')
        self.model_en_ru.add_column(_("clm_cnt_suc"), typedata='number', align='right')
        self.model_en_ru.add_column(_("clm_cnt_err"), typedata='number', align='right')
        self.model_en_ru.add_column(_("clm_study_perсent"), typedata='percent', align='right')

        for row, word in statistic.get_en_ru():
            self.model_en_ru.add_row(row, word)
        self.model_en_ru.sort(5, True)

        for col in range(0, self.model_en_ru.get_column_count()):
            self.model_en_ru.get_column(col).width = self.model_ru_en.get_column(col).width

    def button_add(self, text, command):
        self.buttons.append(Button(self.frame_btn, text=text, command=command, borderwidth=2, default="normal"))
        ind = len(self.buttons)
        self.buttons[-1].grid(row=0, column=ind, sticky=N + S + E + W, pady=5, padx=3)

    def button_sel(self, cur_button):
        self.last_button = cur_button
        for i, it in enumerate(self.buttons):
            if i == cur_button:
                it.configure(relief="sunken")
            else:
                it.configure(relief="raised")
        self.update_idletasks()

    def init_window(self, (statistic, stat_count_row)):
        self.last_button = 0
        self.buttons = []

        self.frame_btn = Frame(self, borderwidth=2, relief=GROOVE)
        self.frame_btn.grid(row=0, column=0, sticky=N + S + E + W)
        Label(self.frame_btn, text="").grid(row=0, column=0)
        self.button_add(_("btn_ru_en"), self.show_ru_en)
        self.button_add(_("btn_en_ru"), self.show_en_ru)
        self.button_add(_("btn_common_stat"), self.show_common_stat)
        Label(self.frame_btn, text="").grid(row=0, column=4)

        self.frame_btn.grid_rowconfigure(0, weight=1)
        self.frame_btn.grid_columnconfigure(1, weight=1)
        self.frame_btn.grid_columnconfigure(2, weight=1)
        self.frame_btn.grid_columnconfigure(3, weight=1)

        self.init_common_stat(statistic)
        self.init_detailed_stat(statistic, stat_count_row)

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.button_sel(0)
        self.show_ru_en()

    def rename_dlg(self, word, row):
        self.rn_word = word
        self.rn_row = row
        self.factory.get_operation("EditWord").set_callback(self.rename_word).execute(self, word.get_source_info())
        self.rn_word = None
        self.rn_row = None

    def rename_word(self):
        if self.rn_word is not None and self.rn_row is not None:
            en_word, transcription, ru_word = self.rn_word.get_show_info()
            row = self.rn_row
            self.model_ru_en.set_value(0, row, en_word)
            self.model_ru_en.set_value(1, row, transcription)
            self.model_ru_en.set_value(2, row, ru_word)
            self.model_en_ru.set_value(0, row, en_word)
            self.model_en_ru.set_value(1, row, transcription)
            self.model_en_ru.set_value(2, row, ru_word)
            self.table_detailed_stat.redrawTable()

    def draw_callback(self, row, col, celltxt, clr):
        if col == 5:
            pr = float(celltxt.strip("% "))
            if pr >= 100.0:
                return celltxt, clr_stat[0]
            elif pr > 0.0:
                return celltxt, clr_stat[1]
            else:
                return "0.0 %", clr_stat[2]
        else:
            return celltxt, clr

    def show_ru_en(self):
        if self.last_button != 0:
            self.button_sel(0)
            self.table_detailed_stat.setModel(self.model_ru_en)
            self.frame_common_stat.grid_forget()
            self.frame_detailed_stat.grid(row=1, column=0, sticky=N + S + E + W)
        self.table_detailed_stat.do_bindings()

    def show_en_ru(self):
        if self.last_button != 1:
            self.button_sel(1)
            self.table_detailed_stat.setModel(self.model_en_ru)
            self.frame_common_stat.grid_forget()
            self.frame_detailed_stat.grid(row=1, column=0, sticky=N + S + E + W)
        self.table_detailed_stat.do_bindings()

    def show_common_stat(self):
        if self.last_button != 2:
            self.button_sel(2)
            self.frame_detailed_stat.grid_forget()
            self.frame_common_stat.grid(row=1, column=0, sticky=N + S + E + W)
        self.table_common_stat.do_bindings()


class OperationShowStatistic(BaseOperation):

    def __init__(self, dictionary, cfg, factory):
        BaseOperation.__init__(self)
        self._dictionary = dictionary
        self._cfg = cfg
        self._factory = factory

    def execute(self, parent):
        _StatisticDialog(parent, self._factory, self._dictionary.global_statistic(), self._cfg["stat_count_row"])
        self.callback()


def run_exclusive():
    from config import Config
    cfg = Config()
    cfg.reload()

    from dictionary import Dict
    dictionary = Dict(cfg)
    dictionary.reload_dict(cfg["path_to_dict"])
    dictionary.reload_stat(cfg["path_to_stat"])

    from oper_factory import OperationFactory
    factory = OperationFactory()
    factory.create(dictionary, cfg)

    tk = Tk()
    tk.withdraw()
    factory.get_operation("ShowStatistic").execute(tk)


def _test_run():
    import os
    import os.path
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    run_exclusive()

if __name__ == '__main__':
    _test_run()
