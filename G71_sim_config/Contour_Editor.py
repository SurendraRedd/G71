#!/usr/bin/python
# --*-- coding:utf-8 --*--

#http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/index.html
from Tkconstants import END, INSERT, ALL, N, S, E, W, RAISED, RIDGE, GROOVE, FLAT, DISABLED, NORMAL, ACTIVE, LEFT

from Tkinter import *
from ttk import Notebook
import re
from math import *

                    
class UI(Frame):
  
    def __init__(self, master):
        Frame.__init__(self, master)   
        
        self.master = master 
                
        self.frame_c=Frame(master) 
        self.frame_c.grid(row=0,column=0,)

        self.frame_r=Frame(master,relief = RIDGE,)
        self.frame_r.grid(row=0,column=1,padx=4,pady=4,sticky=N+E+S+W)        
 

        self.frame_d=Frame(master) 
        self.frame_d.grid(row=1,column=0,padx=4,sticky=E+S+W)

        self.textbox=TextboxClass(frame=self.frame_d,master=self.master)       
        self.A=[] 
        self.All_geo=[]       

        self.nb = Notebook(self.frame_r)

        self.nb_f1 = Frame(self.nb)
        self.nb_f2 = Frame(self.nb)
        self.nb_f3 = Frame(self.nb)
        self.nb_f4 = Frame(self.nb)
        self.nb_f5 = Frame(self.nb)
        self.nb_f6 = Frame(self.nb)
        self.nb_f7 = Frame(self.nb)
        
        self.nb.add(self.nb_f1,)
        self.nb.add(self.nb_f2,)
        self.nb.add(self.nb_f3,)
        self.nb.add(self.nb_f4,)
        self.nb.add(self.nb_f5,)
        self.nb.add(self.nb_f6,)
        self.nb.add(self.nb_f7,)        
        self.nb.pack()
       
        f1=Frame(self.nb_f1,relief = GROOVE,)
        f1.grid(row=0,column=0,padx=2,pady=2,sticky=N+W+E)
        f2=Frame(self.nb_f2,relief = GROOVE,)
        f2.grid(row=1,column=0,padx=2,pady=2,sticky=N+W+E)
        f3=Frame(self.nb_f3,relief = GROOVE,)
        f3.grid(row=2,column=0,padx=2,pady=2,sticky=N+W+E)
        f4=Frame(self.nb_f4,relief = GROOVE,)
        f4.grid(row=3,column=0,padx=2,pady=2,sticky=N+W+E)        
        f5=Frame(self.nb_f5,relief = GROOVE,)
        f5.grid(row=4,column=0,padx=2,pady=2,sticky=N+W+E)  
        f6=Frame(self.nb_f6,relief = GROOVE,)
        f6.grid(row=5,column=0,padx=2,pady=2,sticky=N+W+E) 
        f7=Frame(self.nb_f7,relief = GROOVE,)
        f7.grid(row=6,column=0,padx=2,pady=2,sticky=N+W+E)              
    
        f1.columnconfigure(0,weight=1)
        f2.columnconfigure(0,weight=1)
        f3.columnconfigure(0,weight=1)
        f4.columnconfigure(0,weight=1)        
        f5.columnconfigure(0,weight=1) 
        f6.columnconfigure(0,weight=1)
        f7.columnconfigure(0,weight=1) 
        
        self.f6 = f6
                        
        self.var_st_X = DoubleVar()
        self.var_st_X.set(float(0))
        self.var_st_Z = DoubleVar()
        self.var_st_Z.set(float(-100))
        self.var_Ch = DoubleVar()
        self.var_Ch.set(float(0)) 
        self.var_st_I = DoubleVar()
        self.var_st_I.set(float(0))
        self.var_st_K = DoubleVar()
        self.var_st_K.set(float(0))
        self.rad = DoubleVar()
        self.rad.set(float(0))                        

        self.b_v = Button(f7,command=self.preview_G)
        self.b_v.grid(row=0)

        self.im = PhotoImage(file='images/07.gif')
        self.b_v.config(image=self.im)
        self.b_v.im = self.im

        self.b_g = Button(f7,command=self.preview_V)
        self.b_g.grid(row=1)

        self.im = PhotoImage(file='images/08.gif')
        self.b_g.config(image=self.im)
        self.b_g.im = self.im

        self.b_n = Button(f7,command=self.preview_N)
        self.b_n.grid(row=2)

        self.im = PhotoImage(file='images/06.gif')
        self.b_n.config(image=self.im)
        self.b_n.im = self.im
        
        self.b_c = Button(f7,command=self.preview_C)
        self.b_c.grid(row=3)

        self.im = PhotoImage(file='images/09.gif')
        self.b_c.config(image=self.im)
        self.b_c.im = self.im 
        
        self.run = Button(f7,command=self.run)
        self.run.grid(row=4)

        self.im = PhotoImage(file='images/10.gif')
        self.run.config(image=self.im)
        self.run.im = self.im
         
        self.cenc = Button(f7,command=self.cencel)
        self.cenc.grid(row=5)

        self.im = PhotoImage(file='images/11.gif')
        self.cenc.config(image=self.im)
        self.cenc.im = self.im   
        
        self.rest = Button(f7,command=self.redraw)
        self.rest .grid(row=6)
        
        self.im = PhotoImage(file='images/11.gif')
        self.rest.config(image=self.im)
        self.rest.im = self.im
                    
 #------------------------------------------------------V                    
        Label(f3, text="Next point   X")\
                .grid(row=0,column=0,sticky=N+W,padx=4)
        self.st_X = Entry(f3,width=7,textvariable=self.var_st_X)
        self.st_X.grid(row=0,column=1,sticky=N+E)

        Label(f3, text=("Transition"))\
                .grid(row=3,column=0,sticky=N+W,padx=4)
        self.Ch = Entry(f3,width=7,textvariable=self.var_Ch)
        self.Ch.grid(row=3,column=1,sticky=N+E)

        self.inverse = IntVar()
        self.inverse.set(0)
        
        Label(f3, text=("inverse" ))\
        .grid(row=4,column=0,sticky=N+W,padx=4)        
        self.cb1 = Checkbutton(f3,text="",variable=self.inverse,onvalue=1,offvalue=0)
        self.cb1.grid(row=4,column=1,sticky=N+E)

 
        self.b_added1 = Button(f3,command=self.draw_line)
        self.b_added1.grid(row=5,column=2)

        self.im = PhotoImage(file='images/draw_line.gif')
        self.b_added1.config(image=self.im)
        self.b_added1.im = self.im   
        
        
        self.abs_inc = IntVar()
        self.abs_inc.set(0)
        self.rad1v = Radiobutton(f3,text="abs",variable=self.abs_inc,value=0 )
        self.rad1v.grid(row=0,column=2)
        self.rad2v = Radiobutton(f3,text="inc",variable=self.abs_inc,value=1 )
        self.rad2v.grid(row=1,column=2)

        self.cham_rad = IntVar()
        self.cham_rad.set(0)
        self.rad3v = Radiobutton(f3,text="chm",variable=self.cham_rad,value=0 )
        self.rad3v.grid(row=3,column=2)
        self.rad4v = Radiobutton(f3,text="rad",variable=self.cham_rad,value=1 )
        self.rad4v.grid(row=4,column=2)


        self.cancelV = Button(f3,command=self.cancel)
        self.cancelV.grid(row=6,column=2)

        self.im = PhotoImage(file='images/cancel.gif')
        self.cancelV.config(image=self.im)
        self.cancelV.im = self.im                     
 #----------------------------------------------------------- G           
        Label(f2, text="Next point   Z")\
                .grid(row=0,column=0,sticky=N+W,padx=4)
        self.st_Z = Entry(f2,width=7,textvariable=self.var_st_Z)
        self.st_Z.grid(row=0,column=1,sticky=N+E)       

        Label(f2, text=("Transition"))\
                .grid(row=3,column=0,sticky=N+W,padx=4)
        self.Ch2 = Entry(f2,width=7,textvariable=self.var_Ch)
        self.Ch2.grid(row=3,column=1,sticky=N+E)
        
        Label(f2, text=("inverse" ))\
        .grid(row=4,column=0,sticky=N+W,padx=4)        
        self.cb1 = Checkbutton(f2,text="",variable=self.inverse,onvalue=1,offvalue=0)
        self.cb1.grid(row=4,column=1,sticky=N+E)        
        
        self.b_added2 = Button(f2,command=self.draw_line)
        self.b_added2.grid(row=5,column=2)

        self.im = PhotoImage(file='images/draw_line.gif')
        self.b_added2.config(image=self.im)
        self.b_added2.im = self.im 
        

        self.rad1g = Radiobutton(f2,text="abs",variable=self.abs_inc,value=0 )
        self.rad1g.grid(row=0,column=2)
        self.rad2g = Radiobutton(f2,text="inc",variable=self.abs_inc,value=1 )
        self.rad2g.grid(row=1,column=2) 

        self.rad3g = Radiobutton(f2,text="chm",variable=self.cham_rad,value=0 )
        self.rad3g.grid(row=3,column=2)
        self.rad4g = Radiobutton(f2,text="rad",variable=self.cham_rad,value=1 )
        self.rad4g.grid(row=4,column=2)
        
        self.cancelG = Button(f2,command=self.cancel)
        self.cancelG.grid(row=6,column=2)

        self.im = PhotoImage(file='images/cancel.gif')
        self.cancelG.config(image=self.im)
        self.cancelG.im = self.im                        
