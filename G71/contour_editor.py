#!/usr/bin/python
# --*-- coding:utf-8 --*--

from Tkconstants import END, INSERT, ALL, N, S, E, W, RAISED, RIDGE, GROOVE, FLAT, DISABLED, NORMAL, ACTIVE, LEFT

from Tkinter import *
from ttk import Notebook

class UI(Frame):
  
    def __init__(self, master):
        Frame.__init__(self, master)   
        
        self.master = master 
                
        self.frame_c=Frame(master) 
        self.frame_c.grid(row=0,column=1,)

        self.frame_l=Frame(master,relief = RIDGE,)
        self.frame_l.grid(row=0,column=0,padx=4,pady=4,sticky=N+E+S+W)

        self.frame_r=Frame(master,relief = RIDGE,)
        self.frame_r.grid(row=0,column=2,padx=4,pady=4,sticky=N+E+S+W)        

        self.frame_r1=Frame(master,relief = RIDGE,)
        #self.frame_r1.grid(row=0,column=3,padx=4,pady=4,sticky=N+E+S+W) 

        self.frame_d=Frame(master) 
        self.frame_d.grid(row=1,column=1,padx=4,sticky=E+S+W)

        self.textbox=TextboxClass(frame=self.frame_d,master=self.master)       
        
#######################################################################
        self.nb = Notebook(self.frame_r)

        self.nb_f1 = Frame(self.nb)
        self.nb_f2 = Frame(self.nb)
        self.nb_f3 = Frame(self.nb)
        self.nb_f4 = Frame(self.nb)
        
        self.nb.add(self.nb_f1,)
        self.nb.add(self.nb_f2,)
        self.nb.add(self.nb_f3,)
        self.nb.add(self.nb_f4,)
        self.nb.pack()
       
        f1=Frame(self.nb_f1,relief = GROOVE,)
        f1.grid(row=0,column=0,padx=2,pady=2,sticky=N+W+E)
        f2=Frame(self.nb_f2,relief = GROOVE,)
        f2.grid(row=1,column=0,padx=2,pady=2,sticky=N+W+E)
        f3=Frame(self.nb_f3,relief = GROOVE,)
        f3.grid(row=2,column=0,padx=2,pady=2,sticky=N+W+E)
        f4=Frame(self.nb_f4,relief = GROOVE,)
        f4.grid(row=3,column=0,padx=2,pady=2,sticky=N+W+E)        
        
    
        f1.columnconfigure(0,weight=1)
        f2.columnconfigure(0,weight=1)
        f3.columnconfigure(0,weight=1)
        f4.columnconfigure(0,weight=1)        
                
        self.var_st_X = DoubleVar()
        self.var_st_X.set(float(0))
        self.var_st_Z = DoubleVar()
        self.var_st_Z.set(float(0))
        self.var_Ch = DoubleVar()
        self.var_Ch.set(float(0))                

        self.b_v = Button(f1,command=self.preview_G)
        self.b_v.grid(row=0)

        self.im = PhotoImage(file='images/up.gif')
        self.b_v.config(image=self.im)
        self.b_v.im = self.im

        self.b_g = Button(f1,command=self.preview_V)
        self.b_g.grid(row=1)

        self.im = PhotoImage(file='images/down.gif')
        self.b_g.config(image=self.im)
        self.b_g.im = self.im

        self.b_g = Button(f1,command=self.preview_N)
        self.b_g.grid(row=2)

        self.im = PhotoImage(file='images/down.gif')
        self.b_g.config(image=self.im)
        self.b_g.im = self.im
 #------------------------------------------------------V                    
        Label(f3, text="Next point   X")\
                .grid(row=0,column=0,sticky=N+W,padx=4)
        self.st_X = Entry(f3,width=7,textvariable=self.var_st_X)
        self.st_X.grid(row=0,column=1,sticky=N+E)

        Label(f3, text=("Chamfer"))\
                .grid(row=1,column=0,sticky=N+W,padx=4)
        self.Ch = Entry(f3,width=7,textvariable=self.var_Ch)
        self.Ch.grid(row=1,column=1,sticky=N+E)


        self.var_st_Z = DoubleVar()
        self.var_st_Z.set(float(0))
 
        self.b_added1 = Button(f3,command=self.draw_line)
        self.b_added1.grid(row=2,column=2)

        self.im = PhotoImage(file='images/tool_run.gif')
        self.b_added1.config(image=self.im)
        self.b_added1.im = self.im   
        
        
        self.abs_inc = IntVar()
        self.abs_inc.set(0)
        self.rad1v = Radiobutton(f3,text="abs",variable=self.abs_inc,value=0 )
        self.rad1v.grid(row=0,column=2)
        self.rad2v = Radiobutton(f3,text="inc",variable=self.abs_inc,value=1 )
        self.rad2v.grid(row=1,column=2)

        self.cancelV = Button(f3,command=self.cancel)
        self.cancelV.grid(row=3,column=2)

        self.im = PhotoImage(file='images/tool_estop.gif')
        self.cancelV.config(image=self.im)
        self.cancelV.im = self.im                     
 #----------------------------------------------------------- G           
        Label(f2, text="Next point   Z")\
                .grid(row=0,column=0,sticky=N+W,padx=4)
        self.st_Z = Entry(f2,width=7,textvariable=self.var_st_Z)
        self.st_Z.grid(row=0,column=1,sticky=N+E)       

        Label(f2, text=("Chamfer"))\
                .grid(row=1,column=0,sticky=N+W,padx=4)
        self.Ch2 = Entry(f2,width=7,textvariable=self.var_Ch)
        self.Ch2.grid(row=1,column=1,sticky=N+E)
        
        self.b_added2 = Button(f2,command=self.draw_line)
        self.b_added2.grid(row=2,column=2)

        self.im = PhotoImage(file='images/tool_run.gif')
        self.b_added2.config(image=self.im)
        self.b_added2.im = self.im 
        

        self.rad1g = Radiobutton(f2,text="abs",variable=self.abs_inc,value=0 )
        self.rad1g.grid(row=0,column=2)
        self.rad2g = Radiobutton(f2,text="inc",variable=self.abs_inc,value=1 )
        self.rad2g.grid(row=1,column=2) 
        
        self.cancelG = Button(f2,command=self.cancel)
        self.cancelG.grid(row=3,column=2)

        self.im = PhotoImage(file='images/tool_estop.gif')
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

        self.im = PhotoImage(file='images/tool_run.gif')
        self.b_added3.config(image=self.im)
        self.b_added3.im = self.im

        self.rad1n = Radiobutton(f4,text="abs",variable=self.abs_inc,value=0 )
        self.rad1n.grid(row=0,column=2)
        self.rad2n = Radiobutton(f4,text="inc",variable=self.abs_inc,value=1 )
        self.rad2n.grid(row=1,column=2) 
        
        self.cancelN = Button(f4,command=self.cancel)
        self.cancelN.grid(row=3,column=2)

        self.im = PhotoImage(file='images/tool_estop.gif')
        self.cancelN.config(image=self.im)
        self.cancelN.im = self.im 
        
