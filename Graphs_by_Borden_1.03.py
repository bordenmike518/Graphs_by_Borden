# ==============================================================================
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
# ==============================================================================

import wx
from random import sample
from copy import deepcopy
from math import sin, cos, radians

# VERTICES ---------------------------------------------------------------------
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
        self.button.SetBackgroundColour(wx.Colour(0,0,0))
        self.button.SetForegroundColour(wx.Colour(255,255,255))
        self.button_font = wx.Font(20, wx.MODERN, wx.NORMAL, wx.BOLD)
        self.button.SetFont(self.button_font)

    def getPosition(self):
        px, py = self.button.GetPositionTuple()
        self.pos = [px, py]
        return px, py

    def destroyButton(self):
        self.button.Destroy()
# ------------------------------------------------------------------------------

# GUI --------------------------------------------------------------------------
class PlotPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.k = 300.0   # Temp
        self.edges_array = []
        self.vertices_list = []
        self.down = False
        self.draw = False
        self.same_input = False
        self.bldAdjMtrx = False
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
        self.InitUI()
# ------------------------------------------------------------------------------
        
# DESIGN -----------------------------------------------------------------------
    def InitUI(self):
        self.label1 = wx.StaticText(self,label="Input List of Edges",pos=(10,10))
        self.label1_font = wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD)
        self.label1.SetFont(self.label1_font)
        self.text = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, 
                                      pos=(10, 40), 
                                      size=(275,- 1))
        self.text.SetFocus()
        
        self.label2 = wx.StaticText(self, label="Vertex Label Options", 
                                          pos=(10,80))
        self.label2_font = wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD)
        self.label2.SetFont(self.label2_font)
        self.radio1 = wx.RadioButton(self, label="Uppercase Letters (ABC)", 
                                           pos=(10,110),
                                           style=wx.RB_GROUP)
        self.radio2 = wx.RadioButton(self, label="Lowercase Letters (abc)", 
                                           pos=(10,140))
        self.radio3 = wx.RadioButton(self, label="Integers (123)", pos=(10,170))
        
        self.label3 = wx.StaticText(self, label="Redrawing Graph", pos=(10,205))
        self.label3_font = wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD)
        self.label3.SetFont(self.label3_font)
        self.radio4 = wx.RadioButton(self, label="Keep Position", pos=(10,235),
                                           style=wx.RB_GROUP)
        self.radio5 = wx.RadioButton(self, label="Reset Position", pos=(10,265))
        
        self.error_title = wx.StaticText(self, wx.ID_ANY, 
                                         label=self.error_title_label, 
                                         pos=(85, 400))
        self.error_title.SetForegroundColour((255,0,0))
        self.error_title_font = wx.Font(18, wx.MODERN, wx.NORMAL, wx.BOLD)
        self.error_title.SetFont(self.error_title_font)
        self.error_title.Hide()
        
        self.error_body = wx.StaticText(self, wx.ID_ANY, 
                                        label=self.error_body_label, 
                                        pos=(35, 450))
        self.error_body_font = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL)
        self.error_body.SetFont(self.error_body_font)
        self.error_body.Hide()
        
        self.Bind(wx.EVT_TEXT_ENTER, self.onEnter, self.text) 
        self.Bind(wx.EVT_TEXT_ENTER, self.onDrawEdges)
        #self.Bind(wx.EVT_MOTION, self.onDrawEdges)
        self.Bind(wx.EVT_RADIOBUTTON, self.onRadioButton)
        self.Bind(wx.EVT_MOTION, self.onMove)
        self.Bind(wx.EVT_PAINT, self.onDrawEdges)

        self.Show(True)
# ------------------------------------------------------------------------------

# Amotz Bar-Noy Section --------------------------------------------------------
    def func(self, s):
        num = s[0]
        del s[0]
        for i in range(num):
            s[i] -= 1
        return sorted(s, reverse=True)

    def Graphic(self, arr):
        s = deepcopy(arr)
        first = s[0]
        if first == 0:                      # Observation I
            self.error_title.Hide()
            self.error_body.Hide()
            return True
        elif first >= self.n:               # Observation II
            self.error_title.Show()
            self.error_body.Show()
            return False
        elif s[first] == 0:                 # Observation III
            self.error_title.Show()
            self.error_body.Show()
            return False
        elif sum(s) % 2 == 1:               # Sum(di) != 0 ; for i in range(n)
            self.error_title.Show()
            self.error_body.Show()
            return False
        else:
            s = self.func(s)
            return self.Graphic(s)
#-------------------------------------------------------------------------------