#-------------------------------------------------- N
        Label(f4, text="Next point  X")\
                .grid(row=0,column=0,sticky=N+W,padx=4)
        self.st_X = Entry(f4,width=7,textvariable=self.var_st_X)
        self.st_X.grid(row=0,column=1,sticky=N+E)
       
        Label(f4, text="Next point  Z")\
                .grid(row=1,column=0,sticky=N+W,padx=4)
        self.st_Z = Entry(f4,width=7,textvariable=self.var_st_Z)
        self.st_Z.grid(row=1,column=1,sticky=N+E)       

        Label(f4, text=("Chamfer"))\
                .grid(row=2,column=0,sticky=N+W,padx=4)
        self.Ch3 = Entry(f4,width=7,textvariable=self.var_Ch)
        self.Ch3.grid(row=2,column=1,sticky=N+E)
        
        self.b_added3 = Button(f4,command=self.draw_line)
        self.b_added3.grid(row=2,column=2)

        self.im = PhotoImage(file='images/draw_line.gif')
        self.b_added3.config(image=self.im)
        self.b_added3.im = self.im

        self.rad1n = Radiobutton(f4,text="abs",variable=self.abs_inc,value=0 )
        self.rad1n.grid(row=0,column=2)
        self.rad2n = Radiobutton(f4,text="inc",variable=self.abs_inc,value=1 )
        self.rad2n.grid(row=1,column=2) 
        
        self.cancelN = Button(f4,command=self.cancel)
        self.cancelN.grid(row=3,column=2)

        self.im = PhotoImage(file='images/cancel.gif')
        self.cancelN.config(image=self.im)
        self.cancelN.im = self.im 
          
#-------------------------------------------------- C
        
        Label(f5, text="Radius")\
                .grid(row=0,column=0,sticky=N+W,padx=4)
        self.rad = Entry(f5,width=7,textvariable=self.rad)
        self.rad.grid(row=0,column=1,sticky=N+E) 

        Label(f5, text="Next point cX")\
                .grid(row=1,column=0,sticky=N+W,padx=4)
        self.st_X = Entry(f5,width=7,textvariable=self.var_st_X)
        self.st_X.grid(row=1,column=1,sticky=N+E)
       
        Label(f5, text="Next point cZ")\
                .grid(row=2,column=0,sticky=N+W,padx=4)
        self.st_Z = Entry(f5,width=7,textvariable=self.var_st_Z)
        self.st_Z.grid(row=2,column=1,sticky=N+E) 
        
        
        
        self.btIns = Button(f5, text="Inspect",command=self.preview)
        self.btIns.grid(row=3,column=1,sticky=W)        
        
             
        Label(f5, text="I")\
                .grid(row=4,column=0,sticky=N+W,padx=4)
        self.st_I = Entry(f5,width=7,textvariable=self.var_st_I)
        self.st_I.grid(row=4,column=1,sticky=N+E)

        Label(f5, text="K")\
                .grid(row=5,column=0,sticky=N+W,padx=4)
        self.st_K = Entry(f5,width=7,textvariable=self.var_st_K)
        self.st_K.grid(row=5,column=1,sticky=N+E)

        Label(f5, text=("Chamfer"))\
                .grid(row=6,column=0,sticky=N+W,padx=4)
        self.Ch3 = Entry(f5,width=7,textvariable=self.var_Ch)
        self.Ch3.grid(row=6,column=1,sticky=N+E)

        self.alternative = IntVar()
        self.alternative.set(0)
        
        Label(f5, text=("Alternative" ))\
        .grid(row=7,column=0,sticky=N+W,padx=4)        
        self.cb1 = Checkbutton(f5,text="",state=DISABLED,command=self.preview ,variable=self.alternative,onvalue=1,offvalue=0)
        self.cb1.grid(row=7,column=2,sticky=N+E)


        self.rad1c = Radiobutton(f5,text="abs",variable=self.abs_inc,value=0 )
        self.rad1c.grid(row=0,column=2)
        self.rad2c = Radiobutton(f5,text="inc",variable=self.abs_inc,value=1 )
        self.rad2c.grid(row=1,column=2) 

        self.arc_g2_g3 = IntVar()
        self.arc_g2_g3.set(0)
        
        self.rad3c = Radiobutton(f5,text="G3",variable=self.arc_g2_g3,value=0 , command=self.ch_rad)
        self.rad3c.grid(row=3,column=2)
        self.rad4c = Radiobutton(f5,text="G2",variable=self.arc_g2_g3,value=1, command=self.ch_rad)
        self.rad4c.grid(row=4,column=2) 
 
        self.b_added4 = Button(f5, state=DISABLED , command=self.draw_line)
        self.b_added4.grid(row=8,column=2)

        self.im = PhotoImage(file='images/draw_line.gif')
        self.b_added4.config(image=self.im)
        self.b_added4.im = self.im
        
        
        self.cancelN = Button(f5,command=self.cancel)
        self.cancelN.grid(row=9,column=2)

        self.im = PhotoImage(file='images/cancel.gif')
        self.cancelN.config(image=self.im)
        self.cancelN.im = self.im 

