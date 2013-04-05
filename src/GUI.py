# -*- coding: utf-8 -*-

from tkFont import Font
from Tkinter import *
from loc_res import _
from GUI_config import *
import tkSimpleDialog


class CloseDialog(tkSimpleDialog.Dialog):
    def body(self, master):
        self.var = IntVar(0)
        Radiobutton(master, text=_("end_lesson"), variable=self.var, value=0).grid(sticky="w")
        Radiobutton(master, text=_("end_program"), variable=self.var, value=1).grid(sticky="w")
        self.resizable(False, False)
        return None

    def apply(self):
        self.result = self.var.get()


class MainWindow(Tk):
    def __init__(self, factory):
        Tk.__init__(self)
        self.factory = factory
        self.state = "waiting_for_answer"
        self.lbl_word = None
        self.lbl_transcription = None
        self.lbl_result_msg = None
        self.lbl_correct_word = None
        self.lbl_correct_word_tr = None
        self.edit_translate = None
        self.init_window()

    def init_window(self):
        # 12pt = 16px
        fnt_stat = Font(family="Arial", size=-12)  # 9pt
        fnt_msg = Font(family="Arial", size=-13, weight="bold")  # 10pt
        fnt_word = Font(family="Arial", size=-19)  # 14pt
        fnt_transcription = Font(family="Arial", size=-13)  # 10pt
        self.fnt_answer_normal = Font(family="Arial", size=-16)  # 12pt
        self.fnt_answer_error = Font(family="Arial", size=-16, overstrike=1)  # 12pt

        ########################################################

        frm_stat = Frame(self, bg=clr_stat_frame, bd=5)
        frm_stat.pack(fill="both")

        Label(frm_stat, font=fnt_stat, bg=clr_stat_frame, text=_("correct_incorrect")).pack(side="left")

        frm_btn = Frame(frm_stat, bg=clr_stat_frame)
        frm_btn.pack(side="right")

        img = stat_image()
        bt = Button(frm_btn, image=img, bg=clr_stat_frame, relief="flat", command=self.on_show_statistic_wnd)
        bt.image = img
        bt.pack(side="right")

        img = find_in_web_image()
        self.find_in_web_btn = Button(frm_btn, image=img, bg=clr_stat_frame, relief="flat", command=self.on_find_in_web)
        self.find_in_web_btn.image = img
        self.find_in_web_btn.pack(side="right")

        img = edit_image()
        self.edit_btn = Button(frm_btn, image=img, bg=clr_stat_frame, relief="flat", command=self.on_rename)
        self.edit_btn.image = img
        self.edit_btn.pack(side="right")

        self.lbl_stat_error = Label(frm_stat, font=fnt_stat, bg=clr_stat_frame, fg=clr_error, borderwidth=0)
        self.lbl_stat_error.pack(side="right")

        self.lbl_stat_success = Label(frm_stat, font=fnt_stat, bg=clr_stat_frame, fg=clr_success, borderwidth=0)
        self.lbl_stat_success.pack(side="right")

        ########################################################

        frm_word = Frame(self, bg=clr_word_frame, bd=5)
        frm_word.pack(fill="both")

        self.lbl_word = Label(frm_word, font=fnt_word, bg=clr_word_frame)
        self.lbl_word.pack()

        self.lbl_transcription = Label(frm_word, font=fnt_transcription, bg=clr_word_frame)
        self.lbl_transcription.pack()

        ########################################################

        frm_answer = Frame(self, bg=clr_answer_frame, bd=15)
        frm_answer.pack(fill="both")

        frm_message = Frame(frm_answer, bg=clr_answer_frame)
        frm_message.pack(fill="both")

        self.lbl_result_msg = Label(frm_message, font=fnt_msg, bg=clr_answer_frame)
        self.lbl_result_msg.pack(side="left")

        self.lbl_correct_word = Label(frm_message, font=fnt_msg, bg=clr_answer_frame)
        self.lbl_correct_word.pack(side="left")

        self.lbl_correct_word_tr = Label(frm_message, font=fnt_transcription, bg=clr_answer_frame)
        self.lbl_correct_word_tr.pack(side="left")

        self.edit_translate = Entry(frm_answer, width=35)
        self.edit_translate.pack(fill="both")
        self.edit_translate.focus()

        self.bind("<Return>", self.on_return)
        self.bind("<Control-Return>", self.on_rename)
        self.bind("<FocusIn>", lambda event: self.edit_translate.focus())
        ########################################################

        x = (self.winfo_screenwidth() - self.winfo_reqwidth()) / 2
        y = (self.winfo_screenheight() - self.winfo_reqheight()) / 2
        self.title(_("win_learning_english"))
        self.resizable(False, False)
        self.wm_geometry("+%d+%d" % (x, y))
        self.protocol("WM_DELETE_WINDOW", self.on_destroy)

    def new_lesson(self):
        pass

    def end_lesson(self):
        pass

    def new_practice(self):
        pass

    def end_practice(self, user_answer):
        pass

    def rename_word(self):
        pass

    def get_source_info(self):
        pass

    def is_rur(self):
        pass

    def show(self):
        self.deiconify()
        self.edit_translate.focus()
        start_time_delay = self.cfg["start_time_delay"]

        if start_time_delay > 0:
            def enable_edit():
                self.edit_translate["state"] = "normal"
                self.edit_translate.focus()
            self.edit_translate["state"] = "readonly"
            self.edit_translate.after(start_time_delay * 1000, enable_edit)

    def hide(self):
        self.withdraw()

    def set_question(self, new_word):
        self.show_find_in_web_btn(False)
        self.show_edit_word_btn(False)
        self.lbl_word["text"] = new_word.word
        self.lbl_transcription["text"] = "" if self.cfg["hide_transcription"] == "yes" else new_word.transcription
        self.lbl_result_msg["text"] = ""
        self.lbl_correct_word["text"] = ""
        self.lbl_correct_word_tr["text"] = ""
        self.edit_translate["state"] = "normal"
        self.edit_translate["font"] = self.fnt_answer_normal
        self.edit_translate['fg'] = clr_black
        self.edit_translate.delete(0, END)

    def set_statistic(self, stat):
        success_cnt, max_success, error_cnt = stat
        self.lbl_stat_success["text"] = "%i %s %i/" % (success_cnt, _("of"), max_success)
        self.lbl_stat_error["text"] = "%i" % error_cnt

    def set_right_answer(self, right_answer):
        self.edit_translate["state"] = "readonly"
        self.edit_translate["font"] = self.fnt_answer_normal
        self.edit_translate['fg'] = clr_black
        self.lbl_correct_word["text"] = right_answer.word
        self.lbl_correct_word_tr["text"] = "" if self.cfg["hide_transcription"] == "yes" else right_answer.transcription
        self.lbl_result_msg["text"] = _("correct")
        self.lbl_result_msg["fg"] = clr_success
        self.show_find_in_web_btn(True)
        self.show_edit_word_btn(True)

    def set_wrong_answer(self, right_answer):
        self.edit_translate["state"] = "readonly"
        self.edit_translate["font"] = self.fnt_answer_error
        self.edit_translate['fg'] = clr_error
        self.lbl_correct_word["text"] = right_answer.word
        self.lbl_correct_word_tr["text"] = "" if self.cfg["hide_transcription"] == "yes" else right_answer.transcription
        self.lbl_result_msg["text"] = _("incorrect")
        self.lbl_result_msg["fg"] = clr_error
        self.show_find_in_web_btn(True)
        self.show_edit_word_btn(True)

    def set_repeat(self):
        self.lbl_result_msg["text"] = _("reiterate")
        self.lbl_result_msg["fg"] = clr_error

    def set_new_word(self):
        self.lbl_result_msg["text"] = _("lbl_new_word")
        self.lbl_result_msg["fg"] = clr_error

    def show_edit_word_btn(self, is_show):
        if is_show:
            self.edit_btn.pack(side="right")
        else:
            self.edit_btn.pack_forget()

    def show_find_in_web_btn(self, is_show):
        if is_show:
            self.find_in_web_btn.pack(side="right")
        else:
            self.find_in_web_btn.pack_forget()

    def on_return(self, event):
        if self.state == "waiting_for_answer":
            user_answer = self.edit_translate.get()
            if self.cfg["empty_answer_is_error"] == "no" and user_answer.strip() == "":
                return
            self.end_practice(user_answer)
            self.state = "continue"
        elif self.state == "continue":
            self.new_practice()
            self.state = "waiting_for_answer"

    def on_show_statistic_wnd(self, event=None):
        self.factory.get_operation("ShowStatistic").execute(self)

    def on_rename(self, event=None):
        if self.state == "continue":
            self.factory.get_operation("EditWord").set_callback(self.rename_word).execute(self, self.get_source_info())

    def on_find_in_web(self, event=None):
        if self.state == "continue":
            self.factory.get_operation("FindInWeb").execute(self.lbl_word["text"], self.is_rur())

    def on_destroy(self):
        dlg = CloseDialog(self)
        if dlg.result == 1:
            self.end_lesson()
            self.quit()
        elif dlg.result == 0:
            self.end_lesson()


