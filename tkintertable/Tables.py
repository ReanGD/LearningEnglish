# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
    Created Oct 2008
    TablePlotter Class
    Copyright (C) Damien Farrell
 
    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or (at your option) any later version.
 
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
 
    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

from Tkinter import *
import tkMessageBox
import tkFont
import math
from types import *

class TableCanvas(Canvas):
    """A tkinter class for providing table functionality"""

    def __init__(self, parent, model, newdict=None, width=None, height=None, **kwargs):
        Canvas.__init__(self, parent, bg='white',
                         width=width, height=height,
                         relief=GROOVE,
                         scrollregion=(0,0,300,200))
        self.parentframe = parent
        self.width=width
        self.height=height

        self.set_defaults()
        self.currentpage = None
        self.navFrame = None
        self.currentrow = 0
        self.currentcol = 0
        #for multiple selections
        self.startrow = self.endrow = None
        self.startcol = self.endcol = None
        self.allrows = False   #for selected all rows without setting multiplerowlist
        self.multiplerowlist=[]
        self.multiplecollist=[]
        self.col_positions=[]       #record current column grid positions

        #set any options passed in kwargs to overwrite defaults/prefs
        for key in kwargs:
            self.__dict__[key] = kwargs[key]

        self.model = model
        if newdict != None:
            self.createfromDict(newdict)

        self.rows=self.model.get_row_count()
        self.cols=self.model.get_column_count()
        self.tablewidth=(self.cellwidth)*self.cols
        self.tablecolheader = ColumnHeader(self.parentframe, self, self.header_cfg)
        self.tablerowheader = RowHeader(self.parentframe, self)
        self.do_bindings()

    def set_defaults(self):
        self.cellwidth=120
        self.maxcellwidth=400
        self.rowheight=20
        self.horizlines=1
        self.vertlines=1
        self.alternaterows=0
        self.autoresizecols = 0
        self.paging = 0
        self.rowsperpage = 100
        self.inset=2
        self.x_start=0
        self.y_start=1
        self.linewidth=1.0
        self.fontsize = 11
        self.thefont = ('Arial', self.fontsize)
        self.cellbackgr = '#F7F7FA'
        self.entrybackgr = 'white'
        self.grid_color = '#ABB1AD'
        self.selectedcolor = 'yellow'
        self.rowselectedcolor = '#CCCCFF'
        self.multipleselectioncolor = '#ECD672'
        self.header_cfg = {
             "height"   : 20
            ,"font"     : ("Arial", 11, "normal")
            ,"bg_clr"   : "gray25"
            ,"font_clr" : "white"
            }

    def do_bindings(self):
        """Bind keys and mouse clicks, this can be overriden"""
        self.bind("<Button-1>",self.handle_left_click)
        self.bind("<Shift-Button-1>", self.handle_left_shift_click)
        self.bind("<ButtonRelease-1>", self.handle_left_release)
        self.bind('<B1-Motion>', self.handle_mouse_drag)
        self.bind('<Motion>', self.handle_motion)

        self.parentframe.master.bind_all("<Up>",     self.handle_arrow_keys)
        self.parentframe.master.bind_all("<Down>",   self.handle_arrow_keys)
        self.parentframe.master.bind_all("<Right>",  self.handle_arrow_keys)
        self.parentframe.master.bind_all("<Left>",   self.handle_arrow_keys)
        self.parentframe.master.bind_all("<Prior>",  self.handle_arrow_keys)
        self.parentframe.master.bind_all("<Next>",   self.handle_arrow_keys)
        self.parentframe.master.bind_all("<Home>",   self.handle_arrow_keys)
        self.parentframe.master.bind_all("<End>",    self.handle_arrow_keys)

        self.parentframe.master.bind_all("<MouseWheel>",
            lambda event=None: self.mouse_wheel(-math.trunc(math.copysign(1, event.delta))))
        self.parentframe.master.bind_all('<Button-4>',
            lambda event=None: self.mouse_wheel(-1))
        self.parentframe.master.bind_all('<Button-5>',
            lambda event=None: self.mouse_wheel(1))

    def getModel(self):
        """Get the current table model"""
        return self.model

    def setModel(self,model):
        self.model = model

    def createTableFrame(self, callback=None):
        """Adds column header and scrollbars and combines them with
           the current table adding all to the master frame provided in constructor.
           Table is then redrawn."""

        #Add the table and header to the frame
        self.Yscrollbar = AutoScrollbar(self.parentframe,orient=VERTICAL,command=self.set_yviews)
        self.Yscrollbar.grid(row=1,column=2,rowspan=1,sticky='news',pady=0,ipady=0)
        self.Xscrollbar = AutoScrollbar(self.parentframe,orient=HORIZONTAL,command=self.set_xviews)
        self.Xscrollbar.grid(row=2,column=1,columnspan=1,sticky='news')
        self['xscrollcommand'] = self.Xscrollbar.set
        self['yscrollcommand'] = self.Yscrollbar.set
        self.tablecolheader['xscrollcommand']=self.Xscrollbar.set
        self.tablerowheader['yscrollcommand']=self.Yscrollbar.set
        self.parentframe.rowconfigure(1,weight=1)
        self.parentframe.columnconfigure(1,weight=1)

        self.tablecolheader.grid(row=0,column=1,rowspan=1,sticky='news',pady=0,ipady=0)
        self.tablerowheader.grid(row=1,column=0,rowspan=1,sticky='news',pady=0,ipady=0)
        self.grid(row=1,column=1,rowspan=1,sticky='news',pady=0,ipady=0)
        # if self.model.get_row_count()<500:
        #     self.adjust_colWidths()
        self.redrawTable(callback=callback)
        self.parentframe.bind("<Configure>", self.resizeTable)
        self.tablecolheader.xview("moveto", 0)
        self.xview("moveto", 0)

    def redrawTable(self, event=None, callback=None):
        """Draw the table from scratch based on it's model data"""
        import time
        self.rows=self.model.get_row_count()
        self.cols=self.model.get_column_count()
        self.tablewidth=(self.cellwidth)*self.cols
        self.configure(bg=self.cellbackgr)
        #determine col positions for first time
        self.set_colPositions()

        #check if large no. of records and switch to paging view
        if self.paging == 0 and self.rows >= 500:
            self.paging = 1
        #if using paging, we only want to display the current page..
        if self.paging == 1:
            self.numpages = int(math.ceil(float(self.rows)/self.rowsperpage))
          
            if self.currentpage == None:
                self.currentpage = 0
            self.drawNavFrame()
        else:
            try:
                self.navFrame.destroy()
                self.navFrame.forget()
            except:
                pass
        #determine current range of rows to draw if paging
        if self.paging == 1 and self.rows>self.rowsperpage:
            lower=self.currentpage*self.rowsperpage
            upper=lower+self.rowsperpage
            if upper>=self.rows:
                upper=self.rows
            self.rowrange=range(lower,upper)
            self.configure(scrollregion=(0,0, self.tablewidth+self.x_start, self.rowheight*len(self.rowrange)+10))
        else:
            self.rowrange = range(0,self.rows)
            self.configure(scrollregion=(0,0, self.tablewidth+self.x_start, self.rowheight*self.rows+10))
            
        self.draw_grid()
        self.update_idletasks()
        self.tablecolheader.redraw()
        self.tablerowheader.redraw(paging=self.paging)
        align=None
        self.delete('fillrect')
     
        if self.cols == 0 or self.rows == 0:
            self.delete('entry')
            self.delete('rowrect')
            self.delete('currentrect')
            return

        #now draw model data in cells
        rowpos=0
        if self.model!=None:
            for row in self.rowrange:
                if callback != None:
                    callback()                   
                for col in range(self.cols):
                    align=None
                    bgcolor = None
                    fgcolor = None
                    text = self.model.get_value(col, row)
                    self.draw_Text(rowpos, col, text, fgcolor, align)
                    if bgcolor != None:
                        self.draw_rect(rowpos,col, color=bgcolor)
                rowpos+=1
        self.setSelectedRow(0)
        self.drawSelectedRow()
        self.draw_selected_rect(self.currentrow, self.currentcol)
        if len(self.multiplerowlist)>1:
            self.drawMultipleRows(self.multiplerowlist)
        
    def resizeTable(self, event):
        """Respond to a resize event - redraws table"""
        if self.autoresizecols == 1 and event != None:
            self.cellwidth = (event.width - self.x_start - 24) / self.cols
            self.redrawTable()

    def set_colPositions(self):
        """Determine current column grid positions"""
        self.col_positions=[]
        x_pos=self.x_start
        self.col_positions.append(x_pos)
        for col in range(self.cols):
            x_pos=x_pos+self.model.get_column(col).width
            self.col_positions.append(x_pos)
        self.tablewidth = self.col_positions[len(self.col_positions)-1]

    def sortTable(self, sortcol):
        self.model.resort(sortcol)
        self.redrawTable()

    def set_xviews(self,*args):
        """Set the xview of table and col header"""
        apply(self.xview,args)
        apply(self.tablecolheader.xview,args)
        return

    def set_yviews(self,*args):
        """Set the xview of table and row header"""
        apply(self.yview,args)
        apply(self.tablerowheader.yview,args)
        return

    def drawNavFrame(self):
        """Draw the frame for selecting pages when paging is on"""
        import Table_images
        self.navFrame = Frame(self.parentframe)
        self.navFrame.grid(row=4,column=0,columnspan=2,sticky='news',padx=1,pady=1,ipady=1)
        pagingbuttons = { 'start' : self.first_Page, 'prev' : self.prev_Page,
                          'next' : self.next_Page, 'end' : self.last_Page}
        images = { 'start' : Table_images.start(), 'prev' : Table_images.prev(),
                   'next' : Table_images.next(), 'end' : Table_images.end()}
        skeys=['start', 'prev', 'next', 'end']
        for i in skeys:
            b = Button(self.navFrame, text=i, command=pagingbuttons[i],
                        relief=GROOVE,
                        image=images[i])
            b.image = images[i]
            b.pack(side=LEFT, ipadx=1, ipady=1)
        Label(self.navFrame,text='Page '+str(self.currentpage+1)+' of '+ str(self.numpages),fg='white',
                  bg='#3366CC',relief=SUNKEN).pack(side=LEFT,ipadx=2,ipady=2,padx=4)
        #Label(self.navFrame,text='Goto Record:').pack(side=LEFT,padx=3)
        #self.gotorecordvar = StringVar()
        #Entry(self.navFrame,textvariable=self.gotorecordvar,
        #          width=8,bg='white').pack(side=LEFT,ipady=3,padx=2)
        Label(self.navFrame,text=str(self.rows)+' records').pack(side=LEFT,padx=3)
        Button(self.navFrame,text='Normal View',command=self.paging_Off,
                   bg='#99CCCC',relief=GROOVE).pack(side=LEFT,padx=3)
        return

    def paging_Off(self):
        self.rows=self.model.get_row_count()
        if self.rows >= 1000:
            tkMessageBox.showwarning("Warning",
                                     'This table has over 1000 rows.'
                                     'You should stay in page view.'
                                     'You can increase the rows per page in settings.',
                                     parent=self.parentframe)
        else:
            self.paging = 0
            self.redrawTable()
        return

    def first_Page(self):
        """Go to next page"""
        self.currentpage = 0
        self.redrawTable()
        return

    def last_Page(self):
        """Go to next page"""
        self.currentpage = self.numpages-1
        self.redrawTable()
        return

    def prev_Page(self):
        """Go to next page"""
        if self.currentpage > 0:
            self.currentpage -= 1
            self.redrawTable()
        return

    def next_Page(self):
        """Go to next page"""
        if self.currentpage < self.numpages-1:
            self.currentpage += 1
            self.redrawTable()
        return

    def get_AbsoluteRow(self, row):
        """This function always returns the corrected absolute row number,
           whether if paging is on or not"""
        if self.paging == 0:
            return row
        absrow = row+self.currentpage*self.rowsperpage
        return absrow

    def check_PageView(self, row):
        """Check if row clickable for page view"""
        if self.paging == 1:
            absrow = self.get_AbsoluteRow(row)
            if absrow >= self.rows or row > self.rowsperpage:
                return 1
        return 0
      
    def resize_Column(self, col, width):
        """Resize a column by dragging"""
        #recalculate all col positions..
        self.model.get_column(col).width = width

        self.set_colPositions()
        self.redrawTable()
        self.drawSelectedCol(self.currentcol)

    def get_row_clicked(self, event):
        """get row where event on canvas occurs"""
        h=self.rowheight
        #get coord on canvas, not window, need this if scrolling
        y = int(self.canvasy(event.y))
        y_start=self.y_start
        rowc = (int(y)-y_start)/h
        return rowc

    def get_col_clicked(self,event):
        """get col where event on canvas occurs"""
        w=self.cellwidth
        x = int(self.canvasx(event.x))
        x_start=self.x_start
        for ind, colpos in enumerate(self.col_positions):
            try:
                nextpos=self.col_positions[ind+1]
            except:
                nextpos=self.tablewidth
            if x > colpos and x <= nextpos:
                return ind
            else:
                pass

    def setSelectedRow(self, row):
        """Set currently selected row and reset multiple row list"""
        self.currentrow = row
        self.multiplerowlist = []
        self.multiplerowlist.append(row)

    def setSelectedCol(self, col):
        """Set currently selected column"""
        self.currentcol = col
        self.multiplecollist = []
        self.multiplecollist.append(col)

    def getSelectedRow(self):
        """Get currently selected row"""
        return self.currentrow

    def getSelectedColumn(self):
        """Get currently selected column"""
        return self.currentcol

    def getCellCoords(self, row, col):
        """Get x-y coordinates to drawing a cell in a given row/col"""        
        w=self.model.get_column(col).width
        h=self.rowheight
        x_start=self.x_start
        y_start=self.y_start

        #get nearest rect co-ords for that row/col
        #x1=x_start+w*col
        x1=self.col_positions[col]
        y1=y_start+h*row
        x2=x1+w
        y2=y1+h
        return x1,y1,x2,y2

    def getCanvasPos(self, row, col):
        """Get the cell x-y coords as a fraction of canvas size"""
        if self.rows==0:
            return None, None
        x1,y1,x2,y2 = self.getCellCoords(row,col)
        cx=float(x1)/self.tablewidth
        cy=float(y1)/(self.rows*self.rowheight)
        return cx, cy

    def isInsideTable(self,x,y):
        """Returns true if x-y coord is inside table bounds"""
        if self.x_start < x < self.tablewidth and self.y_start < y < self.rows*self.rowheight:
            return 1
        else:
            return 0
        return answer

    def setRowHeight(self, h):
        """Set the row height"""
        self.rowheight = h
        return

    def clearSelected(self):
        self.delete('rect')
        self.delete('entry')
        self.delete('tooltip')
        self.delete('colrect')
        self.delete('multicellrect')

    def gotoprevRow(self):
        """Programmatically set previous row - eg. for button events"""
        self.clearSelected()
        current = self.getSelectedRow()
        self.setSelectedRow(current-1)
        self.startrow = current-1
        self.endrow = current-1
        #reset multiple selection list
        self.multiplerowlist=[]
        self.multiplerowlist.append(self.currentrow)
        self.draw_selected_rect(self.currentrow, self.currentcol)
        self.drawSelectedRow()

    def gotonextRow(self):
        """Programmatically set next row - eg. for button events"""
        self.clearSelected()
        current = self.getSelectedRow()
        self.setSelectedRow(current+1)
        self.startrow = current+1
        self.endrow = current+1
        #reset multiple selection list
        self.multiplerowlist=[]
        self.multiplerowlist.append(self.currentrow)
        self.draw_selected_rect(self.currentrow, self.currentcol)
        self.drawSelectedRow()

    def handle_left_click(self, event):
        """Respond to a single press"""
        #which row and column is the click inside?
        self.clearSelected()
        self.allrows = False
        rowclicked = self.get_row_clicked(event)
        colclicked = self.get_col_clicked(event)
        if self.check_PageView(rowclicked) == 1:
            return

        self.startrow = rowclicked
        self.endrow = rowclicked
        self.startcol = colclicked
        self.endcol = colclicked
        #reset multiple selection list
        self.multiplerowlist=[]
        self.multiplerowlist.append(rowclicked)
        if 0 <= rowclicked < self.rows and 0 <= colclicked < self.cols:
            self.setSelectedRow(rowclicked)
            self.setSelectedCol(colclicked)
            self.draw_selected_rect(self.currentrow, self.currentcol)
            self.drawSelectedRow()
            self.tablerowheader.drawSelectedRows(rowclicked)

    def handle_left_release(self,event):
        self.endrow = self.get_row_clicked(event)

    def handle_left_shift_click(self, event):
        """Handle shift click, for selecting multiple rows"""
        #Has same effect as mouse drag, so just use same method
        self.handle_mouse_drag(event)

    def handle_mouse_drag(self, event):
        """Handle mouse moved with button held down, multiple selections"""
        rowover = self.get_row_clicked(event)
        colover = self.get_col_clicked(event)
        if colover == None or rowover == None:
            return
        if self.check_PageView(rowover) == 1:
            return
        if rowover >= self.rows or self.startrow > self.rows:
            return
        else:
            self.endrow = rowover
        #do columns
        if colover > self.cols or self.startcol > self.cols:
            return
        else:
            self.endcol = colover
            if self.endcol < self.startcol:
                self.multiplecollist=range(self.endcol, self.startcol+1)
            else:
                self.multiplecollist=range(self.startcol, self.endcol+1)
        #draw the selected rows
        if self.endrow != self.startrow:
            if self.endrow < self.startrow:
                self.multiplerowlist=range(self.endrow, self.startrow+1)
            else:
                self.multiplerowlist=range(self.startrow, self.endrow+1)
            self.drawMultipleRows(self.multiplerowlist)
            self.tablerowheader.drawSelectedRows(self.multiplerowlist)
            #draw selected cells outline using row and col lists
            self.drawMultipleCells()
        else:
            self.multiplerowlist = []
            self.multiplerowlist.append(self.currentrow)
            if len(self.multiplecollist) >= 1:
                self.drawMultipleCells()
            self.delete('multiplesel')
        return

    def scroll_table_by_y(self, cnt):
        row_cnt = len(self.rowrange)
        h       = float(self.rowheight)
        self.currentrow = min(max(self.currentrow + cnt, 0), row_cnt-1)

        x1, y1, x2, y2 = self.getCellCoords(self.currentrow, 0)
        screen_y1 = self.canvasy(0)
        screen_y2 = screen_y1 + self.winfo_height()
        if y2 > screen_y2:
            screen_pos = screen_y1 + (y2 - screen_y2) + 5
        elif y1 < screen_y1:
            screen_pos = float(y1)
        else:
            return
        canvas_pos = float(screen_pos)/(row_cnt*h+10.0)
        self.yview('moveto', canvas_pos)
        self.tablerowheader.yview('moveto', canvas_pos)

    def scroll_table_by_x(self, cnt):
        self.currentcol = min(max(self.currentcol + cnt, 0), self.cols-1)

        x1, y1, x2, y2 = self.getCellCoords(0, self.currentcol)
        screen_x1 = self.canvasx(0)
        screen_x2 = screen_x1 + self.winfo_width()
        if x2 > screen_x2:
            screen_pos = screen_x1 + (x2 - screen_x2) + 5
        elif x1 < screen_x1:
            screen_pos = float(x1)
        else:
            return
        canvas_pos = float(screen_pos)/(self.tablewidth+self.x_start)
        self.xview('moveto', canvas_pos)
        self.tablecolheader.xview("moveto", canvas_pos)

    def handle_arrow_keys(self, event):
        """Handle arrow keys press"""

        if self.rows==0:
            return

        if event.keysym == 'Up':
            self.scroll_table_by_y(-1)
        elif event.keysym == 'Down':
            self.scroll_table_by_y(1)
        elif event.keysym == 'Prior':
            self.scroll_table_by_y(-10)
        elif event.keysym == 'Next':
            self.scroll_table_by_y(10)
        elif event.keysym == 'Home':
            self.scroll_table_by_y(-len(self.rowrange))
        elif event.keysym == 'End':
            self.scroll_table_by_y(len(self.rowrange))            
        elif event.keysym == 'Right':
            self.scroll_table_by_x(1)
        elif event.keysym == 'Left':
            self.scroll_table_by_x(-1)

        self.draw_selected_rect(self.currentrow, self.currentcol)

    def mouse_wheel(self, delta):
        """Handle mouse wheel scroll"""
        self.scroll_table_by_y(delta)
        self.draw_selected_rect(self.currentrow, self.currentcol)

    def handle_motion(self, event):
        """Handle mouse motion on table"""
        self.delete('tooltip')
        row = self.get_row_clicked(event)
        col = self.get_col_clicked(event)
        if self.check_PageView(row) == 1:
            return
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.draw_tooltip(row, col)

    #--- Drawing stuff ---

    def draw_grid(self):
        """Draw the table grid lines"""
        self.delete('gridline','text')
        rows=len(self.rowrange)
        cols=self.cols
        w=self.cellwidth
        h=self.rowheight
        x_start=self.x_start
        y_start=self.y_start

        self.data={}
        x_pos=x_start

        if self.vertlines==1:
            for col in range(cols+1):
                x=self.col_positions[col]
                self.create_line(x,y_start,x,y_start+rows*h, tag='gridline',
                                     fill=self.grid_color, width=self.linewidth)

        if self.horizlines==1:
            for row in range(rows+1):
                y_pos=y_start+row*h
                self.create_line(x_start,y_pos,self.tablewidth,y_pos, tag='gridline',
                                    fill=self.grid_color, width=self.linewidth)

    def draw_rowheader(self):
        """User has clicked to select a cell"""
        self.delete('rowheader')
        x_start=self.x_start
        y_start=self.y_start
        h=self.rowheight
        rowpos=0
        for row in self.rowrange:
            x1,y1,x2,y2 = self.getCellCoords(rowpos,0)
            self.create_rectangle(0,y1,x_start-2,y2,
                                      fill='gray75',
                                      outline='white',
                                      width=1,
                                      tag='rowheader')
            self.create_text(x_start/2,y1+h/2,
                                      text=row+1,
                                      fill='black',
                                      font=self.thefont,
                                      tag='rowheader')
            rowpos+=1

    def draw_selected_rect(self, row, col, color=None):
        """User has clicked to select a cell"""
        if col >= self.cols:
            return
        self.delete('currentrect')
        bg=self.selectedcolor
        if color == None:
            color = 'gray25'
        w=3
        x1,y1,x2,y2 = self.getCellCoords(row,col)
        rect = self.create_rectangle(x1+w/2,y1+w/2,x2-w/2,y2-w/2,
                                  fill=bg,
                                  outline=color,
                                  width=w,
                                  stipple='gray50',
                                  tag='currentrect')
        #self.lower('currentrect')
        #raise text above all
        self.lift('celltext'+str(col)+'_'+str(row))
        return

    def draw_rect(self, row, col, color=None, tag=None, delete=1):
        """Cell is colored"""
        if delete==1:
            self.delete('cellbg'+str(row)+str(col))
        if color==None or color==self.cellbackgr:
            return
        else:
            bg=color
        if tag==None:
            recttag='fillrect'
        else:
            recttag=tag
        w=1
        x1,y1,x2,y2 = self.getCellCoords(row,col)
        rect = self.create_rectangle(x1+w/2,y1+w/2,x2-w/2,y2-w/2,
                                  fill=bg,
                                  outline=bg,
                                  width=w,
                                  tag=(recttag,'cellbg'+str(row)+str(col)))
        self.lower(recttag)

    def draw_Text(self, row, col, celltxt, fgcolor=None, align=None):
        """Draw the text inside a cell area"""
        self.delete('celltext'+str(col)+'_'+str(row))
        h=self.rowheight
        x1,y1,x2,y2 = self.getCellCoords(row,col)
        w=x2-x1
        # If celltxt is a number then we make it a string
        import types
        if type(celltxt) is types.FloatType or type(celltxt) is types.IntType:
            celltxt=str(celltxt)
        if w<=15:
            return

        fontsize = self.fontsize
        scale = fontsize*1.2
        total = len(celltxt)
        
        if len(celltxt) > w/scale:           
            celltxt=celltxt[0:int(w/fontsize*1.2)-3]
        if len(celltxt) < total:
            celltxt=celltxt+'..'            
        if w < 25:
            celltxt = ''
        if fgcolor == None or fgcolor == "None":
            fgcolor = 'black'
        if align == None:
            align = 'center'
        elif align == 'w':
            x1 = x1-w/2+1

        rect = self.create_text(x1+w/2,y1+h/2,
                                  text=celltxt,
                                  fill=fgcolor,
                                  font=self.thefont,
                                  anchor=align,
                                  tag=('text','celltext'+str(col)+'_'+str(row)))

    def drawSelectedRow(self):
        """Draw the highlight rect for the currently selected row"""
        self.delete('rowrect')
        row=self.currentrow
        x1,y1,x2,y2 = self.getCellCoords(row,0)
        x2=self.tablewidth
        rect = self.create_rectangle(x1,y1,x2,y2,
                                  fill=self.rowselectedcolor,
                                  outline=self.rowselectedcolor,
                                  tag='rowrect')
        self.lower('rowrect')
        self.lower('fillrect')

    def drawSelectedCol(self, col=None, delete=1):
        """Draw an outline rect fot the current column selection"""
        if delete == 1:
            self.delete('colrect')
        if col == None:
            col=self.currentcol
        w=2
        x1,y1,x2,y2 = self.getCellCoords(0,col)
        y2 = self.rows * self.rowheight
        rect = self.create_rectangle(x1+w/2,y1+w/2,x2,y2+w/2,
                                     outline='blue',width=w,
                                     tag='colrect')

    def drawMultipleRows(self, rowlist):
        """Draw more than one row selection"""
        self.delete('multiplesel')
        for r in rowlist:
            if r > self.rows-1:
                continue
            x1,y1,x2,y2 = self.getCellCoords(r,0)
            x2=self.tablewidth
            rect = self.create_rectangle(x1,y1,x2,y2,
                                      fill=self.multipleselectioncolor,
                                      outline=self.rowselectedcolor,
                                      tag=('multiplesel','rowrect'))
        self.lower('multiplesel')
        self.lower('fillrect')

    def drawMultipleCells(self):
        """Draw an outline box for multiple cell selection"""
        self.delete('multicellrect')
        rows = self.multiplerowlist
        cols = self.multiplecollist
        w=2
        x1,y1,a,b = self.getCellCoords(rows[0],cols[0])
        c,d,x2,y2 = self.getCellCoords(rows[len(rows)-1],cols[len(cols)-1])
        rect = self.create_rectangle(x1+w/2,y1+w/2,x2,y2,
                             outline='blue',width=w,activefill='red',activestipple='gray25',
                             tag='multicellrect')

    def draw_tooltip(self, row, col):
        """Draw a tooltip showing contents of cell"""

        absrow = self.get_AbsoluteRow(row)
        x1,y1,x2,y2 = self.getCellCoords(row,col)
        w=x2-x1
        text = self.model.get_value(col,absrow)
        if isinstance(text, dict):
            if text.has_key('link'):
                text = text['link']

        # If text is a number we make it a string
        import types
        if type(text) is types.FloatType or type is types.IntType:
            text=str(text)
        if text == NoneType or text == '' or len(str(text))<=3:
            return
        import tkFont
        sfont = tkFont.Font (family='Arial', size=12,weight='bold')
        obj=self.create_text(x1+w/1.5,y2,text=text,
                                anchor='w',
                                font=sfont,tag='tooltip')

        box = self.bbox(obj)
        x1=box[0]-1
        y1=box[1]-1
        x2=box[2]+1
        y2=box[3]+1

        rect = self.create_rectangle(x1+1,y1+1,x2+1,y2+1,tag='tooltip',fill='black')
        rect2 = self.create_rectangle(x1,y1,x2,y2,tag='tooltip',fill='lightyellow')
        self.lift(obj)

