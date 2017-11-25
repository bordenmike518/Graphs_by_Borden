# ============================================================================
# Author      :: Michael Borden
# Created     :: Nov 19, 2017
# Last Update :: Nov 25, 2017
# 
# Porpose     :: This is an attempt to visualize Graphs with interactive
#                Vertices and dynamic edges. 
#
# Directions  :: In the textbox you can enter a list of edges per vertex 
#                seperated by any delimiter.
#
# Example     :: 2 2 2 or 3 3 3 3 or 4 4 3 2 2 2 2 1 or 1 1
# ============================================================================

import wx
from random import sample
from numpy import zeros
from copy import deepcopy
from math import sin, cos, radians

# VERTICES --------------------------------------------------------------------
class Vertex:
    def __init__(self, parent, edges, label, pos):
        self.edges = edges
        self.label = label
        self.adjacency_list = []
        self.pos = pos
        self.button = wx.Button(parent=parent, 
                                id=-1, 
                                label=self.label, 
                                pos=self.pos, 
                                size=(50, 50))
        
    def getPosition(self):
        px, py = self.button.GetPositionTuple()
        self.pos = [px, py]
        return px, py

    def destroyButton(self):
        self.button.Destroy()
# -----------------------------------------------------------------------------

# GUI -------------------------------------------------------------------------
class widgetFrame(wx.Frame):
    def __init__(self, parent, id, title):
        self.panel_size = (1000, 1500)
        self.k = 300.0   # Temp
        self.vertex_array = []
        self.vertices_list = []
        self.down = False
        self.draw = False
        self.error_title_label = "ERROR - ERROR - ERROR - ERROR - ERROR"
        self.error_body_label = '''
 ----------------------------------------------------
 
 The sumation of edges are odd or in violation of one
 of the following observations:
 
 I  : The sequence (0,0,..,0) of length n is graphic
      since it represents the null graph Nn.
    
 II : Is in a graphic sequence S = (d[0]>=...>=d[n])
      d[0]<= n-1.
    
 III: d[d[0]+1] > 0; a graphic sequence of a non-null
      graph S = (d[0]>=...>=d[n]).
     
 ----------------------------------------------------
 
 Try the following :: 1 1
                or :: 3 3 3 3
                or :: 4 4 3 2 2 2 2 1
'''
        self.InitUI(parent=parent, id=id, title=title)
# ----------------------------------------------------------------------------
        
# DESIGN ---------------------------------------------------------------------
    def InitUI(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=self.panel_size)
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.label1 = wx.StaticText(self.panel, label="Input List of Edges", pos=(10,5))
        self.label1_font = wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD)
        self.label1.SetFont(self.label1_font)
        self.text = wx.TextCtrl(self.panel, style=wx.TE_PROCESS_ENTER, pos=(10, 35), size=(275,- 1))
        self.text.SetFocus()
        
        self.label2 = wx.StaticText(self.panel, label="Vertex Label Options", pos=(10,75))
        self.label2_font = wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD)
        self.label2.SetFont(self.label2_font)
        
        self.radio1 = wx.RadioButton(self.panel, label="Uppercase Letters (ABC)", pos=(10,105))
        self.radio2 = wx.RadioButton(self.panel, label="Lowercase Letters (abc)", pos=(10,135))
        self.radio3 = wx.RadioButton(self.panel, label="Integers (123)", pos=(10,165))
        
        self.error_title = wx.StaticText(self.panel, wx.ID_ANY, label=self.error_title_label, pos=(85, 400))
        self.error_title.SetForegroundColour((255,0,0))
        self.error_title_font = wx.Font(18, wx.MODERN, wx.NORMAL, wx.BOLD)
        self.error_title.SetFont(self.error_title_font)
        self.error_title.Hide()
        
        self.error_body = wx.StaticText(self.panel, wx.ID_ANY, label=self.error_body_label, pos=(35, 450))
        self.error_body_font = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL)
        self.error_body.SetFont(self.error_body_font)
        self.error_body.Hide()
        
        self.adjacency_matrix_text = wx.StaticText(self.panel,label="",pos=(10,1000),style=wx.TE_MULTILINE)
        self.adjacency_matrix_text.SetForegroundColour((0,0,0))
        self.adjacecy_matrix_font = wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL)
        self.adjacency_matrix_text.SetFont(self.adjacecy_matrix_font)
        self.adjacency_matrix_text.Hide()
        
        self.Bind(wx.EVT_TEXT_ENTER, self.onEnter, self.text) 
        self.Bind(wx.EVT_TEXT_ENTER, self.onDrawEdges)
        self.Bind(wx.EVT_RADIOBUTTON, self.onRadioButton)
        #self.panel.Bind(wx.EVT_MOTION, self.onMove)
        self.panel.Bind(wx.EVT_PAINT, self.onDrawEdges)

        self.Centre()
        self.Show(True)