#-------------------------------------------------- ST
        Label(f1, text="Start point  X")\
                .grid(row=0,column=0,sticky=N+W,padx=4)
        self.zero_X = Entry(f1,width=7,textvariable=self.var_st_X)
        self.zero_X.grid(row=0,column=1,sticky=N+E)
       
        Label(f1, text="Start  point  Z")\
                .grid(row=1,column=0,sticky=N+W,padx=4)
        self.zero_Z = Entry(f1,width=7,textvariable=self.var_st_Z)
        self.zero_Z.grid(row=1,column=1,sticky=N+E)       

        
        self.b_added5 = Button(f1,command=self.start_point)
        self.b_added5.grid(row=2,column=2)

        self.im = PhotoImage(file='images/draw_line.gif')
        self.b_added5.config(image=self.im)
        self.b_added5.im = self.im
        
#--------------------------------------------------                
        self.canvas=Canvas(self.frame_c,width=650,height=500,bg="red")
        self.canvas.grid(row=0,column=0,sticky=N+E+S+W)
        self.canvas.config(background="#D4DDE3",bd=2)
#------------------------------------------------------------------Grid

        
        self.grid()
        
        self.string = 'F1000\n'
         
        self.page_make_gcode()
        
        self.no_add_lines = 0 
              
                              
        '''# This is what enables using the mouse:
        self.canvas.bind("<ButtonPress-1>", self.move_start)
        self.canvas.bind("<B1-Motion>", self.move_move)'''



        #linux scroll
        #self.canvas.bind("<Button-4>", self.zoomerP)
        #self.canvas.bind("<Button-5>", self.zoomerM)
        
        '''#windows scroll
        self.canvas.bind("<MouseWheel>",self.zoomer)
        # Hack to make zoom work on Windows
        master.bind_all("<MouseWheel>",self.zoomer)
        
    #move
    def move_start(self, event):
        self.canvas.scan_mark(event.x, event.y)
    def move_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

       

    #windows zoom
    def zoomer(self,event):
        if (event.delta > 0):
            self.canvas.scale("all", event.x, event.y, 1.1, 1.1)
        elif (event.delta < 0):
            self.canvas.scale("all", event.x, event.y, 0.9, 0.9)
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))'''

    #linux zoom
    def zoomerP(self,event):
        self.canvas.scale("all", event.x, event.y, 1.1, 1.1)
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))
    def zoomerM(self,event):
        self.canvas.scale("all", event.x, event.y, 0.9, 0.9)
        self.canvas.configure(scrollregion = self.canvas.bbox("all"))
        
                        

        #self.canvas.bind('<Return>',self.zoomerP)
        
        
        
    def cencel(self):

        self.canvas.delete(self.pvd)
        
        self.x_old = self.mem_x
        self.z_old = self.mem_z

        self.A.pop()
   
       
    def preview(self,) :


        try:
            self.canvas.delete(self.cpv)
            self.canvas.delete(self.cpv1)
        except:
            pass            
        try:    
            self.canvas.delete(self.ca)
            self.canvas.delete(self.ca1)
        except:
            pass            
        try:            
            self.canvas.delete(self.ppv1) 
            self.canvas.delete(self.ppg1)
        except:
            pass             
        try:             
            self.canvas.delete(self.ppv2) 
            self.canvas.delete(self.ppg2)                       
        except:
            pass
            self.textbox.prt('\nError' )
                
        self.k = 1
        if self.arc_g2_g3.get():
            self.k = 1
        
        if self.abs_inc.get():
            self.z += float(self.st_Z.get())             
            self.x += float(self.st_X.get())  
        else:
            self.z = float(self.st_Z.get()) + 325            
            self.x = float(self.st_X.get()) + 250 
 
        self.r = float(self.rad.get()) 
        r=self.r
        
        if self.alternative.get():
            self.s1= None
            self.s2="gray12"
            self.w1 = 1
            self.w2 = 2
        else:
            self.s2= None
            self.s1="gray12"
            self.w2 = 1
            self.w1 = 2       
        
        try:
            ix1,iz1,ix2,iz2 = self.insc_arc_arc(self.x_old,self.z_old,self.x,self.z,self.r)
            ixx1,izz1,ixx2,izz2 = ix1,iz1,ix2,iz2

            # отрисуем центры окружностей с линиями 
            if self.fset == 3:           
                if self.alternative.get(): 
                    self.ca1 = self.canvas.create_oval([izz2 - 2,ixx2 - 2],[izz2 + 2,ixx2 + 2],fill="red")
                    self.ppv1 = self.canvas.create_line(iz2,0,iz2,500,width=1,fill="red",stipple="gray50")
                    self.ppg1 = self.canvas.create_line(0,ix2,650,ix2,width=1,fill="red",stipple="gray50")              
                else:
                    self.ca = self.canvas.create_oval([izz1 - 2,ixx1 - 2],[izz1 + 2,ixx1 + 2],fill="red")
                    self.ppv2 = self.canvas.create_line(iz1,0,iz1,500,width=1,fill="red",stipple="gray50")
                    self.ppg2 = self.canvas.create_line(0,ix1,650,ix1,width=1,fill="red",stipple="gray50") 
                    pass 

            #print 'ix1 =',ix1-250, 'iz1=',iz1-325, 'ix2=',ix2-250, 'iz2=',iz2-325
            
            '''print 'self.x =' , self.x                      
            print 'self.z =' , self.z
            print 'oldx =' , self.x_old                     
            print 'oldz =' , self.z_old'''           
                       


            # ARC1 
            # st.point self.x_old self.z_old    
            if (ix1>self.x_old):#XXX когда ix1 == self.x_old (и ниже)
                if (iz1<self.z_old):
                    self.st_arc1  = degrees(atan2(ix1-self.x_old,self.z_old-iz1)) 
                else:                
                    self.st_arc1  = 180 - degrees(atan2(ix1-self.x_old,iz1-self.z_old))                    
            else:
                if (iz1<self.z_old):
                    self.st_arc1  = 360-degrees(atan2(self.x_old-ix1,self.z_old-iz1))                    
                else:
                    self.st_arc1  = degrees(atan2(self.x_old-ix1,iz1-self.z_old))+180 
 
                                     
            # end point self.x self.z
            if (ix1>self.x):
                if (iz1<self.z):
                    self.end_arc1 = -(degrees(atan2(ix1-self.x,self.z-iz1)))
                else:                
                    self.end_arc1 = degrees(atan2(ix1-self.x,iz1-self.z))+180 
            else:
                if (iz1<self.z):
                    self.end_arc1 = degrees(atan2(self.x-ix1,self.z-iz1))
                else:
                    self.end_arc1 = 180 - degrees(atan2(self.x-ix1,iz1-self.z))
                    
                     
            # ARC2
            # st.point self.x_old self.z_old            
            if (ix2>self.x_old):
                if (iz2<self.z_old):
                    print '1s'
                    self.st_arc2  = degrees(atan2(ix2-self.x_old,self.z_old-iz2)) 
                else:                
                    print '2s'
                    self.st_arc2  = 180 - degrees(atan2(ix2-self.x_old,iz2-self.z_old))                    
            else:
                if (iz2<self.z_old):
                    print '3s'
                    self.st_arc2  = 360-degrees(atan2(self.x_old-ix2,self.z_old-iz2))                    
                else:
                    print '4s'
                    self.st_arc2  = degrees(atan2(self.x_old-ix2,iz2-self.z_old))+180 

            # end point self.x self.z
            if (ix2>self.x):
                if (iz2<self.z):
                    self.end_arc2 = -(degrees(atan2(ix2-self.x,self.z-iz2))) 
                else:                
                    self.end_arc2 = degrees(atan2(ix2-self.x,iz2-self.z))+180                   
            else:
                if (iz2<self.z):
                    self.end_arc2 = degrees(atan2(self.x-ix2,self.z-iz2))      
                else:
                    self.end_arc2 = 180 - degrees(atan2(self.x-ix2,iz2-self.z))
                                         
            END1 =   -(self.st_arc1 + self.end_arc1)
            END2 =   -(self.st_arc2 + self.end_arc2)
            
            if self.arc_g2_g3.get():
                END1 = 360 - self.end_arc1 - self.st_arc1
                END2 = 360 - self.st_arc2  - self.end_arc2
                             
            print '=========================================================='                
            print 'st_arc1 ='  , self.st_arc1                      
            print 'end_arc1 =' , self.end_arc1
            print 'END1 =' , END1
            print ''
            print 'st_arc2 ='  , self.st_arc2
            print 'end_arc2 =' , self.end_arc2
            print 'END2 =' , END2
            print '=========================================================='
            print '' 
  
            self.cpv = self.canvas.create_arc([iz1-r,ix1-r],[iz1+r,ix1+r],
            style=ARC,outline="blue",width=self.w1,start=self.st_arc1,extent=END1,stipple=self.s2)
            
            self.cpv1 = self.canvas.create_arc([iz2-r,ix2-r],[iz2+r,ix2+r],
            style=ARC,outline="blue",width=self.w2,start=self.st_arc2,extent=END2,stipple=self.s1)
            
        except:
            self.textbox.prt('\nb_data' )
            self.cb1.config(state="disabled")
            self.b_added4.config(state="disabled")
            return

        self.cb1.config(state="normal")
        self.b_added4.config(state="normal")
        self.textbox.prt('\nok' )        
               
    def start_point(self):
   
        self.z_old = float(self.zero_Z.get()) + 325            
        self.x_old = float(self.zero_X.get()) + 250
        
        self.A.append([1,self.z_old-325,self.x_old-250])
        
        geo=[0,(self.z_old),(self.x_old)]
        self.All_geo.append(geo)
                
        self.canvas.create_oval([self.z_old-2, self.x_old-2],[self.z_old+2, self.x_old+2],fill="blue")
        
        self.nb.add(self.nb_f1)
        self.nb.add(self.nb_f2)
        self.nb.add(self.nb_f3)
        self.nb.add(self.nb_f4)
        self.nb.add(self.nb_f5)
        self.nb.add(self.nb_f6)
        self.nb.add(self.nb_f7)
        self.nb.select(self.nb_f7) 
                 
    def run(self):
        print 'All_geo=',self.All_geo
        self.nb.hide(0)
        self.nb.hide(1)
        self.nb.hide(2)
        self.nb.hide(3)
        self.nb.hide(4)
        self.nb.hide(6)
        ns=1
        for n in self.A: #TODO для self.fset = 3
            if n[0]==1:
                self.string +=str('N%s G1 X%s Z%s \n' % (ns,n[2]*2, n[1]))
            elif n[0]>1:
                self.string +=str('N%s G%s X%s Z%s R%s\n' % (ns,n[0],n[2]*2, n[1],n[3]))                
            ns += 1
        #print  'string=',self.string
            
    def add(self,A): 
        if self.fset <= 2:
        
            part=[1,(self.z-325),(self.x-250)]
            A.append(part)
            
            geo=[1,(self.z_old),(self.x_old),(self.z),(self.x)]
            self.All_geo.append(geo)
            
                   

    def add_arc(self,A): #TODO для self.fset = 3
        if self.fset == 3:
            if self.arc_g2_g3.get():
                ga=2
            else:
                ga=3
            part=[ga,(self.z-325),(self.x-250),(float(self.rad.get()))]
            A.append(part) 
            
            geo=[ga,(self.z_old-325),(self.x_old-250),(self.z-325),(self.x-250),(float(self.rad.get()))]
            self.All_geo.append(geo)            
                    
    def cancel(self):
    
        self.nb.add(self.nb_f1)
        self.nb.add(self.nb_f2)
        self.nb.add(self.nb_f3)
        self.nb.add(self.nb_f4)
        self.nb.add(self.nb_f5)
        self.nb.add(self.nb_f6)
        self.nb.add(self.nb_f7)
        self.nb.select(self.nb_f7)
        try:
            self.canvas.delete(self.pv)
        except:
           pass
           
           
    def radius(self):

        self.x = self.x_old + abs(float(self.var_Ch.get()))
        self.z = self.z_old - abs(float(self.var_Ch.get()))
        
        if self.inverse.get():
            rz1 = self.z 
            rx1 = self.x_old 
            
            rz2 = self.z_old + abs(float(self.var_Ch.get()))
            rx2 = self.x + abs(float(self.var_Ch.get()))        
            
            self.pv2 = self.canvas.create_arc([rz1,rx1],[rz2,rx2],
            style=ARC,outline="blue",width=2,fill="red",start=90,extent=90,stipple="gray50")        
        else:
            rz1 = self.z - abs(float(self.var_Ch.get()))
            rx1 = self.x_old - abs(float(self.var_Ch.get()))
            
            rz2 = self.z + abs(float(self.var_Ch.get()))
            rx2 = self.x_old + abs(float(self.var_Ch.get()))        
            
            self.pv2 = self.canvas.create_arc([rz1,rx1],[rz2,rx2],
            style=ARC,outline="blue",width=2,fill="red",start=0,extent=-90,stipple="gray50")
        
        self.x_old = self.x
        self.z_old = self.z
        
        self.canvas.pack(fill=BOTH, expand=1)
         
        self.add(self.A)            
            
                    
    def chamfer(self):

        self.x = self.x_old + abs(float(self.var_Ch.get()))
        self.z = self.z_old - abs(float(self.var_Ch.get())) 
                        
        self.pvd = self.canvas.create_line(self.z_old,self.x_old,self.z,self.x, width=2,fill="blue",)
        
        self.mem_x  = self.x_old 
        self.mem_z  = self.z_old         
        
        self.x_old = self.x
        self.z_old = self.z
        
        self.canvas.pack(fill=BOTH, expand=1)
         
        self.add(self.A)
        
    def redraw(self,):# с учетом scale
        self.canvas.delete("all")
        for n in self.All_geo:
            if n[0]==1:
                self.canvas.create_line(n[1],n[2],n[3],n[4], width=2,fill="blue",)
            elif n[0]>1:
                pass
            elif n[0]==0:
                self.canvas.create_oval([n[1]-2, n[2]-2],[n[1]+2, n[2]+2],fill="blue")
                
        self.canvas.pack(fill=BOTH, expand=1)   

        self.grid()
        self.x_old = self.x
        self.z_old = self.z
                               
    def draw_line(self):
    
        self.scale_g = 2
        
        self.nb.add(self.nb_f1)
        self.nb.add(self.nb_f2)
        self.nb.add(self.nb_f3)
        self.nb.add(self.nb_f4)
        self.nb.add(self.nb_f5)
        self.nb.add(self.nb_f6)
        self.nb.add(self.nb_f7)
        self.nb.select(self.nb_f7)
        try:
            self.canvas.delete(self.ppv1) 
            self.canvas.delete(self.ppv2)
            self.canvas.delete(self.ppg1) 
            self.canvas.delete(self.ppg2)        
        except:
           pass        
        if self.fset==1: # флаг ,показывает после какой функции выбора сработали
            self.x = self.x_old
            if self.abs_inc.get():
                self.z += float(self.st_Z.get()) 
            else:           
                self.z = float(self.st_Z.get()) + 325 
        elif self.fset==0:
            self.z = self.z_old
            if self.abs_inc.get():            
                self.x += float(self.st_X.get())  
            else:           
                self.x = float(self.st_X.get()) + 250
        elif self.fset==2:
            if self.abs_inc.get():
                self.z += float(self.st_Z.get())             
                self.x += float(self.st_X.get())  
            else:
                self.z = float(self.st_Z.get()) + 325            
                self.x = float(self.st_X.get()) + 250 
        elif self.fset==3:
            pass
                                


        
        if self.fset==3:
            try:
                if self.alternative.get():
                    self.canvas.delete(self.cpv)
                    self.canvas.delete(self.ca)
                else:
                    self.canvas.delete(self.cpv1)
                    self.canvas.delete(self.ca1)
            except:
                pass    
            self.add_arc(self.A)
        else:                               
            self.pvd = self.canvas.create_line(self.z_old,self.x_old,self.z,self.x, width=2,fill="blue",)
            self.add(self.A)

        self.mem_x  = self.x_old 
        self.mem_z  = self.z_old           
            
        self.x_old = self.x
        self.z_old = self.z
        
        self.canvas.pack(fill=BOTH, expand=1)
        
        try:
            self.canvas.delete(self.pv)
        except:
           pass
                           
        if float(self.var_Ch.get()):
            if self.cham_rad.get():
                self.radius()
            else: 
                self.chamfer()
                     
    def preview_G(self):
    
        self.var_st_Z.set(0.00)
        self.var_st_X.set(0.00)
        self.var_Ch.set(0.00)
                
        self.nb.hide(0)
        self.nb.hide(2)
        self.nb.hide(3)
        self.nb.hide(4)
        self.nb.hide(5)
        self.nb.hide(6)
        
        self.x = self.x_old  
        self.z = self.z_old 
        self.pv = self.canvas.create_line(0,self.x,650,self.x,width=1,fill="blue",stipple="gray50")        
        self.canvas.pack(fill=BOTH, expand=1)

        self.fset = 1
        
    def preview_V(self):
    
        self.var_st_X.set(0.00)
        self.var_st_Z.set(0.00)
        self.var_Ch.set(0.00)
        
        self.nb.hide(0)
        self.nb.hide(1)
        self.nb.hide(3)
        self.nb.hide(4)
        self.nb.hide(5)
        self.nb.hide(6)
        
        self.x = self.x_old  
        self.z = self.z_old 
        self.pv = self.canvas.create_line(self.z,0,self.z,500,width=1,fill="blue",stipple="gray50")        

        self.canvas.pack(fill=BOTH, expand=1)

        self.fset = 0
        
    def preview_N(self):
    
        self.var_st_X.set(0.00)
        self.var_st_Z.set(0.00)
        self.var_Ch.set(0.00)
            
        self.nb.hide(0)
        self.nb.hide(1)
        self.nb.hide(2)
        self.nb.hide(4)
        self.nb.hide(5)
        self.nb.hide(6)
        
        self.x = self.x_old  
        self.z = self.z_old 
        self.pv = self.canvas.create_line(self.z,self.x,0,500,width=1,fill="blue",stipple="gray50")        

        self.canvas.pack(fill=BOTH, expand=1)
        
        self.fset = 2

    def preview_C(self):
    
        self.var_st_X.set(0.00)
        self.var_st_Z.set(0.00)
        self.var_Ch.set(0.00)
        
        self.nb.hide(0)
        self.nb.hide(1)
        self.nb.hide(2)
        self.nb.hide(3)
        self.nb.hide(5)
        self.nb.hide(6)
               
        self.x = self.x_old  
        self.z = self.z_old 

        self.canvas.pack(fill=BOTH, expand=1)
        
        self.fset = 3

    def selection_cycle(self):
        pass
        
    # если переключили G2<==>G3   
    def ch_rad(self): 
        self.cb1.config(state="disabled")
        self.b_added4.config(state="disabled")
        
    def restart(self):
        self.nb.select(self.nb_f1)
        self.canvas.delete("all")
        self.textbox.text_delete_entries()
        
        self.x_old = 0
        self.z_old = 0

        self.A=[]  

    def grid(self):
        self.canvas.create_line(25,25,25,475, width=2,)     
        self.canvas.create_line(25,25,645,25, width=2,)     
        self.canvas.create_line(645,25,645,475, width=2,) 
        self.canvas.create_line(25,475,645,475, width=2,) 
        
        h_f = 0
        w_f = 0
        while w_f<650:
            self.canvas.create_line(w_f,475,w_f,480, width=1,)
            w_f += 25
        while h_f<500:
            self.canvas.create_line(25,h_f,22,h_f, width=1,)
            h_f += 25
                                           
        self.canvas.create_text(322,487,text="0",font="Verdana 7",anchor="w",justify=CENTER,)
        self.canvas.create_text(211,487,text="-100",font="Verdana 7",anchor="w",justify=CENTER,) 
        self.canvas.create_text(415,487,text="100",font="Verdana 7",anchor="w",justify=CENTER,) 

        self.canvas.create_text(12,250,text="0",font="Verdana 7",anchor="w",justify=CENTER,)
        self.canvas.create_text(1,150,text="-100",font="Verdana 7",anchor="w",justify=CENTER,) 
        self.canvas.create_text(1,350,text="100",font="Verdana 7",anchor="w",justify=CENTER,) 
        
        self.canvas.create_line(35,415,75,415, width=1,arrow=LAST)
        self.canvas.create_line(35,415,35,455, width=1,arrow=LAST) 
        self.canvas.create_text(75,416,text="Z",font="Verdana 8",anchor="w",justify=CENTER,) 
        self.canvas.create_text(32,460,text="X",font="Verdana 8",anchor="w",justify=CENTER,) 
        
          
    def Write_GCode(self):
        
        tempfile_rw = 'tempfile_rw.ngc'         
        editfile = 'editfilename.ngc'
        
        delete_e = open(editfile, "w")
        delete_e.write("")
        delete_e.close()       
        
        outlog = open(editfile, "a")
        edit_readline = open(tempfile_rw, "r")
        for ew in edit_readline:
            outlog.write(ew )
            
        outlog.write("M2")
        outlog.close()
        edit_readline.close() 
        
        readline = open(tempfile_rw, "r")    
        for w in readline:
            ln = re.sub("^\s+|\n|\r|\s+$",'',w ) 
            print ln       
        print'M2'
        readline.close()
                
        delete_t = open(tempfile_rw, "w")
        delete_t.write("")
        delete_t.close()
        
        self.ende()  
    
        
    def page_make_gcode(self):
       
        rf1=Frame(self.f6,relief = GROOVE,bd = 2)
        rf1.grid(row=0,column=0,padx=2,pady=2,sticky=N+W+E)
        rf2=Frame(self.f6,relief = GROOVE,bd = 2)
        rf2.grid(row=1,column=0,padx=2,pady=2,sticky=N+W+E)
        rf3=Frame(self.f6,relief = GROOVE,bd = 2)
        rf3.grid(row=2,column=0,padx=2,pady=2,sticky=N+W+E)
        rf4=Frame(self.f6,relief = GROOVE,bd = 2)
        rf4.grid(row=3,column=0,padx=2,pady=2,sticky=N+W+E)
        rf5=Frame(self.f6,relief = GROOVE,bd = 2)
        rf5.grid(row=4,column=0,padx=2,pady=2,sticky=N+W+E) 
        rf6=Frame(self.f6,relief = GROOVE,bd = 2)
        rf6.grid(row=5,column=0,padx=2,pady=2,sticky=N+W+E)                
            
        rf1.columnconfigure(0,weight=1)
        rf2.columnconfigure(0,weight=1)
        rf3.columnconfigure(0,weight=1) 
        rf4.columnconfigure(0,weight=1)   
        rf5.columnconfigure(0,weight=1)  
        rf6.columnconfigure(0,weight=1)               
