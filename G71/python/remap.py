# --*-- coding:utf-8 --*--
import linuxcnc
import re
import os
from math import *
import traceback
from interpreter import *
from emccanon import MESSAGE
import subprocess
import select
from itertools import chain
import time

throw_exceptions = 1 # raises InterpreterException if execute() or read() fail

dir_ini = str(os.getcwd())
all_files = os.listdir(os.getcwd()) 
n_ini = filter(lambda x: x.endswith('.ini'),all_files)
if len(n_ini)>1 : print 'ini file > 1'
f_ini = os.path.join(dir_ini, n_ini[0])
inifile = linuxcnc.ini(f_ini)
  
def pars(array,reg ,lines): 
    a=array.insert(0,(float(re.search(reg,lines, re.I).group(1))))
def cathetus(c,b):
    a = sqrt(abs(c*c - b*b))
    return a 
def hip(a,b):
    c = sqrt(abs(a*a + b*b))
    return c
    
def en_line_arc(G,stZ,endZ,stX,endX, Mz1,Mx1,Mz2,Mx2,centreZ,centreX,rad,A): 
    a=[]   
    b = -2*centreZ  
    c = -rad**2 + (Mx1-centreX)**2 + centreZ**2 
    D = b**2 - 4*c 
    if D < 0: 
      print 'D<0'
      return
    z1 = (-b-sqrt(D))/2 
    z2 = (-b+sqrt(D))/2
    hh=Mx1*2
    print  'D=' ,D
    if G==3:
        if 0:
          pointZ1 = z1   
          pointX1 = hh
          a.append(pointZ1)
          a.append(pointX1)
          A.append(a)
          return  
        else:
          print z2 , hh  , 'z2 ,hh'
          print stZ,endZ,stX,endX ,'stZ,endZ,stX,endX'
          if stZ > z2 > endZ and stX < hh < endX :
            pointZ1 = z2
            pointX1 = hh
            a.append(pointZ1)
            a.append(pointX1)
            A.append(a)
          return  
    if G==2:
        if 0:
          pointZ1 = z1   
          pointX1 = hh
          a.append(pointZ1)
          a.append(pointX1)
          A.append(a)
          return  
        else:
          if stZ > z1 > endZ and stX < hh < endX :
            pointZ1 = z1
            pointX1 = hh
            a.append(pointZ1)
            a.append(pointX1)
            A.append(a)
          return     
    
def en_line_arc(G,Mz1,Mx1,Mz2,Mx2,centreZ,centreX,rad):    
    if (Mz2-Mz1)!=0:
        K=(Mx2-Mx1)/(Mz2-Mz1)
        B=-(K*Mz1-Mx1)           
        a = 1 + K**2 
        b = -2*centreZ + 2*K*B -2*K*centreX  
        c = -rad**2 + (B-centreX)**2 + centreZ**2 
        D = b**2 - 4*a*c 
        if D < 0: 
          print 'D<0'
        if (2*a)!=0:
          try:   
            z1 = (-b-sqrt(D))/(2*a) 
            z2 = (-b+sqrt(D))/(2*a)
          except:
            pass
        if G==3:
            if Mz2 < z1 < Mz1:
              pointZ1 = z1   
              pointX1 = K*z1+B
              a.append(pointZ1)
              a.append(pointX1)
              A.append(a)
              return  
            else:
              pointZ1 = z2
              pointX1 = K*z2+B
              a.append(pointZ1)
              a.append(pointX1)
              A.append(a)
              return  
        if G==2:
            if Mz2 < z1 < Mz1:
              pointZ1 = z2 
              pointX1 = K*z2+B
              a.append(pointZ1)
              a.append(pointX1)
              A.append(a)
              return  
            else:
              pointZ1 = z1
              pointX1 = K*z1+B
              a.append(pointZ1)
              a.append(pointX1)
              A.append(a)              
              return 
                  