def _look_1(wnd):
    success_cnt = 1
    max_success = 5
    error_cnt = 2
    wnd.set_statistic((success_cnt, max_success, error_cnt))
    import word
    wnd.set_question(word.WordInfo(u"gaze", u"[geiz]"))
    wnd.edit_translate["textvariable"] = StringVar(value="пристальный взгляд")


def _look_2(wnd):
    success_cnt = 1
    max_success = 5
    error_cnt = 2
    wnd.set_statistic((success_cnt, max_success, error_cnt))
    import word
    wnd.set_question(word.WordInfo(u"пристальный взгляд, вглядываться", u""))
    wnd.edit_translate["textvariable"] = StringVar(value="gaze")


def _look_3(wnd):
    success_cnt = 1
    max_success = 5
    error_cnt = 2
    wnd.set_statistic((success_cnt, max_success, error_cnt))
    import word
    wnd.set_question(word.WordInfo(u"Hello", u"[\'he\'ləu]"))
    wnd.edit_translate["textvariable"] = StringVar(value=u"Привет")
    wnd.set_repeat()


def _look_4(wnd):
    success_cnt = 1
    max_success = 5
    error_cnt = 2
    wnd.set_statistic((success_cnt, max_success, error_cnt))
    import word
    wnd.set_question(word.WordInfo(u"Hello", u"[\'he\'ləu]"))
    wnd.edit_translate["textvariable"] = StringVar(value=u"Привет")
    wnd.set_new_word()