#########################################################################################параметры в окне 
        self.depth_D=DoubleVar()
        self.depth_D.set(1)
        
        self.finishing_depth=DoubleVar()
        self.finishing_depth.set(0.1)        

        self.quantity_I=DoubleVar()
        self.quantity_I.set(1)
        
        self.feedrate_F=DoubleVar()
        self.feedrate_F.set(1000)        
        
        self.reserve_S=DoubleVar()
        self.reserve_S.set(500)
                
        self.tool_T=DoubleVar()
        self.tool_T.set(01) 
        
        self.reserve_L=DoubleVar()
        self.reserve_L.set(0)       
             
        Label(rf1, text="Depth of cut   [D]")\
                .grid(row=0,column=0,sticky=N+W,padx=4)
        self.d_D = Entry(rf1,width=7,textvariable=self.depth_D)
        self.d_D.grid(row=0,column=1,sticky=N+E)
             
        Label(rf1, text="Finishing(depth)      [K]")\
                .grid(row=1,column=0,sticky=N+W,padx=4)
        self.d_K = Entry(rf1,width=7,textvariable=self.finishing_depth)
        self.d_K.grid(row=1,column=1,sticky=N+E)        

        Label(rf1, text=("Quantity      [I]" ))\
                .grid(row=2,column=0,sticky=N+W,padx=4)
        self.d_I = Entry(rf1,width=7,textvariable=self.quantity_I)
        self.d_I.grid(row=2,column=1,sticky=N+E)
        

        Label(rf2, text=("Feedrate   [F]"))\
                .grid(row=0,column=0,sticky=N+W,padx=4)
        self.d_F = Entry(rf2,width=7,textvariable=self.feedrate_F)
        self.d_F.grid(row=0,column=1,sticky=N+E)

        
        Label(rf2, text=("reserve  [S]" ))\
                .grid(row=1,column=0,sticky=N+W,padx=4)
        self.d_S = Entry(rf2,width=7,textvariable=self.reserve_S)
        self.d_S.grid(row=1,column=1,sticky=N+E)

        Label(rf2, text=("Tool  [T]" ))\
                .grid(row=2,column=0,sticky=N+W,padx=4)
        self.d_T = Entry(rf2,width=7,textvariable=self.tool_T)
        self.d_T.grid(row=2,column=1,sticky=N+E)


        Label(rf2, text=("reserve  [L]" ))\
                .grid(row=3,column=0,sticky=N+W,padx=4)
        self.d_L = Entry(rf2,width=7,textvariable=self.reserve_L)  
        self.d_L.grid(row=3,column=1,sticky=N+E)

                               
        self.g71_72=IntVar()
        self.g71_72.set(0)
        self.ssp=IntVar()
        self.ssp.set(0)
        self.show_blank=IntVar()
        self.show_blank.set(1)
        
        Label(rf3, text=("G71" ))\
        .grid(row=3,column=0,sticky=N+W,padx=4)
        self.rad0 = Radiobutton(rf3,text="G71",variable=self.g71_72,value=0 ,command=None)
        self.rad0.grid(row=3,column=1,sticky=N+E)
        
        Label(rf3, text=("G70" ))\
        .grid(row=4,column=0,sticky=N+W,padx=4)        
        self.rad1 = Radiobutton(rf3,text="G70",variable=self.g71_72,value=1,command=None)
        self.rad1.grid(row=4,column=1,sticky=N+E)
        
        Label(rf3, text=("G72" ))\
        .grid(row=5,column=0,sticky=N+W,padx=4)
        self.rad2 = Radiobutton(rf3,text="G72",variable=self.g71_72,value=2 ,command=None)
        self.rad2.grid(row=5,column=1,sticky=N+E)
        
        Label(rf3, text=("G73" ))\
        .grid(row=6,column=0,sticky=N+W,padx=4)        
        self.rad3 = Radiobutton(rf3,text="G73",variable=self.g71_72,value=3,command=None)
        self.rad3.grid(row=6,column=1,sticky=N+E)
        
        self.Igl = StringVar()        

        self.b_D_out=DoubleVar()
        self.b_D_out.set(40)
        
        self.b_L=DoubleVar()
        self.b_L.set(150)        
        
        self.b_D_in=DoubleVar()
        self.b_D_in.set(0)
                
        self.start_X0=DoubleVar()
        self.start_X0.set(0) 
        
        self.start_Z0=DoubleVar()
        self.start_Z0.set(0) 

        self.rad4 = Radiobutton(rf3,text="MDI",variable=self.g71_72,value=4,command=None)
        self.rad4.grid(row=7,column=1,sticky=N+E)
        self.Igl = Entry(rf3,width=16,textvariable=self.Igl)
        self.Igl.grid(row=7,columnspan=1,sticky=W) 

        Label(rf4, text=("Show blank" ))\
        .grid(row=0,column=0,sticky=N+W,padx=4)        
        self.rad3 = Checkbutton(rf4,text="",variable=self.show_blank,onvalue=1,offvalue=0)
        self.rad3.grid(row=0,column=1,sticky=N+E)        
        
        Label(rf4, text="D blank outside")\
        .grid(row=1,column=0,sticky=N+W,padx=4)
        self.D_out = Entry(rf4,width=7,textvariable=self.b_D_out)
        self.D_out.grid(row=1,column=1,sticky=N+E)
             
        Label(rf4, text="Lenght blank")\
        .grid(row=2,column=0,sticky=N+W,padx=4)
        self.Lg = Entry(rf4,width=7,textvariable=self.b_L)
        self.Lg.grid(row=2,column=1,sticky=N+E)        

        Label(rf4, text=("d blank  inside" ))\
        .grid(row=3,column=0,sticky=N+W,padx=4)
        self.D_in = Entry(rf4,width=7,textvariable=self.b_D_in)
        self.D_in.grid(row=3,column=1,sticky=N+E)
        


        Label(rf5, text=("Set start point" ))\
        .grid(row=0,column=0,sticky=N+W,padx=4)        
        self.rad5 = Checkbutton(rf5,text="",variable=self.ssp,onvalue=1,offvalue=0)
        self.rad5.grid(row=0,column=1,sticky=N+E)
                
        Label(rf5, text=("Start_X [X0] "))\
                .grid(row=1,column=0,sticky=N+W,padx=4)
        self.d_X0 = Entry(rf5,width=7,textvariable=self.start_X0)
        self.d_X0.grid(row=1,column=1,sticky=N+E)

        Label(rf5, text=("Start_Z  [Z0]"))\
                .grid(row=2,column=0,sticky=N+W,padx=4)
        self.d_Z0 = Entry(rf5,width=7,textvariable=self.start_Z0)
        self.d_Z0.grid(row=2,column=1,sticky=N+E)

        
        self.cancelR = Button(self.f6,command=self.cancel)
        self.cancelR.grid(row=6,column=0)

        self.im = PhotoImage(file='images/cancel.gif')
        self.cancelR.config(image=self.im)
        self.cancelR.im = self.im 


        self.bt1 = Button(rf6, text="Added",command=self.selection_cycle)
        self.bt1.grid(row=0,column=0,sticky=W)
        self.bt2 = Button(rf6, text="Write",command=self.Write_GCode)
        self.bt2.grid(row=0,column=1,sticky=E)