def intersection_line_arc(G,Mz1,Mx1,Mz2,Mx2,centreZ,centreX,rad):    
    if (Mz2-Mz1)!=0:
        K=(Mx2-Mx1)/(Mz2-Mz1)
        B=-(K*Mz1-Mx1)           
        a = 1 + K**2 
        b = -2*centreZ + 2*K*B -2*K*centreX  
        c = -rad**2 + (B-centreX)**2 + centreZ**2 
        D = b**2 - 4*a*c 
        if D < 0: 
          print 'D<0' 
        z1 = (-b-sqrt(D))/(2*a) 
        z2 = (-b+sqrt(D))/(2*a)
        if G==3:
            if Mz2 < z1 < Mz1:
              pointZ1 = z1   
              pointX1 = K*z1+B
              return  pointZ1,pointX1
            else:
              pointZ1 = z2
              pointX1 = K*z2+B
              return  pointZ1,pointX1
        if G==2:
            if Mz2 < z1 < Mz1:
              pointZ1 = z2 
              pointX1 = K*z2+B
              return  pointZ1,pointX1
            else:
              pointZ1 = z1
              pointX1 = K*z1+B
              return  pointZ1,pointX1 
             
def intersection_arc_arc(x1,z1,r1,x2,z2,r2,Px,Pz):
    d=sqrt( pow(abs(x1-x2),2) + pow(abs(z1-z2),2))
    if(d > r1+r2): 
        return
    a= (r1*r1 - r2*r2 + d*d ) / (2*d)
    h= sqrt( pow(r1,2) - pow(a,2))
    x0 = x1 + a*( x2 - x1 ) / d
    z0 = z1 + a*( z2 - z1 ) / d;
    ix1= x0 + h*( z2 - z1 ) / d
    iz1= z0 - h*( x2 - x1 ) / d
    ix2= x0 - h*( z2 - z1 ) / d
    iz2= z0 + h*( x2 - x1 ) / d
    if(a == r1 ) :
        intscX = ix2
        intscZ = iz2
        return intscX , intscZ 

    l1= sqrt((Px - ix1)**2+(Pz - iz1)**2)
    l2= sqrt((Px - ix2)**2+(Pz - iz2)**2)
    if l1>l2:
        intscX = ix2
        intscZ = iz2
    else:
       intscX = ix1
       intscZ = iz1              
    return  intscX , intscZ
     
def intersection_line_line( p1X, p1Z, p2X, p2Z ,p3X, p3Z, p4X, p4Z,A   ):
              
    p1X = p1X *(-0.5)        
    p2X = p2X *(-0.5)        
    p3X = p3X *(-1)       
    p4X = p4X *(-1) 
                      
    a = []

    if (p2X - p1X):    
        z = p1Z + ((p2Z - p1Z) * (p3X - p1X)) / (p2X - p1X)
    elif p2X==p3X:     
        #print p1Z, p1X, p2Z, p2X, 'горизонтальный отрезок z1,x1 z2,x2'
        a.append(p1Z)
        a.append(-p1X)
        A.append(a)
        a.append(p2Z)
        a.append(-p2X)
        A.append(a) 
        return
    else:
        #print  '?????'
        return

    if (z>max(p3Z,p4Z) or z<min(p3Z,p4Z) or z>max(p1Z,p2Z) or z<min(p1Z,p2Z)or p3X>max(p1X,p2X) or p3X<min(p1X,p2X)):
        #print 'нет пересечения'
        pass
    else:
        #print z, -p3X, 'Z, X'
        a.append(z)
        a.append(-p3X*2)
        A.append(a)                
        return a
                                      
def papp(n,G,x,z,old_x,old_z,App=[],r=None,xc=None,zc=None):
    App.append([])
    App[n].append(G)
    App[n].append(old_x*2)
    App[n].append(old_z)                                               
    App[n].append(x)
    App[n].append(z)
    if G>1:
        App[n].append(r)
        App[n].append(xc)
        App[n].append(zc)
    return App 
def prog(array,G,x,z,i=None,k=None):
    ser=' '
    string=ser.join(['G1','X',str(x),'Z',str(z)])
    if G==2: 
        string=ser.join(['G2','X',str(x),'Z',str(z),'I',str(i),'K',str(k)])
    if G==3: 
        string=ser.join(['G3','X',str(x),'Z',str(z),'I',str(i),'K',str(k)])        
    return array.append(string)                
