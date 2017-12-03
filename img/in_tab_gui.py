#!/usr/bin/env python


import os, sys
import math
import collections
import  gtk
import Tkinter
import time 

from optparse import OptionParser


try :
    import linuxcnc
    import hal
except :
    print 'error'

parser = OptionParser()
parser.add_option('-w', '--window', dest='window', help='Embed into window')


def reparent(window, parent):
    from Xlib import display
    from Xlib.xobject import drawable
    d = display.Display()
    dd=d.display
    w = drawable.Window(d.display, window.window.xid, 0)
    atom = d.get_atom('_XEMBED_INFO')
    w.change_property(atom, atom, 32, [0, 1])
    w.reparent(parent, 0, 0)
    w.map()
    d.sync()

class Widgets:
	def __init__(self, xml):
		self._xml = xml
	def __getattr__(self, attr):
		r = self._xml.get_object(attr)
		if r is None: raise AttributeError, "No widget %r" % attr
		return r
	def __getitem__(self, attr):
		r = self._xml.get_object(attr)
		if r is None: raise IndexError, "No widget %r" % attr
		    
class ContourEditor:
    def __init__(self, options):
        builder = gtk.Builder()
        builder.add_from_file('gui.glade')

        window = builder.get_object('window1')
        
        self.builder = builder
        self.builder.connect_signals(self)
        self.widgets = Widgets(self.builder)
        
        self.halcomp = hal.component("cedit")
        self.halcomp.newpin( "ps_enable_tab_preview", hal.HAL_BIT, hal.HAL_OUT)
        self.halcomp.ready()
            
                          
        xid = None
        if options.window:
            w = window
            xid = long(options.window, 0)
            plug = gtk.Plug(xid)
            for c in window.get_children():
                window.remove(c)
                plug.add(c)
            window = plug        
        
        
        window.connect("delete-event", gtk.main_quit)
        window.show_all()


        if options.window:
            reparent(window, xid)

        res = os.spawnvp(os.P_WAIT, "halcmd", ["halcmd", "-f", "/home/nkp/linuxcnc/configs/G71_sim_config/postCE.hal"])
        if res: raise SystemExit, res
        
    def open_c(self,widget, ):
    
        self.word = self.widgets.entry1.get_text()
        print '11111=',self.word

        fname = 'g1.ngc'

        try:
            c = linuxcnc.command()
            stat = linuxcnc.stat()
            stat.poll()

            if stat.interp_state == linuxcnc.INTERP_IDLE :
                try :
                    self.halcomp["ps_enable_tab_preview"] = 1
                    Tkinter.Tk().tk.call("send", "axis", ("remote", "open_file_name", fname))
                    c.wait_complete()
                    self.halcomp["ps_enable_tab_preview"] = 0

                except Tkinter.TclError as detail:
                    c.reset_interpreter()
                    time.sleep(0.5)
                    c.mode(linuxcnc.MODE_AUTO)
                    c.program_open(fname)

        except :
            pass

 
                      
options, args = parser.parse_args()


gui = ContourEditor(options)
gtk.main()