#--------------------------------------------------  
               
        self.canvas=Canvas(self.frame_c,width=650,height=500,bg="red")
        self.canvas.grid(row=0,column=0,sticky=N+E+S+W)
        self.canvas.config(background="#D4DDE3",bd=2)
        
        if self.abs_inc.get():
            self.x = 250
            self.z = 325 
        else:
            self.x = 0
            self.z = 0               
        self.x_old = 250
        self.z_old = 325
        
    def cancel(self):
    
        self.nb.add(self.nb_f1)
        self.nb.add(self.nb_f2)
        self.nb.add(self.nb_f3)
        self.nb.add(self.nb_f4)
        self.nb.select(self.nb_f1)
        self.canvas.delete(self.pv)
        
    def chamfer(self):

        self.x = self.x_old + float(self.var_Ch.get()) 
        self.z = self.z_old - float(self.var_Ch.get()) 
                        
        self.canvas.create_line(self.z_old,self.x_old,self.z,self.x, width=2,fill="blue",)
        self.x_old = self.x
        self.z_old = self.z
        
        self.canvas.pack(fill=BOTH, expand=1) 
                        
    def draw_line(self):
    
        self.nb.add(self.nb_f1)
        self.nb.add(self.nb_f2)
        self.nb.add(self.nb_f3)
        self.nb.add(self.nb_f4)
        self.nb.select(self.nb_f1)
        
        if self.fset==1: #флаг ,показывает после какой функции выбора сработали
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
                                        
        self.canvas.create_line(self.z_old,self.x_old,self.z,self.x, width=2,fill="blue",)
        self.x_old = self.x
        self.z_old = self.z
        
        self.canvas.pack(fill=BOTH, expand=1)
        self.canvas.delete(self.pv)
        
        if float(self.var_Ch.get()):
            self.chamfer()        
                     
    def preview_G(self):
    
        self.var_st_Z.set(0.00)
        self.var_st_X.set(0.00)
        self.var_Ch.set(0.00)
                
        self.nb.hide(0)
        self.nb.hide(2)
        self.x = self.x_old  
        self.z = self.z_old 
        self.pv = self.canvas.create_line(0,self.x,650,self.x,width=1,fill="blue",stipple="gray50")        

        self.canvas.pack(fill=BOTH, expand=1)

        self.fset = 1
        
    def preview_V(self):
    
        self.var_st_X.set(0.00)
        self.var_st_Z.set(0.00)
        self.var_Ch.set(0.00)
        
        self.nb.hide(1)
        self.nb.hide(0)
        self.x = self.x_old  
        self.z = self.z_old 
        self.pv = self.canvas.create_line(self.z,0,self.z,500,width=1,fill="blue",stipple="gray50")        

        self.canvas.pack(fill=BOTH, expand=1)

        self.fset = 0
        
    def preview_N(self):
    
        self.var_st_X.set(0.00)
        self.var_st_Z.set(0.00)
        self.var_Ch.set(0.00)
            
        self.nb.hide(1)
        self.nb.hide(0)
        self.nb.hide(2)
        self.x = self.x_old  
        self.z = self.z_old 
        self.pv = self.canvas.create_line(self.z,self.x,0,500,width=1,fill="blue",stipple="gray50")        

        print "N.x=",self.x,"N.z=",self.z
        print "N.x_old=",self.x_old,"N.z_old=",self.z_old
        print "\n"
        self.canvas.pack(fill=BOTH, expand=1)
        
        self.fset = 2
                        
class TextboxClass:
    def __init__(self,frame=None,master=None):
            

        self.master=master
        self.text = Text(frame,height=5)
        
        self.textscr = Scrollbar(frame)
        self.text.grid(row=0,column=0,pady=4,sticky=E+W)
        self.textscr.grid(row=0,column=1,pady=4,sticky=N+S)
        frame.columnconfigure(0,weight=1)
        frame.columnconfigure(1,weight=0)

def main():  
    master = Tk()
    master.title("Contour Editor")
    ui = UI(master)
    master.geometry("900x550+200+200")
    master.mainloop()  
if __name__ == '__main__':
    main()  