#################################################-----G71.2
# Fanuc code:
# Programming
# G71 U... R...
# G71 P... Q... U... W... F... S...
# Parameters
#
# First blockParamete
# U	Depth of cut.
# R	Retract height.
#
#
# Second blockParameter	Description
# P	Contour start block number.
# Q	Contour end block number.
# U	Finishing allowance in x-axis.
# W	Finishing allowance in z-axis.
# F	Feedrate during G71 cycle.
# S	Spindle speed during G71 cycle.
#
def g710(self, **words):
    """ remap code G71.2 """
    p = int(words['p'])    
    q = int(words['q'])
    d = float(words['d'])
    offset = float(words['k'])
    
    if words.has_key('s'):
        sspeed = int(words['s'])
        self.execute("S%d" % (sspeed))
    if words.has_key('l'): #только int ???
        offset_StartZ = int(words['l']) 
    only_finishing_cut = 0    
    if words.has_key('j'):
        only_finishing_cut = int(words['j'])
    quantity = 1    
    if words.has_key('i'):
        quantity = int(words['i'])
    if words.has_key('t'):
        R_Fanuc = float(words['t'])

    if words.has_key('f'):    
        fr = float(words['f'])
        
    tfile  = "./rs.tbl"
    setline = open(tfile ,"w")
    offs = ' '.join(['\n','T1','P1','X0','Z0','D%s' % (str(offset/12.7))])
    setline.write(offs)
    setline.close() 
           
    s = linuxcnc.stat() 
    s.poll()
    filename = s.file
    f = open(filename, "r")
    lines = f.readlines()

    self.execute("G21 G18 G49 G40 G90 G61 G7 F1000")
    name_file = "./fgcode.ngc" 
    fgcode = open(name_file, "w") 
    string = 'G21 G18 G49 G40 G90 G61 G7 F1000 \n'
    string += 'T1 M6\n'
    string += 'G1 X-30 Z30\n'
    string += 'G42\n'             
    for w in lines:
        if  re.search("^\s*[(]\s*N\d", w.upper()):
            if not re.search("[^\(\)\.\-\+NGZXRIK\d\s]", w.upper()):
                num2 = int(re.findall("^\s*\d*",(re.split('N',w.upper())[1]))[0])
                if num2 >= p and num2 <= q:
                    try: 
                        contour=re.split('\)',(re.split('\(',w.upper())[1]))[0]
                        string += contour
                        string += '\n'
                    except InterpreterException,e:
                        msg = "%d: '%s' - %s" % (e.line_number,e.line_text, e.error_message)
                        self.set_errormsg(msg) 
                        return INTERP_ERROR                             
    f.close()
    string += 'G40\n'
    self.execute("G40")
    string += 'M30\n'
    fgcode.write(string)
    outfilename  = "./RS274_temp.txt"
    outfile = open(outfilename, "w")
    
    fgcode.close() 
    p = subprocess.Popen(["sh", "-c", (' '.join(['./rs274','-t',tfile,'-g',name_file,outfilename]))],
                      stdin=None,
                      stdout=outfile,
                      stderr=None )
    p.wait()                 
    outfile.close()
    P = []                      
    pr = []    
    f1 = open(outfilename, "r")
    ln = f1.readlines()
    old_posX = 0
    old_posZ = 0 
    i=-1   
    for w in ln:
        if  re.search("STRAIGHT_TRAVERSE", w.upper()):
            numbers = re.split('\(',w.upper())
            number = re.split('\,',numbers[1].upper())
            prog(pr,0,number[0],number[2])
            old_posX = float(number[0])
            old_posZ = float(number[2])             
        elif  re.search("STRAIGHT_FEED", w.upper()):
            numbers = re.split('\(',w.upper())
            number = re.split('\,',numbers[1].upper())
            x1=float(number[0])*2
            z1=float(number[2])
            prog(pr,1,x1,z1)
            i+=1
            papp(i,1,x1,z1,old_posX,old_posZ,P)
            old_posX = float(number[0])
            old_posZ = float(number[2])

        elif  re.search("ARC_FEED", w.upper()):
            numbers = re.split('\(',w.upper())
            number = re.split('\,',numbers[1].upper())
            if float(number[4])>0:
                g=3
            elif float(number[4])<0:
                g=2 
            x_arc=float(number[1])*2
            z_arc=float(number[0])
            arc_I = float(number[3]) - old_posX
            arc_K = float(number[2]) - old_posZ
            radius = round(hip(arc_I,arc_K),6)
            prog(pr,g,x_arc,z_arc,arc_I,arc_K)            
            i+=1
            papp(i,g,x_arc,z_arc,old_posX,old_posZ,P,radius,arc_I,arc_K)
            old_posX = float(number[1])
            old_posZ = float(number[0])

    # начало контура       
    h1=45#XXX вычислять max(X)
    A=[]
    A1=[]
    A2=[]
    A3=[]
    coordZ_start = 2
    bounce_x = 0.5
    bounce_z = 0.5
    while h1>=0:
        for i in reversed(range(len(P))):
            
            if i>1 and P[i][0]==1 :
                intersection_line_line( P[i][3], P[i][4], P[i][1], P[i][2],  h1, -85,h1, 5,A)
            #if i>=1 and P[i][0]>1 :                    
                #en_line_arc(P[i][0],P[i][2],P[i][4],P[i][1],P[i][3],P[len(P)-1][4],h1,P[0][4],h1,P[i][7],P[i][6],P[i][5],A)
        h1 = h1-(0.5*d)

    print 'A =', A ,'\n'
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++GO
    #считаем - сколько раз прямая пересекла контур(max_R)
    repeat=[]
    r=1
    for a in range(len(A)):
            if A[a][1]==A[a-1][1]:
                r+=1
                repeat.append(r)
            else:
                r=1           
    max_R= int(max(repeat) / 2)  
    
    #находим X всех горизонталей
    L=[]
    nn=0                            
    for a in range(len(A)):
        try:
            if A[a][1]!=nn:
                ns=A[a][1]
                L.append(A[a][1])
                nn= ns  
        except:
            pass

    # находим A[a] двух точек с max Z (самые правые)
    def two_a(Arr,L,l, z_min = -10000):
        for a in range(len(Arr)):    
            if Arr[a][1]==L[int(l)]:
                if Arr[a][0] > z_min:
                    z_minL = z_min
                    a0 = a
                    a1  = a-1
        return   a1,a0

    # находим Z двух точек с max Z (самые правые)
    D=[]
    def two(Arr,L,l, z_min = -10000):
        for a in range(len(Arr)):    
            if Arr[a][1]==L[int(l)]:
                if Arr[a][0] > z_min:
                    z_minL = z_min
                    z_minR = Arr[a][0]
                    z_min  = z_minR
        return   z_minL,z_minR

    # сколько точек на следующей линии между z_minL и z_minR
    # ноль , две или более
    def more_than_two(Arr,L,l):
        mtt=[]   
        for a in range(len(Arr)):
            if Arr[a][1]==L[int(l)]:
               lz,rz=two(Arr,L,int(l)-1)
               if (Arr[a][0]) >= lz and (Arr[a][0]) <= rz:
                   mtt.append(Arr[a])
        print len(mtt)        
        if len(mtt) > 2:  return len(mtt)
        if len(mtt) == 2: return len(mtt)
        if len(mtt) == 0: return len(mtt) 
              
    # находим две точки на следующей линии между z_minL и z_minR
    # если их ТОЛЬКО две
    def two_next(Arr,L,l):
        mtt=[]
        for a in range(len(Arr)):            
            if Arr[a][1]==L[int(l)]:
               lz,rz=two(Arr,L,int(l)-1)
               if (Arr[a][0]) >= lz and (Arr[a][0]) <= rz:
                   mtt.append(Arr[a])
                   D.append(Arr[a])             
        return   mtt[0][0],mtt[1][0] , mtt[0][1]

    # находим две точки на следующей линии между z_minL и z_minR
    # если их БОЛЬШЕ чем две
    def two_next2(Arr,L,l):
        mtt=[]
        for a in range(len(Arr)):            
            if Arr[a][1]==L[int(l)]:
               lz,rz=two(Arr,L,int(l)-1)
               mtt=[]
               if (Arr[a][0]) >= lz and (Arr[a][0]) <= rz:
                   mtt.append(Arr[a])
                   D.append(Arr[a])
                   mtt.append(Arr[a-1])
                   D.append(Arr[a-1])                   
        print 'D',D             
        return   mtt[0][0],mtt[1][0] , mtt[0][1]

    for i in range(4):
        l=1 
        while more_than_two(A,L,l):
            if more_than_two(A,L,l)==2:
                Cl,Cr,Cx = two_next(A,L,l)
            elif more_than_two(A,L,l)>2:
                Cl,Cr,Cx = two_next2(A,L,l)                
            self.execute("G1 F1000 X%f Z%f" % (float(Cx),float(Cl)))
            self.execute("G1 F1000 X%f Z%f" % (float(Cx),float(Cr)))
            l+=1
            
        a1,a0 =two_a(A,L ,0)
        del A[a1]
        del A[a1]
             
        A1=[]
        for a in A: 
            if a not in D: A1.append(a)
        A=[]
        for a in A1:
            A.append(a)                     
        D=[] 

        
    #cd /home/nkp/git/linuxcnc/scripts ./linuxcnc             
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++GO            
    #print 'pr=', pr
    #print 'P=', P  
    for w in range(1,len(pr)):
        #print pr[w]
        try:  
            self.execute(pr[w])
        except InterpreterException,e:
                    msg = "%d: '%s' - %s" % (e.line_number,e.line_text, e.error_message)
                    self.set_errormsg(msg) 
                    return INTERP_ERROR 
    