class ColumnHeader(Canvas):
    """Class that takes it's size and rendering from a parent table
        and column names from the table model."""

    def __init__(self, parent, table, cfg):
        Canvas.__init__(self, parent, bg=cfg["bg_clr"], width=table.width, height=cfg["height"])
        self.table    = table
        self.height   = cfg["height"]
        fnt           = cfg["font"]
        self.thefont  = tkFont.Font(family=fnt[0], size=fnt[1], weight=fnt[2])
        self.model    = self.table.getModel()
        self.font_clr = cfg["font_clr"]
        self.bind("<Button-1>",        self.handle_left_click)
        self.bind("<ButtonRelease-1>", self.handle_left_release)
        self.bind("<B1-Motion>",       self.handle_mouse_drag)
        self.bind("<Motion>",          self.handle_mouse_move)

    def redraw(self):
        cols=self.model.get_column_count()
        self.tablewidth=self.table.tablewidth
        self.configure(scrollregion=(0,0, self.table.tablewidth+self.table.x_start, self.height))
        self.delete('gridline','text')
        self.atdivider = None

        if cols == 0:
            return

        if self.model.get_sort_is_reverse():
            order_ch = ' ▼'
        else:
            order_ch = ' ▲'
        h = self.height

        for col in range(cols):
            w=self.model.get_column(col).width
            x=self.table.col_positions[col]

            if col == self.model.get_sort_index():
                dop_sm = order_ch
            else:
                dop_sm = ''

            collabel = self.get_clipped_colname(self.model.get_column(col).caption, dop_sm, self.thefont, w)

            line = self.create_line(x, 0, x, h, tag=('gridline', 'vertline'),
                                 fill='white', width=2)

            self.create_text(x+w/2,h/2,
                                text=collabel,
                                fill=self.font_clr,
                                font=self.thefont,
                                tag='text')

        x=self.table.col_positions[col+1]
        self.create_line(x,0, x,h, tag='gridline',
                        fill='white', width=2)

    def handle_left_click(self,event):
        """Does cell selection when mouse is clicked on canvas"""
        self.table.delete('entry')
        self.table.delete('multicellrect')
        #set all rows selected
        self.table.allrows = True
        
        if self.atdivider == 1:
            x=int(self.canvasx(event.x))          
            self.table.setSelectedCol(self.get_col_for_resize(x))
        else:
            colclicked = self.table.get_col_clicked(event)
            self.table.setSelectedCol(colclicked)
            self.table.sortTable(colclicked)

    def handle_left_release(self,event):
        """When mouse released implement col move"""
        self.delete('resizesymbol')
        if self.atdivider == 1:
            x=int(self.canvasx(event.x))
            col = self.table.currentcol
            x1,y1,x2,y2 = self.table.getCellCoords(0,col)
            newwidth=x - x1
            if newwidth < 5:
                newwidth=5
            self.table.resize_Column(col, newwidth)
            self.table.delete('resizeline')
            self.delete('resizeline')
            self.atdivider = 0

    def handle_mouse_drag(self, event):
        """Handle column drag, will be either to resize cols"""
        x=int(self.canvasx(event.x))
        if self.atdivider == 1:
            self.table.delete('resizeline')
            self.delete('resizeline')
            self.table.create_line(x, 0, x, self.table.rowheight*self.table.rows,
                                width=2, fill='gray', tag='resizeline')
            self.create_line(x, 0, x, self.height,
                                width=2, fill='gray', tag='resizeline')

    def handle_mouse_move(self, event):
        """Handle mouse moved in header, if near divider draw resize symbol"""
        self.delete('resizesymbol')

        x = int(self.canvasx(event.x))
        if self.table.x_start < x < (self.tablewidth+self.table.cellwidth):
            col = self.get_col_for_resize(x)
            if col == None:
                self.atdivider = 0
            else:
                self.atdivider = 1
                self.draw_resize_symbol(col)

    def get_clipped_colname(self, text, dop_sm, font, max_width):
        new_text = text+dop_sm
        if font.measure(new_text) <= max_width:
            return new_text
        for i in range(len(text)-1, 0, -1):
            new_text = text[:i] + '.' + dop_sm
            if font.measure(new_text) <= max_width:
                return new_text
        new_text = dop_sm
        if font.measure(new_text) <= max_width:
            return new_text
        else:
            return ''

    def get_col_for_resize(self, pos_x):
        dt = 10
        for i, pos in enumerate(self.table.col_positions):
            if i > 0 and abs(pos_x-pos) <= dt:
                return i-1
        return None

    def draw_resize_symbol(self, col):
        """Draw a symbol to show that col can be resized when mouse here"""
        self.delete('resizesymbol')
        
        h=self.height
        x1,y1,x2,y2 = self.table.getCellCoords(0,col)

        self.create_polygon(x2-3,h/4, x2-10,h/2, x2-3,h*3/4, tag='resizesymbol',
            fill='white', outline='gray', width=1)
        self.create_polygon(x2+2,h/4, x2+10,h/2, x2+2,h*3/4, tag='resizesymbol',
            fill='white', outline='gray', width=1)

