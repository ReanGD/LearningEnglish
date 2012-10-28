# -*- coding: utf-8 -*-

import math

class ErrColumnList(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class ErrRowList(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class ErrTableModel(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class Column:
    def __init__(self, caption, width = None, typedata = None):
        if len(caption) == 0:
            raise ErrColumnList("Create a column with an empty caption")
        self.caption = caption
        if width == None:
            width = len(caption)*10
        self.width = width
        if typedata == None:
            typedata = 'text'
        self.typedata = typedata

class ColumnList(object):
    def __init__(self):
        self.clear()

    def get(self, col):
        if self.count() > col:
            return self.columns[col]
        else:
            return None

    def count(self):
        return len(self.columns)

    def add(self, caption, width = None, typedata = None):
        self.columns.append(Column(caption, width, typedata))

    def clear(self):
        self.columns         = []
        self.sort_index      = None
        self.sort_is_reverse = True

    def get_sort_index(self):
        return self.sort_index

    def get_sort_is_reverse(self):
        return self.sort_is_reverse

    def set_sort(self, col, is_reverse):
        if self.count() <= col:
            msg = 'sort by column "%i", that does not exist' % col
            raise ErrColumnList(msg)
        self.sort_index      = col
        self.sort_is_reverse = is_reverse

class RowList(object):
    def __init__(self):
        self.clear()

    def get(self, col, row):
        if self.count_col() > col and self.count_row() > row:
            return self.rows[row][col]

    def count_col(self):
        return self.cnt_col

    def count_row(self):
        return len(self.rows)

    def create(self, cnt_col):
        self.clear()
        if cnt_col <= 0:
            raise ErrRowList('Number of columns must be greater than 0')
        self.cnt_col = cnt_col

    def add(self, row):
        if self.count_col() != len(row):
            msg = 'number of elements in the row should be = %i' % self.count_col()
            raise ErrRowList(msg)
        self.rows.append(row)

    def clear(self):
        self.rows = []
        self.cnt_col = 0

    def sort(self, col, is_reverse, typedata):
        def key(row):
            sort_key = row[col]
            if typedata == 'number':
                sort_key = float(sort_key)
            return (sort_key)
        self.rows = sorted(self.rows, key = key, reverse = is_reverse)

class TableModel(object):
    def __init__(self, rowsperpage = 100, paginal = True):
        if rowsperpage <= 0:
            rowsperpage = 100
        self.rowsperpage = rowsperpage
        self.paginal     = paginal
        self.currentpage = 0
        self.rowrange    = []
        self.columns     = ColumnList()
        self.data        = RowList()
        self.recalc_page(0)

    def add_column(self, caption, width = None, typedata = None):
        self.columns.add(caption, width, typedata)
        self.data.create(self.columns.count())
        self.recalc_page(self.currentpage)

    def add_row(self, row):
        self.data.add(row)
        self.recalc_page(self.currentpage)

    def resort(self, col):
        is_reverse = not self.get_sort_is_reverse()
        self.columns.set_sort(col, is_reverse)
        self.data.sort(col, is_reverse, self.columns.get(col).typedata)

    def recalc_page(self, col):
        self.currentpage = col
        if self.paginal:
            lower = self.currentpage*self.rowsperpage
            upper = min(lower+self.rowsperpage, self.get_row_count())
            self.rowrange = range(lower, upper)
        else:
            self.rowrange = range(0, self.get_row_count())

    def goto_first_page(self):
        if self.currentpage != 0:
            self.recalc_page(0)
            return True
        return False

    def goto_last_page(self):
        if self.currentpage != self.get_pages_count()-1:
            self.recalc_page(self.get_pages_count()-1)
            return True
        return False

    def goto_prev_page(self):
        if self.currentpage > 0:
            self.recalc_page(self.currentpage - 1)
            return True
        return False

    def goto_next_page(self):
        if self.currentpage < self.get_pages_count()-1:
            self.recalc_page(self.currentpage + 1)
            return True
        return False

    def get_column_count(self):
        return self.columns.count()

    def get_row_count(self):
        return self.data.count_row()

    def get_page_row_count(self):
        return len(self.rowrange)

    def get_pages_count(self):
        if self.paginal:
            return math.trunc(math.ceil(float(self.data.count_row())/self.rowsperpage))
        else:
            return 1

    def get_current_page(self):
        return self.currentpage

    def page_row_to_absolute_row(self, row):
        return row+self.currentpage*self.rowsperpage

    def get_column(self, col):
        return self.columns.get(col)

    def get_value(self, col, row):
        return self.data.get(col, row)

    def get_page_rows(self):
        return self.rowrange

    def get_sort_index(self):
        return self.columns.get_sort_index()

    def get_sort_is_reverse(self):
        return self.columns.get_sort_is_reverse()

    def is_paginal(self):
        return self.paginal

    def set_paginal(self, is_paginal):
        self.paginal = is_paginal
        self.recalc_page(0)

    def clear(self):
        self.columns.clear()
        self.data.clear()
        self.recalc_page(0)