################################################################################вывод программы
    def Add_to_File_G71(self):
        string = self.string
        save_file = 'tempfile_gcode.ngc'
        f = open(save_file, "w")
        f.write(string)
        f.close()
        
        f = open(save_file, "r")  
        lines = f.readlines()
        f.close()
        ch = '' 
        ch1 = ''
        program = ''
        x_max, p, q, d, k, i, f, j, s, l, t = 0, 1, 15, 1.5, 0.3, 1, 433, 0, 0, 1, 0101
        Dtr, Lng, Prk = 0, 0, 0
        N_start_end = []
        Z_start = []
        for l in lines:
            if  re.search("[^\(\)\.\-\+NGZXRIK\d\s]",l.upper()):
                l=str(re.sub("^\s+|\n|\r|\s+$", '', l.upper(),re.I))
                ch1 +=l
                ch1 +='\n'
            elif  re.search("G\s*([0-3.]+)", l.upper() ,re.I):
                if not  re.search("[^\(\)\.\-\+NGZXRIK\d\s]",l.upper()):
                    l=re.sub("^\s+|\n|\r|\s+$", '', l.upper(),re.I)
                    ch +='('
                    ch +=l
                    ch +=')'
                    ch +='\n'
                    p1 = N_start_end.append(int(re.search("N\s*([-0-9.]+)",l.upper(), re.I).group(1)))
                    z_st = Z_start.append(float(re.search("Z\s*([-0-9.]+)",l.upper(), re.I).group(1)))
                    x_max_sr = float(re.search("X\s*([-0-9.]+)",l.upper(), re.I).group(1))
                    if x_max_sr > x_max:
                        x_max = x_max_sr
                    z_max = float(re.search("Z\s*([-0-9.]+)",l.upper(), re.I).group(1))
                        
        p = N_start_end[0]
        q = N_start_end[-1]
        z0 = Z_start[0]
        d = float(self.d_D.get())
        k = float(self.d_K.get())
        i = float(self.d_I.get())
        f = float(self.d_F.get())
        s = float(self.d_S.get())
        l = float(self.d_L.get())
        t = str(self.d_T.get())
        rb = self.g71_72.get()
        sx = float(self.d_X0.get())
        sz = float(self.d_Z0.get())

        Dtr = float(self.D_out.get())
        Lng = float(self.Lg.get())
        Prk = float(self.D_in.get())
        chb_ssp = self.ssp.get()
        show_blank = self.show_blank.get()
        code = 'G71'
        start_point = str('G1 X%s  Z%s \n' % (x_max, z0))
        if chb_ssp :
            start_point = str('G1 X%s  Z%s \n' % (sx, sz))           
        program += ch1
        blank = str('(AXIS,blank,%s,%s,%s)\n' % (Dtr, Lng, Prk))
        if show_blank :
            program += blank
        program += start_point
        stt = str('%s P%s Q%s  D%s K%s I%s F%s J%s S%s L%s \n' % (code,p,q,d,k,i,f,j,s,l,))

        program += stt

        if self.no_add_lines == 0: #выводим в программу строки контура(один раз)
            program += ch
                       
        tempfile_rw = 'tempfile_rw.ngc'
        rw = open(tempfile_rw, "a")
        rw.write(program)
        rw.close()
        self.no_add_lines = 1
        
    def Add_to_File_G70(self):
    
        string = self.string
        save_file = 'tempfile_gcode.ngc'
        f = open(save_file, "w")
        f.write(string)
        f.close()
        
        f = open(save_file, "r")  
        lines = f.readlines()
        f.close()
        ch = '' 
        ch1 = ''
        program = ''
        x_max, p, q, d, k, i, f, j, s, l, t = 0, 1, 15, 1.5, 0.3, 1, 433, 0, 0, 1, 0101
        Dtr, Lng, Prk = 0, 0, 0
        N_start_end = []
        Z_start = []
        for l in lines:
            if  re.search("[^\(\)\.\-\+NGZXRIK\d\s]",l.upper()):
                l=str(re.sub("^\s+|\n|\r|\s+$", '', l.upper(),re.I))
                ch1 +=l
                ch1 +='\n'
            elif  re.search("G\s*([0-3.]+)", l.upper() ,re.I):
                if not  re.search("[^\(\)\.\-\+NGZXRIK\d\s]",l.upper()):
                    l=re.sub("^\s+|\n|\r|\s+$", '', l.upper(),re.I)
                    ch +='('
                    ch +=l
                    ch +=')'
                    ch +='\n'
                    p1 = N_start_end.append(int(re.search("N\s*([-0-9.]+)",l.upper(), re.I).group(1)))
                    z_st = Z_start.append(float(re.search("Z\s*([-0-9.]+)",l.upper(), re.I).group(1)))
                    x_max_sr = float(re.search("X\s*([-0-9.]+)",l.upper(), re.I).group(1))
                    if x_max_sr > x_max:
                        x_max = x_max_sr + 5
                    z_max = float(re.search("Z\s*([-0-9.]+)",l.upper(), re.I).group(1))
                    
        d = float(self.d_D.get())                
        p = N_start_end[0]
        q = N_start_end[-1]
        code = 'G70'
        s_fin = str('%s P%s Q%s F%s D%s  \n' % (code,p,q,f,d))
        tempfile_rw = 'tempfile_rw.ngc'
        rw = open(tempfile_rw, "a")
        program += s_fin
        if self.no_add_lines == 0 : #выводим в программу строки контура(один раз)
            program += ch
        rw.write(program)        
        rw.close()
        self.no_add_lines = 1
        
    def Add_to_File_G73(self):
    
        string = self.string
        save_file = 'tempfile_gcode.ngc'
        f = open(save_file, "w")
        f.write(string)
        f.close()
        
        f = open(save_file, "r")  
        lines = f.readlines()
        f.close()
        ch = '' 
        ch1 = ''
        program = ''
        x_max, p, q, d, k, i, f, j, s, l, t = 0, 1, 15, 1.5, 0.3, 1, 433, 0, 0, 1, 0101
        Dtr, Lng, Prk = 0, 0, 0
        N_start_end = []
        Z_start = []
        for l in lines:
            if  re.search("[^\(\)\.\-\+NGZXRIK\d\s]",l.upper()):
                l=str(re.sub("^\s+|\n|\r|\s+$", '', l.upper(),re.I))
                ch1 +=l
                ch1 +='\n'
            elif  re.search("G\s*([0-3.]+)", l.upper() ,re.I):
                if not  re.search("[^\(\)\.\-\+NGZXRIK\d\s]",l.upper()):
                    l=re.sub("^\s+|\n|\r|\s+$", '', l.upper(),re.I)
                    ch +='('
                    ch +=l
                    ch +=')'
                    ch +='\n'
                    p1 = N_start_end.append(int(re.search("N\s*([-0-9.]+)",l.upper(), re.I).group(1)))
                    z_st = Z_start.append(float(re.search("Z\s*([-0-9.]+)",l.upper(), re.I).group(1)))
                    x_max_sr = float(re.search("X\s*([-0-9.]+)",l.upper(), re.I).group(1))
                    if x_max_sr > x_max:
                        x_max = x_max_sr + 5
                    z_max = float(re.search("Z\s*([-0-9.]+)",l.upper(), re.I).group(1))
                        
        p = N_start_end[0]
        q = N_start_end[-1]
        z0 = Z_start[0]
        d = float(self.d_D.get())
        k = float(self.d_K.get())
        i = float(self.d_I.get())
        f = float(self.d_F.get())
        s = float(self.d_S.get())
        l = float(self.d_L.get())
        t = str(self.d_T.get())
        rb = self.g71_72.get()

        Dtr = float(self.D_out.get())
        Lng = float(self.Lg.get())
        Prk = float(self.D_in.get())
        checkbutton = self.ssp.get()
        show_blank = self.show_blank.get()
        code = 'G73.3'
        start_point = str('G1 X%s  Z%s \n' % (x_max, z0))
        if checkbutton :
            j = 1           
        program += ch1
        blank = str('(AXIS,blank,%s,%s,%s)\n' % (Dtr, Lng, Prk))
        if show_blank :
            program += blank
        program += start_point
        stt = str('%s P%s Q%s  D%s K%s I%s F%s J%s S%s  \n' % (code,p,q,d,k,i,f,j,s,))

        program += stt

        if self.no_add_lines == 0: #выводим в программу строки контура(один раз)
            program += ch
                       
        tempfile_rw = 'tempfile_rw.ngc'
        rw = open(tempfile_rw, "a")
        rw.write(program)
        rw.close()
        self.no_add_lines = 1           

    def Add_to_File_G72(self):
        string = self.string
        save_file = 'tempfile_gcode.ngc'
        f = open(save_file, "w")
        f.write(string)
        f.close()
        
        f = open(save_file, "r")  
        lines = f.readlines()
        f.close()
        ch = '' 
        ch1 = ''
        program = ''
        x_max, p, q, d, k, i, f, j, s, l, t = 0, 1, 15, 1.5, 0.3, 1, 433, 0, 0, 1, 0101
        Dtr, Lng, Prk = 0, 0, 0
        N_start_end = []
        Z_start = []
        for l in lines:
            if  re.search("[^\(\)\.\-\+NGZXRIK\d\s]",l.upper()):
                l=str(re.sub("^\s+|\n|\r|\s+$", '', l.upper(),re.I))
                ch1 +=l
                ch1 +='\n'
            elif  re.search("G\s*([0-3.]+)", l.upper() ,re.I):
                if not  re.search("[^\(\)\.\-\+NGZXRIK\d\s]",l.upper()):
                    l=re.sub("^\s+|\n|\r|\s+$", '', l.upper(),re.I)
                    ch +='('
                    ch +=l
                    ch +=')'
                    ch +='\n'
                    p1 = N_start_end.append(int(re.search("N\s*([-0-9.]+)",l.upper(), re.I).group(1)))
                    z_st = Z_start.append(float(re.search("Z\s*([-0-9.]+)",l.upper(), re.I).group(1)))
                    x_max_sr = float(re.search("X\s*([-0-9.]+)",l.upper(), re.I).group(1))
                    if x_max_sr > x_max:
                        x_max = x_max_sr
                    z_max = float(re.search("Z\s*([-0-9.]+)",l.upper(), re.I).group(1))
                        
        p = N_start_end[0]
        q = N_start_end[-1]
        z0 = Z_start[0]
        d = float(self.d_D.get())
        k = float(self.d_K.get())
        i = float(self.d_I.get())
        f = float(self.d_F.get())
        s = float(self.d_S.get())
        l = float(self.d_L.get())
        t = str(self.d_T.get())
        rb = self.g71_72.get()
        sx = float(self.d_X0.get())
        sz = float(self.d_Z0.get())

        Dtr = float(self.D_out.get())
        Lng = float(self.Lg.get())
        Prk = float(self.D_in.get())
        chb_ssp = self.ssp.get()
        show_blank = self.show_blank.get()
        code = 'G72'
        start_point = str('G1 X%s  Z%s \n' % (x_max, z0))
        if chb_ssp :
            start_point = str('G1 X%s  Z%s \n' % (sx, sz))           
        program += ch1
        blank = str('(AXIS,blank,%s,%s,%s)\n' % (Dtr, Lng, Prk))
        if show_blank :
            program += blank
        program += start_point
        stt = str('%s P%s Q%s  D%s K%s I%s F%s J%s S%s L%s \n' % (code,p,q,d,k,i,f,j,s,l,))

        program += stt

        if self.no_add_lines == 0: #выводим в программу строки контура(один раз)
            program += ch
                       
        tempfile_rw = 'tempfile_rw.ngc'
        rw = open(tempfile_rw, "a")
        rw.write(program)
        rw.close()
        self.no_add_lines = 1
        
    def insert_gcode_line(self):
        tempfile_rw = 'tempfile_rw.ngc'
        ln = str(self.Igl.get())
        rw = open(tempfile_rw, "a")
        program = ''
        
        program += ln
        program += '\n'
        rw.write(program)        
        rw.close()        
                        
    def selection_cycle(self):
         rb = self.g71_72.get()
         if   rb==0:
             return self.Add_to_File_G71()
         elif rb==1:
             return  self.Add_to_File_G70()
         elif rb==2:
             return  self.Add_to_File_G72()
         elif rb==3:
             return  self.Add_to_File_G73()             
         elif rb==4:
             return  self.insert_gcode_line() 
    def ende(self):
        self.master.destroy()
        self.master.quit()
         
    def insc_arc_arc(self,x1,z1,x2,z2,r):        

        r1=r
        r2=r
        d=sqrt( pow(abs(x1-x2),2) + pow(abs(z1-z2),2))
        if(d > r1+r2): 
            #print 'do not intersect'
            return
        a= (r1*r1 - r2*r2 + d*d ) / (2*d)
        h= sqrt( pow(r1,2) - pow(a,2))

        x0 = x1 + a*( x2 - x1 ) / d
        z0 = z1 + a*( z2 - z1 ) / d

        ix1= x0 + h*( z2 - z1 ) / d
        iz1= z0 - h*( x2 - x1 ) / d

        if(a == r1 ) :
            #print 'сircles touch'
            return

        ix2= x0 - h*( z2 - z1 ) / d
        iz2= z0 + h*( x2 - x1 ) / d

        return ix1, iz1, ix2, iz2
        
                               
