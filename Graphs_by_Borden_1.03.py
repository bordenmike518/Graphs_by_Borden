# ============================================================================
# Author      :: Michael Borden
# Created     :: Nov 19, 2017
# Last Update :: Nov 21, 2017
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
from copy import deepcopy
from math import sin, cos, radians

# INITIALIZATION -------------------------------------------------------------
class widgetFrame(wx.Frame):
    def __init__(self, parent, id, title):
        self.panel_size = (1000, 1000)
        self.k = 400.0   # Temp
        self.vertex_list = []
        self.vertex_array = []
        self.down = False
        self.draw = False
        error_title = "ERROR - ERROR - ERROR - ERROR - ERROR"
        error_body = '''
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
# ----------------------------------------------------------------------------
        
# DESIGN ---------------------------------------------------------------------
        wx.Frame.__init__(self, parent, id, title, size=self.panel_size)
        self.panel = wx.Panel(self, wx.ID_ANY)        
        self.panel.Bind(wx.EVT_MOTION, self.onMove)
        self.label = wx.StaticText(self.panel, label="Input ::", pos=(10,25), size=(90, -1))
        self.error_title = wx.StaticText(self.panel, wx.ID_ANY, label=error_title, pos=(85, 100))
        self.error_title.SetForegroundColour((255,0,0))
        self.error_title_font = wx.Font(18, wx.MODERN, wx.NORMAL, wx.BOLD)
        self.error_title.SetFont(self.error_title_font)
        self.error_title.Hide()
        self.error_body = wx.StaticText(self.panel, wx.ID_ANY, label=error_body, pos=(35, 150))
        self.error_body_font = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL)
        self.error_body.SetFont(self.error_body_font)
        self.error_body.Hide()
        self.text = wx.TextCtrl(self.panel, style=wx.TE_PROCESS_ENTER, pos=(100, 20), size=(300,- 1))
        self.text.SetFocus()
        self.topSizer = wx.BoxSizer(wx.VERTICAL)
        self.Bind(wx.EVT_TEXT_ENTER, self.onEnter, self.text) 
        self.Bind(wx.EVT_TEXT_ENTER, self.onDrawEdges)
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
#-----------------------------------------------------------------------------

# ASSISTING FUNCTIONS --------------------------------------------------------------
    def destroyButtons(self):
        if len(self.vertex_list) > 0:
            for button in self.vertex_list:
                button.Destroy()

    def placeVertices(self):
        size = (50, 50)
        offset = -35
        for i in range(self.n):
            theta = -(radians((360.0/self.n)*i))
            x = (0.0)*cos(theta)-(self.k)*sin(theta)+(self.panel_size[0]/2.0)+offset
            y = -((self.k)*cos(theta)+(0.0)*sin(theta))+(self.panel_size[1]/2.0)
            self.vertex_list.append(wx.Button(parent=self.panel, 
                                              id=-1, 
                                              label=chr(65+i), 
                                              pos=(x, y), 
                                              size=size))
            self.vertex_list[i].Bind(wx.EVT_BUTTON, self.onButton)
            self.vertex_list[i].Bind(wx.EVT_MOTION, self.onMove)
 
    def printVerticesPos(self):
        for vertex in self.vertex_list:
            x, y = vertex.GetPositionTuple()
            print ("Vertex %s at pos (%i, %i)" % (vertex.GetLabel(), int(x), int(y)))
            
    def Skip(self, edges, length, skip, vertex_array):
        v_arr = deepcopy(vertex_array)
        count = 0
        pos_index = 0
        j = 0
        s = False
        while s == False and skip > 0:
            while j < length:
                if v_arr[j] == 0:
                    pos_index += 1
                if j == pos_index and count < edges and v_arr[j] != 0:
                    pos_index += skip
                    count += 1
                    v_arr[j] -= 1
                j += 1
            if count == edges:
                s = True
            else:
                skip -= 1
        if count == edges:
            return skip
        else:
            return 1
    
    def getSkip(self, edges, length, vertex_array):
        if edges == 0 or length == 0:
            return 1
        else:
            return self.Skip(edges, length, length/edges, vertex_array)
            
# ----------------------------------------------------------------------------

# EVENTS ---------------------------------------------------------------------
    def onEnter(self, event):
        self.destroyButtons()
        self.vertex_list = []
        self.vertex_array = []
        self.draw = True
        self.input_text = self.text.GetValue()
        self.vertex_array = map(int, self.input_text.split())
        self.n = len(self.vertex_array)
        arr = deepcopy(self.vertex_array)
        if self.Graphic(arr):   # GRAPHIC /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
            self.placeVertices()
            self.printVerticesPos()
        self.Refresh()
        
    
    def onDrawEdges(self, event): 
        if self.draw:
            self.dc = wx.PaintDC(event.GetEventObject())
            self.dc.Clear()
            black_pen = wx.Pen(wx.Colour(0,0,0), 3) 
            self.dc.SetPen(black_pen)
            v_array = deepcopy(self.vertex_array)
            print v_array
            length = len(v_array)
            for i, vertex1 in enumerate(self.vertex_list):
                v1_x, v1_y = vertex1.GetPositionTuple()
                edges = v_array[i]
                v_array[i] = 0
                v1_label = vertex1.GetLabel()
                count = 0
                pos_index = 0
                skip = self.getSkip(edges, length-i, v_array)
                for j, vertex2 in enumerate(self.vertex_list):
                    v2_label = vertex2.GetLabel()
                    if v_array[j] == 0:
                        pos_index += 1
                    print (j, " == ", pos_index, " and ", count, " < ", edges, " and ", v_array[j], " != 0")
                    if j == pos_index and count < edges and v_array[j] != 0:
                        pos_index += skip
                        count += 1
                        v_array[j] -= 1
                        v2_x, v2_y = vertex2.GetPositionTuple()
                        self.dc.DrawLine(v1_x+25, v1_y+25, v2_x+25, v2_y+25)
                print v_array
        event.Skip()

    def onButton(self, event):
        print("Click")
        self.cur_vertex = event.GetEventObject()
        sx,sy = self.cur_vertex.GetPositionTuple()
        dx,dy = wx.GetMousePosition()
        self.cur_vertex._x, self.cur_vertex._y   = (sx-dx, sy-dy)
        if self.down == True:
            self.down = False
            print("Down is False")
        else:
            self.down = True
            print("Down is True")
        event.Skip()

    def onMove(self, event):
        if self.down:
            x, y = wx.GetMousePosition()
            print("%i, %i" % (x+self.cur_vertex._x, y+self.cur_vertex._y))
            self.cur_vertex.SetPosition(wx.Point(x+self.cur_vertex._x,y+self.cur_vertex._y))
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



