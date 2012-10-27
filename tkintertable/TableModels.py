# -*- coding: utf-8 -*-

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
        self.set_default()

    def set_default(self):
        self.columns         = []
        self.sort_index      = None
        self.sort_is_reverse = True

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
        self.set_default()

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
        self.set_default()

    def set_default(self):
        self.rows = []
        self.cnt_col = 0

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
        self.set_default()

    def sort(self, col, is_reverse, typedata):
        def key(row):
            sort_key = row[col]
            if typedata == 'number':
                sort_key = float(sort_key)
            return (sort_key)
        self.rows = sorted(self.rows, key = key, reverse = is_reverse)

class TableModel(object):
    def __init__(self):
        self.columns = ColumnList()
        self.data    = RowList()

    def add_column(self, caption, width = None, typedata = None):
        self.columns.add(caption, width, typedata)
        self.data.create(self.columns.count())

    def add_row(self, row):
        self.data.add(row)

    def resort(self, col):
        is_reverse = not self.get_sort_is_reverse()
        self.columns.set_sort(col, is_reverse)
        self.data.sort(col, is_reverse, self.columns.get(col).typedata)

    def get_column_count(self):
        return self.columns.count()

    def get_row_count(self):
        return self.data.count_row()

    def get_column(self, col):
        return self.columns.get(col)

    def get_value(self, col, row):
        return self.data.get(col, row)

    def get_sort_index(self):
        return self.columns.get_sort_index()

    def get_sort_is_reverse(self):
        return self.columns.get_sort_is_reverse()

    def clear(self):
        self.columns.clear()
        self.data.clear()