class TextboxClass:
    def __init__(self,frame=None,master=None,DEBUG=0):
            
        self.DEBUG=DEBUG
        self.master=master
        self.text = Text(frame,height=7)
        
        self.textscr = Scrollbar(frame)
        self.text.grid(row=0,column=0,pady=4,sticky=E+W)
        self.textscr.grid(row=0,column=1,pady=4,sticky=N+S)
        frame.columnconfigure(0,weight=1)
        frame.columnconfigure(1,weight=0)        

        self.text.bind("<Button-3>", self.text_contextmenu)
        self.textscr.config(command=self.text.yview)
        self.text.config(yscrollcommand=self.textscr.set)

    def set_debuglevel(self,DEBUG=0):
        self.DEBUG=DEBUG
        if DEBUG:
            self.text.config(height=15)

    def prt(self,txt='',DEBUGLEVEL=0):

        if self.DEBUG>=DEBUGLEVEL:
            self.text.insert(END,txt)
            self.text.yview(END)
            self.master.update_idletasks()
            
    def text_contextmenu(self,event):        
        popup = Menu(self.text,tearoff=0)        
        popup.add_command(label='Delete text entries',command=self.text_delete_entries)
        popup.post(event.x_root, event.y_root)
        
    def text_delete_entries(self):
        self.text.delete(1.0,END)
        self.text.yview(END) 
        

 
def main():  
    master = Tk()
    master.title("Contour Editor")
    ui = UI(master)
    master.geometry("900x670+200+200")
    master.mainloop()  
if __name__ == '__main__':
    main()  
