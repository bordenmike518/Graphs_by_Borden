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
# Example     :: 1 1  or 2 2 2 or 3 3 3 3 or 4 4 3 2 2 2 2 1 or Petersen Graph
# ==============================================================================

import wx
from random import sample, randint
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
                              size=(60, 50))
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
        self.epv_array = []
        self.edges_label_array = []
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
        self.attr_font = wx.Font(11, wx.MODERN, wx.NORMAL, wx.BOLD)
        self.label1.SetFont(self.attr_font)
        self.input_textbox = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER, 
                                               pos=(10, 40), 
                                               size=(275,- 1))
        self.input_textbox.SetFocus()
        
        self.label2 = wx.StaticText(self, label="Vertex Label Options", 
                                          pos=(10,80))
        self.label2.SetFont(self.attr_font)
        self.radio1 = wx.RadioButton(self, label="Uppercase Letters (ABC)", 
                                           pos=(10,110),
                                           style=wx.RB_GROUP)
        self.radio2 = wx.RadioButton(self, label="Lowercase Letters (abc)", 
                                           pos=(10,140))
        self.radio3 = wx.RadioButton(self, label="Integers (123)", pos=(10,170))
        
        self.label3 = wx.StaticText(self, label="Redrawing Graph", pos=(10,205))
        self.label3.SetFont(self.attr_font)
        self.radio4 = wx.RadioButton(self, label="Keep Layout", pos=(10,235),
                                           style=wx.RB_GROUP)
        self.radio5 = wx.RadioButton(self, label="Reset Layout", pos=(10,265))
        
        self.label4 = wx.StaticText(self, label="Graph Shape", pos=(10,300))
        self.label4.SetFont(self.attr_font)
        self.radio6 = wx.RadioButton(self, label="Circular", pos=(10,330),
                                           style=wx.RB_GROUP)
        self.radio7 = wx.RadioButton(self, label="Random", pos=(10,360))
        
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
        
        self.Bind(wx.EVT_TEXT_ENTER, self.onEnter, self.input_textbox) 
        #self.Bind(wx.EVT_TEXT_ENTER, self.onDrawEdges)
        self.Bind(wx.EVT_RADIOBUTTON, self.onRadioButton)
        self.Bind(wx.EVT_MOTION, self.onMove)
        self.Bind(wx.EVT_PAINT, self.onDrawEdges)
        #self.Bind(wx.EVT_MOTION, self.onDrawEdges)

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
        # Observation I
        if first == 0:  # If reducable to Null, then graph, else show() error.
            self.error_title.Hide()
            self.error_body.Hide()
            return True
        # Observation II, III, Sum(di) != 0 ; for i in range(n)
        elif first >= self.n or s[first] == 0 or sum(s) % 2 == 1:               
            self.error_title.Show()
            self.error_body.Show()
            return False
        else:
            s = self.func(s)
            return self.Graphic(s)  # Recursive
#-------------------------------------------------------------------------------

# ASSISTING FUNCTIONS ----------------------------------------------------------
    def destroyButtons(self):
        if len(self.vertices_list) > 0:
            [vertex.destroyButton() for vertex in self.vertices_list]
                

    def labelMaker(self, i):
        if self.radio1.GetValue():
            if i >= 26:
                df = i-26
                v_lbl = ''.join([chr(65+i/26-1), chr(65+i%26)])
            else:
                v_lbl = chr(65+i)
        if self.radio2.GetValue():
            if i >= 26:
                df = i-26
                v_lbl = ''.join([chr(65+i/26-1), chr(65+i%26)])
            else:
                v_lbl = chr(97+i)
        if self.radio3.GetValue():
            v_lbl = str(i)
        return v_lbl

    def placeVertices(self):
        for i in range(self.n):
            if self.radio5.GetValue() or not self.same_input:
                v_lbl = self.labelMaker(i)
                theta = -(radians((360.0/self.n)*i))
                if self.radio6.GetValue():
                    x = (0.0)*cos(theta)-(self.k)*sin(theta)+(500)-35
                    y = -((self.k)*cos(theta)+(0.0)*sin(theta))+(500)
                else:
                    y = randint(50, 900)
                    if y > 500:
                        x = randint(50, 900)
                    else:
                        x = randint(250, 900)
                vertex = Vertex(parent=self, edges=self.epv_array[i], 
                                label=v_lbl, pos=[x,y])
                vertex.button.Bind(wx.EVT_BUTTON, self.onButton)
                vertex.button.Bind(wx.EVT_MOTION, self.onMove)
                self.vertices_list.append(vertex)
            else:
                self.vertices_list[i].adjacency_list = []
                self.vertices_list[i].edges = self.epv_array[i]
 
    def printVerticesPos(self):
        for vertex in self.vertices_list:
            x, y = vertex.getPosition()
            print ("Vertex %s at pos (%i,%i)"%(vertex.button.GetLabel(),
                                               int(x),
                                               int(y)))
     
    def print_v_list(self, v_list):
        vlist = []
        [vlist.append(str("%s%s"%(str(v.edges),str(v.label)))) for v in v_list]
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
    
    def MakeSet(self, edges_array):
        buff_list = []
        for i, edge in enumerate(edges_array):
            buff_list.append(set(self.vertices_list[i].label))
        return buff_list
        
    def FindSet(self, edge, edge_array):
        for i, e in enumerate(edge_array):
            if edge in e:
                return i
                
    def UnionSet(self, i, j, edge_array):
        edge_array[j] = edge_array[i].union(edge_array[j])
        del edge_array[i]
        return edge_array
        
    def CountSet(self, edge_array):
        count_set = []
        for e_set in edge_array:
            count_set.append(len(e_set))
        return count_set
        
    
    def createSet(self, edges_array):
        edge_array = self.MakeSet(edges_array)
        for edge in edges_array:
            for e, _ in enumerate(edge[:-1:]):
                i = self.FindSet(edge[e], edge_array)
                j = self.FindSet(edge[e+1], edge_array)
                if i is not j:
                    edge_array = self.UnionSet(i, j, edge_array)
        print "edge_array = ", edge_array
        count_set = self.CountSet(edge_array)
        print "count_set = ", sorted(count_set, reverse=True)
        
        
            