# ASSISTING FUNCTIONS ----------------------------------------------------------
    def destroyButtons(self):
        if len(self.vertices_list) > 0:
            for vertex in self.vertices_list:
                vertex.destroyButton()

    def labelMaker(self, i):
        if self.radio1.GetValue():
            v_lbl = chr(65+i)
        if self.radio2.GetValue():
            v_lbl = chr(97+i)
        if self.radio3.GetValue():
            v_lbl = str(i)
        return v_lbl
        

    def placeVertices(self):
        for i in range(self.n):
            if self.radio5.GetValue() or not self.same_input:
                v_lbl = self.labelMaker(i)
                theta = -(radians((360.0/self.n)*i))
                x = (0.0)*cos(theta)-(self.k)*sin(theta)+(500)-35
                y = -((self.k)*cos(theta)+(0.0)*sin(theta))+(500)
                vertex = Vertex(parent=self, edges=self.edges_array[i], 
                                label=v_lbl, pos=[x,y])
                vertex.button.Bind(wx.EVT_BUTTON, self.onButton)
                vertex.button.Bind(wx.EVT_MOTION, self.onMove)
                self.vertices_list.append(vertex)
            else:
                self.vertices_list[i].adjacency_list = []
                self.vertices_list[i].edges = self.edges_array[i]
 
    def printVerticesPos(self):
        for vertex in self.vertices_list:
            x, y = vertex.getPosition()
            print ("Vertex %s at pos (%i,%i)"%(vertex.button.GetLabel(),
                                               int(x),
                                               int(y)))
     
    def print_v_list(self, v_list):
        vlist = []
        for vx in v_list:
            vlist.append(str("%i%c" % (vx.edges, vx.label)))
        print vlist
    
    def createAdjacencyList(self):
        v_list = []
        for v in self.vertices_list:
            v_list.append(v)
        self.print_v_list(v_list)
        v_list = sample(v_list, len(v_list))
        v_list = sorted(v_list, key=lambda v: v.edges, reverse=True)
        for i in range(self.n):
            edges = v_list[0].edges
            lbl = v_list[0].label
            button = [v for v in self.vertices_list if v.label == lbl]
            del v_list[0]
            for e in range(edges):
                button[0].adjacency_list.append(v_list[e])
                [b.adjacency_list.append(button[0]) for b in \
                            self.vertices_list if v_list[e].label == b.label]
                v_list[e].edges -= 1
            v_list = sample(v_list, len(v_list))
            v_list = sorted(v_list, key=lambda v: v.edges, reverse=True)
            self.print_v_list(v_list)
        
            
# ------------------------------------------------------------------------------

# EVENTS -----------------------------------------------------------------------
    def onEnter(self, event):
        self.draw = True
        self.input_text = self.text.GetValue()
        if self.radio5.GetValue() or map(int, self.input_text.split()) != self.edges_array:
            self.destroyButtons()
            self.vertices_list = []
            self.edges_array = []
            self.edges_array = map(int, self.input_text.split())
            self.same_input = False
            self.n = len(self.edges_array)
        else:
            self.same_input = True
        if self.Graphic(self.edges_array):   # GRAPHIC /\/\/\/\/\/\/\/\/\/\/\/\
            self.placeVertices()
            self.printVerticesPos()
            self.createAdjacencyList()
        self.Refresh()
    
    def onDrawEdges(self, event): 
        if self.draw:
            self.dc = wx.PaintDC(event.GetEventObject())
            self.dc.Clear()
            black_pen = wx.Pen(wx.Colour(0,0,0), 3) 
            self.dc.SetPen(black_pen)
            for v1, vertex1 in enumerate(self.vertices_list):
                v1_x, v1_y = vertex1.getPosition()
                print vertex1.button.GetLabel()
                for vertex2 in self.vertices_list[v1].adjacency_list:
                    v2_x, v2_y = vertex2.getPosition()
                    print "-- ", vertex2.button.GetLabel()
                    self.dc.DrawLine(v1_x+25, v1_y+25, v2_x+25, v2_y+25)
        event.Skip()
    
    def onRadioButton(self, event):
        for i, vertex in enumerate(self.vertices_list):
            v_lbl = self.labelMaker(i)
            vertex.button.SetLabel(v_lbl)
            vertex.label = v_lbl

    def onButton(self, event):
        print("Click")
        self.button = event.GetEventObject()
        sx,sy = self.button.GetPositionTuple()
        dx,dy = wx.GetMousePosition()
        self.button_label = self.button.GetLabel()
        v_button = [v for v in self.vertices_list if v.label == self.button_label]
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
            button = event.GetEventObject()
            lbl = button.GetLabel()
            if lbl == self.button_label:
                x, y = wx.GetMousePosition()
                v_button = [v for v in self.vertices_list if v.label == lbl]
                print("%i, %i" % (self.button._x+x, self.button._y+y))
                button.SetPosition(wx.Point(self.button._x+x, self.button._y+y))
                self.Refresh()  # Triggers EVT_PAINT on panel
        event.Skip()
# ------------------------------------------------------------------------------

# MAINLOOP ---------------------------------------------------------------------
class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, 
                                title="Graph by Borden 1.01", 
                                size=(1000, 1500))
        panel = PlotPanel(self)
        self.Centre()
        self.Show()

if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()
# ------------------------------------------------------------------------------