def _look_5(wnd):
    success_cnt = 1
    max_success = 5
    error_cnt = 2
    wnd.set_statistic((success_cnt, max_success, error_cnt))
    import word
    wnd.set_question(word.WordInfo(u"пристальный взгляд, вглядываться", u""))
    wnd.edit_translate["textvariable"] = StringVar(value=u"gaze")
    wnd.set_right_answer(word.WordInfo(u"gaze", u"[geiz]"))


def _look_6(wnd):
    success_cnt = 1
    max_success = 5
    error_cnt = 2
    wnd.set_statistic((success_cnt, max_success, error_cnt))
    import word
    wnd.set_question(word.WordInfo(u"gaze", u"[geiz]"))
    wnd.edit_translate["textvariable"] = StringVar(value=u"вглядываться")
    wnd.set_right_answer(word.WordInfo(u"пристальный взгляд, вглядываться", u""))


def _look_7(wnd):
    success_cnt = 1
    max_success = 5
    error_cnt = 2
    wnd.set_statistic((success_cnt, max_success, error_cnt))
    import word
    wnd.set_question(word.WordInfo(u"Hello", u"[\'he\'ləu]"))
    wnd.edit_translate["textvariable"] = StringVar(value=u"Пока")
    wnd.set_wrong_answer(word.WordInfo(u"Привет", u""))


class _LookManager:
    def __init__(self, wnd):
        self.wnd = wnd
        self.looks = [_look_1, _look_2, _look_3, _look_4, _look_5, _look_6, _look_7]
        self.it = -1

    def next(self, event=None):
        self.it += 1
        if self.it == len(self.looks):
            self.it = 0
        self.looks[self.it](self.wnd)


def _test_run():
    wnd = MainWindow(None)
    manager = _LookManager(wnd)
    wnd.bind("<Return>", manager.next)
    import config
    wnd.cfg = config.Config("fake_config.json", "fake_config_user.json")
    wnd.cfg.reload()
    manager.next()
    wnd.mainloop()

if __name__ == '__main__':
    _test_run()