def g700(self, **words):
    """ remap code G70 """
    p = int(words['p'])    
    q = int(words['q'])

    s = linuxcnc.stat() 
    s.poll()

    filename = s.file
    f = open(filename, "r")
    lines = f.readlines()    
##################################################### 
    if words.has_key('f'):    
        fr = float(words['f'])
    self.execute("F%f" % fr)#TODO
    c_line2 = 0               
    for w in lines:
        if  re.search("^\s*[(]\s*N\d", w.upper()):
            if not re.search("[^\(\)\.\-\+NGZXRIKSF\d\s]", w.upper()):
                num2 = int(re.findall("^\s*\d*",(re.split('N',w.upper())[1]))[0])
                if num2 == p: 
                    c_line2 = 1
        if c_line2:
            try: 
                contour=re.split('\)',(re.split('\(',w.upper())[1]))[0]
                self.execute(contour)
            except InterpreterException,e:
                msg = "%d: '%s' - %s" % (e.line_number,e.line_text, e.error_message)
                self.set_errormsg(msg) 
                return INTERP_ERROR
        if  re.search("^\s*[(]\s*N\d", w.upper()):
            if not re.search("[^\(\)\.\-\+NGZXRIKSF\d\s]", w.upper()):
                num2 = int(re.findall("^\s*\d*",(re.split('N',w.upper())[1]))[0])
                if num2 == q: 
                    c_line2 = 0