# ------------------------------------------------------------------------------

# EVENTS -----------------------------------------------------------------------
    def onEnter(self, event):
        self.draw = True
        input_text = self.input_textbox.GetValue()
        if self.radio5.GetValue() or \
           map(int, input_text.split()) != self.epv_array:
            self.destroyButtons()
            self.vertices_list = []
            self.epv_array = []
            self.epv_array = map(int, input_text.split())
            self.same_input = False
            self.n = len(self.epv_array)
        else:
            self.same_input = True
        if self.Graphic(self.epv_array):   # GRAPHIC test!
            self.placeVertices()
            self.printVerticesPos()
            self.createAdjacencyList()
        self.input_textbox.SetFocus()
        self.input_textbox.SetInsertionPointEnd()
        self.Refresh()
        event.Skip()
    
    def onDrawEdges(self, event):
        button = event.GetEventObject()
        self.edges_label_array = []
        #                                4 Linux, 6 Windows <<INVESTIGAGE>>>
        if self.draw and len(button.GetLabel()) < 6:    
            self.dc = wx.PaintDC(event.GetEventObject())
            self.dc.Clear()
            black_pen = wx.Pen(wx.Colour(0,0,0), 3) 
            self.dc.SetPen(black_pen)
            for v1, vertex1 in enumerate(self.vertices_list):
                v1_x, v1_y = vertex1.getPosition()
                v1_lbl = vertex1.button.GetLabel()
                print v1_lbl
                for vertex2 in self.vertices_list[v1].adjacency_list:
                    v2_x, v2_y = vertex2.getPosition()
                    v2_lbl = vertex2.button.GetLabel()
                    tpl = (v1_lbl, v2_lbl)
                    if tpl not in self.edges_label_array and \
                        tpl[::-1] not in self.edges_label_array:
                        self.edges_label_array.append(tpl)
                        print "-- ", v2_lbl
                        self.dc.DrawLine(v1_x+30, v1_y+25, v2_x+30, v2_y+25)
            for i, edge in enumerate(self.edges_label_array):
                print "Edge ", i, " = ", "(", edge[0], ", ", edge[1], ")"
            self.createSet(self.edges_label_array)
        event.Skip()
    
    def onRadioButton(self, event):
        rb = event.GetEventObject()
        rb_lbl = rb.GetLabel() 
        if rb_lbl == self.radio1.GetLabel() or \
           rb_lbl == self.radio2.GetLabel() or \
           rb_lbl == self.radio3.GetLabel(): 
            for i, vertex in enumerate(self.vertices_list):
                v_lbl = self.labelMaker(i)
                vertex.button.SetLabel(v_lbl)
                vertex.label = v_lbl
        elif rb_lbl == self.radio6.GetLabel() or \
             rb_lbl == self.radio7.GetLabel():
            self.radio5.SetValue(True)
        self.input_textbox.SetFocus()
        self.input_textbox.SetInsertionPointEnd()
        event.Skip()

    def onButton(self, event):
        print("Click")
        self.button = event.GetEventObject()
        bx, by = self.button.GetPositionTuple()
        mx, my = wx.GetMousePosition()
        self.clicked_button = self.button.GetLabel()
        self.button._x, self.button._y = (bx-mx, by-my)
        if self.down:
            self.down = False
            print("Down is False")
        else:
            self.down = True
            print("Down is True")
        self.input_textbox.SetFocus()
        self.input_textbox.SetInsertionPointEnd()
        event.Skip()

    def onMove(self, event):
        if self.down:
            button = event.GetEventObject()
            lbl = button.GetLabel()
            if lbl == self.clicked_button and len(lbl) < 4:
                mx, my = wx.GetMousePosition()
                print("%i, %i" % (self.button._x+mx, self.button._y+my))
                button.SetPosition(wx.Point(self.button._x+mx, 
                                            self.button._y+my))
                self.Refresh()  # Triggers EVT_PAINT on panel
            else:
                v_btn = [v for v in self.vertices_list \
                               if v.button.GetLabel() == self.clicked_button]
                print "vbtn = ", v_btn[0].button.GetLabel()
                vbtn = v_btn[0]
                mx, my = wx.GetMousePosition()
                print("%i, %i" % (vbtn.button._x+mx, vbtn.button._y+my))
                vbtn.button.SetPosition(wx.Point(vbtn.button._x+mx, 
                                                 vbtn.button._y+my))
                self.Refresh()  # Triggers EVT_PAINT on panel
        event.Skip()
# ------------------------------------------------------------------------------

# Main ---------------------------------------------------------------------
class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, 
                                title="Graph by Borden 1.01", 
                                size=(1000, 1000))
        panel = PlotPanel(self)
        self.Centre()
        self.Show()

if __name__ == "__main__":
    print("Starting Graphs by Borden")
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()
# ------------------------------------------------------------------------------