class RowHeader(Canvas):
    """Class that displays the row headings on the table
       takes it's size and rendering from the parent table
       This also handles row/record selection as opposed to cell
       selection"""
    def __init__(self, parent=None, table=None):
        Canvas.__init__(self, parent, bg='gray75', width=40, height=None )

        if table != None:
            self.table = table
            self.width = 40
            self.x_start = 40
            self.inset = 1
            #self.config(width=self.width)
            self.config(height = self.table.height)
            self.startrow = self.endrow = None
            self.model = self.table.getModel()
            self.bind('<Button-1>',self.handle_left_click)
            self.bind("<ButtonRelease-1>", self.handle_left_release)
            self.bind("<Control-Button-1>", self.handle_left_ctrl_click)
            self.bind('<B1-Motion>', self.handle_mouse_drag)

    def redraw(self, paging = 0):
        """Redraw row header"""
        if paging == 1:
            self.height = self.table.rowheight * self.table.rowsperpage+10
        else:
            self.height = self.table.rowheight * self.table.rows+10
     
        self.configure(scrollregion=(0,0, self.width, self.height))
        self.delete('rowheader','text')
        self.delete('rect')

        w=1
        x_start=self.x_start
        y_start=self.table.y_start
        h = self.table.rowheight
        rowpos=0
        for row in self.table.rowrange:
            x1,y1,x2,y2 = self.table.getCellCoords(rowpos,0)
            self.create_rectangle(0,y1,x_start-w,y2,
                                      fill='gray75',
                                      outline='white',
                                      width=w,
                                      tag='rowheader')
            self.create_text(x_start/2,y1+h/2,
                                      text=row+1,
                                      fill='black',
                                      font=self.table.thefont,
                                      tag='text')
            rowpos+=1
        return

    def clearSelected(self):
        self.delete('rect')
        return

    def handle_left_click(self, event):
        rowclicked = self.table.get_row_clicked(event)
        self.startrow = rowclicked
        if 0 <= rowclicked < self.table.rows:
            self.delete('rect')
            self.table.delete('entry')
            self.table.delete('multicellrect')
            #set row selected
            self.table.setSelectedRow(rowclicked)
            self.table.drawSelectedRow()
            self.drawSelectedRows(self.table.currentrow)
        return

    def handle_left_release(self,event):

        return

    def handle_left_ctrl_click(self, event):
        """Handle ctrl clicks - for multiple row selections"""
        rowclicked = self.table.get_row_clicked(event)
        multirowlist = self.table.multiplerowlist
        if 0 <= rowclicked < self.table.rows:
            if rowclicked not in multirowlist:
                multirowlist.append(rowclicked)
            else:
                multirowlist.remove(rowclicked)
            self.table.drawMultipleRows(multirowlist)
            self.drawSelectedRows(multirowlist)
        return

    def handle_mouse_drag(self, event):
        """Handle mouse drag for mult row selection"""
        rowover = self.table.get_row_clicked(event)
        colover = self.table.get_col_clicked(event)
        if colover == None or rowover == None:
            return
        if self.table.check_PageView(rowover) == 1:
            return

    def handle_mouse_drag(self, event):
        """Handle mouse moved with button held down, multiple selections"""
        rowover = self.table.get_row_clicked(event)
        colover = self.table.get_col_clicked(event)
        if rowover == None or self.table.check_PageView(rowover) == 1:
            return
        if rowover >= self.table.rows or self.startrow > self.table.rows:
            return
        else:
            self.endrow = rowover
        #draw the selected rows
        if self.endrow != self.startrow:
            if self.endrow < self.startrow:
                rowlist=range(self.endrow, self.startrow+1)
            else:
                rowlist=range(self.startrow, self.endrow+1)
            self.drawSelectedRows(rowlist)
            self.table.multiplerowlist = rowlist
            self.table.drawMultipleRows(rowlist)
        else:
            self.table.multiplerowlist = []
            self.table.multiplerowlist.append(rowover)
            self.drawSelectedRows(rowover)
            self.table.drawMultipleRows(self.table.multiplerowlist)
        return

    def drawSelectedRows(self, rows=None):
        """Draw selected rows, accepts a list or integer"""
        self.delete('rect')
        if type(rows) is not ListType:
            rowlist=[]
            rowlist.append(rows)
        else:
           rowlist = rows
        for r in rowlist:
            self.draw_rect(r, delete=0)
        return

    def draw_rect(self, row=None, tag=None, color=None, outline=None, delete=1):
        """Draw a rect representing row selection"""
        if tag==None:
            tag='rect'
        if color==None:
            color='#0099CC'
        if outline==None:
            outline='gray25'
        if delete == 1:
            self.delete(tag)
        w=0
        i = self.inset
        x1,y1,x2,y2 = self.table.getCellCoords(row, 0)
        rect = self.create_rectangle(0+i,y1+i,self.x_start-i,y2,
                                      fill=color,
                                      outline=outline,
                                      width=w,
                                      tag=tag)
        self.lift('text')
        return

class AutoScrollbar(Scrollbar):
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        Scrollbar.set(self, lo, hi)
    def pack(self, **kw):
        raise TclError, "cannot use pack with this widget"
    def place(self, **kw):
        raise TclError, "cannot use place with this widget"