#------------------------------------------------------#XXX                    
    self.execute("G91") 
    self.execute("G0 X%f Z%f" % ((0.5),(-0.5))) 
    self.execute("G0 X%f " % (25))
    self.execute("G90") 
    self.execute("G0  Z0")                       
    self.execute("G0 Z0") 
#------------------------------------------------------#XXX                                 
    f.close()               
    return INTERP_OK    
#######################################################################
def g733(self, **words):
    """ remap code G73.3 """
    p = int(words['p'])    
    q = int(words['q'])
    #d = float(words['d'])
    offset = float(words['k'])
    
    if words.has_key('s'):
        sspeed = int(words['s'])
        self.execute("S%d" % (sspeed))
    if words.has_key('l'): #только int ???
        offset_StartZ = int(words['l']) 
    only_finishing_cut = 0    
    if words.has_key('j'):
        only_finishing_cut = int(words['j'])
    quantity = 1    
    if words.has_key('i'):
        quantity = int(words['i'])
    if words.has_key('t'):
        R_Fanuc = float(words['t'])

    if words.has_key('f'):    
        fr = float(words['f'])
        

           
    s = linuxcnc.stat() 
    s.poll()
    filename = s.file
    f = open(filename, "r")
    lines = f.readlines()
    pr = []
    self.execute("G21 G18 G49 G40 G90 G61 G7 F1000")
    name_file = "./fgcode.ngc" 
    fgcode = open(name_file, "w") 
    string = 'G21 G18 G49 G40 G90 G61 G7 F1000 \n'
    string += 'T1 M6\n'
    string += 'G1 X-30 Z30\n'
    string += 'G42\n'             
    for w in lines:
        if  re.search("^\s*[(]\s*N\d", w.upper()):
            if not re.search("[^\(\)\.\-\+NGZXRIK\d\s]", w.upper()):
                num2 = int(re.findall("^\s*\d*",(re.split('N',w.upper())[1]))[0])
                if num2 >= p and num2 <= q:
                    try: 
                        contour=re.split('\)',(re.split('\(',w.upper())[1]))[0]
                        string += contour
                        string += '\n'
                    except InterpreterException,e:
                        msg = "%d: '%s' - %s" % (e.line_number,e.line_text, e.error_message)
                        self.set_errormsg(msg) 
                        return INTERP_ERROR                             
    f.close()
    string += 'G40\n'
    self.execute("G40")
    string += 'M30\n'
    fgcode.write(string)
    outfilename  = "./RS274_temp.txt"
    outfile = open(outfilename, "w")    
    fgcode.close() 
    offset = offset/12.7
    offset_mem = offset