# ----------------------------------------------------------------------------

# Amotz Bar-Noy Section ------------------------------------------------------
    def func(self, s):
        num = s[0]
        del s[0]
        for i in range(num):
            s[i] -= 1
        return sorted(s, reverse=True)

    def Graphic(self, s):
        first = s[0]
        if first == 0:                      # Observation I
            self.error_title.Hide()
            self.error_body.Hide()
            self.adjacency_matrix_text.Show()
            return True
        elif first >= self.n:               # Observation II
            self.error_title.Show()
            self.error_body.Show()
            self.adjacency_matrix_text.Hide()
            return False
        elif s[first] == 0:                 # Observation III
            self.error_title.Show()
            self.error_body.Show()
            self.adjacency_matrix_text.Hide()
            return False
        elif sum(s) % 2 == 1:               # Sum(di) != 0 ; for i in range(n)
            self.error_title.Show()
            self.error_body.Show()
            self.adjacency_matrix_text.Hide()
            return False
        else:
            s = self.func(s)
            return self.Graphic(s)
#-----------------------------------------------------------------------------

# ASSISTING FUNCTIONS --------------------------------------------------------------
    def destroyButtons(self):
        if len(self.vertices_list) > 0:
            for vertex in self.vertices_list:
                vertex.destroyButton()

    def placeVertices(self):
        for i in range(self.n):
            if self.radio1.GetValue():
                v_lbl = chr(65+i)
            if self.radio2.GetValue():
                v_lbl = chr(97+i)
            if self.radio3.GetValue():
                v_lbl = str(i)
            theta = -(radians((360.0/self.n)*i))
            x = (0.0)*cos(theta)-(self.k)*sin(theta)+(500)-35
            y = -((self.k)*cos(theta)+(0.0)*sin(theta))+(500)
            vertex = Vertex(parent=self.panel, edges=self.vertex_array[i], label=v_lbl, pos=[x,y])
            vertex.button.Bind(wx.EVT_BUTTON, self.onButton)
            vertex.button.Bind(wx.EVT_MOTION, self.onMove)
            self.vertices_list.append(vertex)
        self.createAdjacencyList()
 
    def printVerticesPos(self):
        for vertex in self.vertices_list:
            x, y = vertex.getPosition()
            print ("Vertex %s at pos (%i,%i)"%(vertex.button.GetLabel(),int(x),int(y)))
            
    def createAdjacencyList(self):
        v_list = []
        for v in self.vertices_list:
            v_list.append(v)
        v_list = sample(v_list, len(v_list))
        v_list = sorted(v_list, key=lambda v: v.edges, reverse=True)
        vlist = []
        for vx in v_list:
            vlist.append(str("%i%c" % (vx.edges, vx.label)))
        print vlist
        length = len(self.vertices_list)
        for i in range(length):
            edges = v_list[0].edges
            lbl = v_list[0].label
            button = [v for v in self.vertices_list if v.label == lbl]
            del v_list[0]
            length = len(v_list)
            for e in range(edges):
                button[0].adjacency_list.append(v_list[e])
                v_list[e].edges -= 1
            v_list = sample(v_list, len(v_list))
            v_list = sorted(v_list, key=lambda v: v.edges, reverse=True)
            vlist = []
            for vx in v_list:
                vlist.append(str("%i%c" % (vx.edges, vx.label)))
            print vlist

    def buildAdjacencyMatrix(self, adjacency_matrix):
        n = len(self.vertices_list)
        adj_matrix_txt = []
        sz = n + 2
        print "len(self.vertices_list) = ", sz
        for x in range(sz):
            for y in range(sz-1):
                if x == 0 and x == 0:
                    pass
                elif x == 0 and x > 0 and y < sz+1:
                    adj_matrix_txt.append(" ")
                    adj_matrix_txt.append(str(self.vertices_list[y-2].button.GetLabel()))
                elif y == 0 and y > 0 and x < sz+1:
                    adj_matrix_txt.append(" ")
                    adj_matrix_txt.append(str(self.vertices_list[x-2].button.GetLabel()))
                elif x == sz-1 or y == sz-1:
                    adj_matrix_txt.append("\n")
                elif x < sz+1 and y < sz+1:
                    adj_matrix_txt.append(" ")
                    adj_matrix_txt.append(str(adjacency_matrix[2-1][y-2]))
                else:
                    print "ERROR ERROR, WHAT SHALL WE DO!!"
        print "adj_matrix_txt"
        adj_matrix_txt = ''.join(adj_matrix_txt)
        print adj_matrix_txt
        self.adjacency_matrix_text.SetLabel(adj_matrix_txt)
        self.adjacency_matrix_text.Show()
        
            