#============================================================================    
    for i in range(quantity):
        tfile  = "./rs.tbl"
        setline = open(tfile ,"w")
        offs = ' '.join(['\n','T1','P1','X0','Z0','D%s' % (str(offset_mem))])
        setline.write(offs)
        setline.close()
     
        p = subprocess.Popen(["sh", "-c", (' '.join(['./rs274','-t',tfile,'-g',name_file,outfilename]))],
                          stdin=None,
                          stdout=None,
                          stderr=None )
        p.wait()                
        outfile.close()                      
        
        f1 = open(outfilename, "r")
        ln = f1.readlines()
        old_posX = 0
        old_posZ = 0   
        for w in ln:
            if  re.search("STRAIGHT_TRAVERSE", w.upper()):
                numbers = re.split('\(',w.upper())
                number = re.split('\,',numbers[1].upper())
                prog(pr,0,number[0],number[2])
                old_posX = float(number[0])
                old_posZ = float(number[2])             
            elif  re.search("STRAIGHT_FEED", w.upper()):
                numbers = re.split('\(',w.upper())
                number = re.split('\,',numbers[1].upper())
                x1=float(number[0])*2
                z1=float(number[2])
                prog(pr,1,x1,z1)
                old_posX = float(number[0])
                old_posZ = float(number[2])

            elif  re.search("ARC_FEED", w.upper()):
                numbers = re.split('\(',w.upper())
                number = re.split('\,',numbers[1].upper())
                if float(number[4])>0:
                    g=3
                elif float(number[4])<0:
                    g=2 
                x_arc=float(number[1])*2
                z_arc=float(number[0])
                arc_I = float(number[3]) - old_posX
                arc_K = float(number[2]) - old_posZ
                radius = round(hip(arc_I,arc_K),6)
                prog(pr,g,x_arc,z_arc,arc_I,arc_K)            
                old_posX = float(number[1])
                old_posZ = float(number[0])        
        f1.close()       
        print 'pr=', pr 
        for w in range(1,len(pr)):
            try:  
                self.execute(pr[w])
            except InterpreterException,e:
                        msg = "%d: '%s' - %s" % (e.line_number,e.line_text, e.error_message)
                        self.set_errormsg(msg) 
                        return INTERP_ERROR     
        offset_mem -= offset/quantity
        pr = []
        self.execute("G91") 
        self.execute("G0 X%f Z%f" % ((0.5),(-0.5))) 
        self.execute("G0 X%f " % (25))
        self.execute("G90") 
        self.execute("G0  Z0") 
    
    
    
    
    
    