# ----------------------------------------------------------------------------

# EVENTS ---------------------------------------------------------------------
    def onEnter(self, event):
        self.destroyButtons()
        self.vertex_array = []
        self.vertices_list = []
        self.draw = True
        self.input_text = self.text.GetValue()
        self.vertex_array = map(int, self.input_text.split())
        self.n = len(self.vertex_array)
        self.adjacency_matrix = list(zeros(shape=(self.n,self.n),dtype=int))
        arr = deepcopy(self.vertex_array)
        if self.Graphic(arr):   # GRAPHIC /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
            self.placeVertices()
            self.printVerticesPos()
        self.Refresh()
        #if self.Graphic(arr):   # Ugly Need to fix, ewww
        #    self.buildAdjacencyMatrix(self.adjacency_matrix)
    
    def onDrawEdges(self, event): 
        if self.draw:
            self.dc = wx.PaintDC(event.GetEventObject())
            self.dc.Clear()
            black_pen = wx.Pen(wx.Colour(0,0,0), 3) 
            self.dc.SetPen(black_pen)
            length = len(self.vertices_list)
            for v1, vertex1 in enumerate(self.vertices_list):
                v1_x, v1_y = vertex1.getPosition()
                print vertex1.button.GetLabel()
                for v2, vertex2 in enumerate(self.vertices_list[v1].adjacency_list):
                    v2_x, v2_y = vertex2.getPosition()
                    print "-- ", vertex2.button.GetLabel()
                    self.adjacency_matrix[v1][v2] = 1
                    self.adjacency_matrix[v2][v1] = 1
                    self.dc.DrawLine(v1_x+25, v1_y+25, v2_x+25, v2_y+25)
        event.Skip()
    
    def onRadioButton(self, event):
        for i, vertex in enumerate(self.vertices_list):
            if self.radio1.GetValue():
                v_lbl = chr(65+i)
            if self.radio2.GetValue():
                v_lbl = chr(97+i)
            if self.radio3.GetValue():
                v_lbl = str(i)
            vertex.button.SetLabel(v_lbl)
            vertex.label = v_lbl

    def onButton(self, event):
        print("Click")
        self.button = event.GetEventObject()
        sx,sy = self.button.GetPositionTuple()
        dx,dy = wx.GetMousePosition()
        lbl = self.button.GetLabel()
        v_button = [v for v in self.vertices_list if v.label == lbl]
        v_button[0].pos[0] = sx-dx
        v_button[0].pos[1] = sy-dy
        self.button._x, self.button._y = (sx-dx, sy-dy)
        if self.down:
            self.down = False
            print("Down is False")
        else:
            self.down = True
            print("Down is True")
        event.Skip()

    def onMove(self, event):
        if self.down:
            x, y = wx.GetMousePosition()
            button = event.GetEventObject()
            print "event.GetEventObject() = ", event.GetEventObject() 
            lbl = button.GetLabel()
            v_button = [v for v in self.vertices_list if v.label == lbl]
            print("%i, %i" % (self.button._x+x, self.button._y+y))
            button.SetPosition(wx.Point(self.button._x+x, self.button._y+y))
            self.Refresh()  # Triggers EVT_PAINT on panel
        event.Skip()
# ----------------------------------------------------------------------------

# MAINLOOP -------------------------------------------------------------------
def main():
    app = wx.App(False)
    widgetFrame(None, -1, "Graph by Borden 1.01")
    app.MainLoop()

if __name__ == "__main__":
    main()
# ----------------------------------------------------------------------------



