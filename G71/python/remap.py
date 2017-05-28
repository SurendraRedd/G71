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

    
def hip(a,b):
    c = sqrt(abs(a*a + b*b))
    return c
    
def arc_max_point(G,stZ,endZ,stX,endX):
    pass
    return
        
def en_line_arc(G,stZ,endZ,stX,endX, Mz1,Mx1,Mz2,Mx2,centreZ,centreX,rad,A):
    centreX = centreX * 1
    centreZ = centreZ * 1
    
    #r_Xmax = (centreX + rad)*2
    
    a=[]
    aa=[]
               
    b = -2*centreZ  
    c = -rad**2 + (Mx1-centreX)**2 + centreZ**2 
    D = b**2 - 4*c 
    if D < 0: 
      #print 'D<0'      
      return
    z1 = (-b-sqrt(D))/2 
    z2 = (-b+sqrt(D))/2
    if z1==z2: return True # если касается(не пересекает)
    hh=Mx1*2
    if G==3:
        r_Xmax = (centreX + rad)*2
        if   centreZ <= endZ or centreZ >= stZ: r_Xmax = None
        if stZ >= z1 >= endZ and  min(stX,endX) <= hh <= max(stX,endX,r_Xmax) :#XXX  r_Xmax
          pointZ1 = z1
          pointX1 = hh
          a.append(pointZ1)
          a.append(pointX1)
          A.append(a)
        if stZ >= z2 >= endZ and  min(stX,endX) <= hh <= max(stX,endX,r_Xmax) :
          pointZ2 = z2 
          pointX1 = hh
          aa.append(pointZ2)
          aa.append(pointX1)
          A.append(aa)
          return   
 
    if G==2:
        r_Xmax = (centreX - rad)*2
        if   centreZ <= endZ or centreZ >= stZ: r_Xmax = None
            
        if stZ >= z1 >= endZ and  max(stX,endX) >= hh >= min(stX,endX,r_Xmax) :#XXX  r_Xmax
          pointZ1 = z1 
          pointX1 = hh
          a.append(pointZ1)
          a.append(pointX1)
          A.append(a)
        if stZ >= z2 >= endZ and  max(stX,endX) >= hh >= min(stX,endX,r_Xmax) :
          pointZ2 = z2 
          pointX1 = hh
          aa.append(pointZ2)
          aa.append(pointX1)
          A.append(aa)
          return 

def intersect_vertic(stZ,endZ,stX,endX, h,centreZ,centreX,rad,A):

    centreX = centreX * 2
    rad = rad * 1
        
    a=[]

    cat = abs(h-centreZ)
    b=sqrt(abs(rad*rad - cat*cat))
    
    x1 = centreX + b*2
    x2 = centreX - b*2

    r_Xmin = (centreX - rad)*2
        
    if 40 >= x1 >= 0 and  max(stZ,endZ) >= h >= min(stZ,endZ):
        a.append(x1)
        a.append(h)
        A.append(a)
        return   
 
    elif 40 >= x2 >= 0 and  max(stZ,endZ) >= h >= min(stZ,endZ):
        a.append(x2)
        a.append(h)
        A.append(a)
        return   
     
def intersection_line_line( p1X, p1Z, p2X, p2Z ,p3X, p3Z, p4X, p4Z,A   ):
              
    p1X = p1X *(-0.5)        
    p2X = p2X *(-0.5)        
    p3X = p3X *(-1)       
    p4X = p4X *(-1) 
                      
    a = []

    if (p2X - p1X):    
        z = p1Z + ((p2Z - p1Z) * (p3X - p1X)) / (p2X - p1X)
    elif p2X==p1X:      
        return True

    if (z>max(p3Z,p4Z) or z<min(p3Z,p4Z) or z>max(p1Z,p2Z) or z<min(p1Z,p2Z) or p3X>max(p1X,p2X) or p3X<min(p1X,p2X)):
        pass
    else:
        a.append(z)
        a.append(-p3X*2)
        A.append(a)                
        return False

def in_line_line_G72( p1X, p1Z, p2X, p2Z ,p3X, p3Z, p4X, p4Z,A   ):
              
    p1X = p1X *(-0.5)        
    p2X = p2X *(-0.5)        
    p3X = p3X *(-1)       
    p4X = p4X *(-1) 
                      
    a = []

    if (p2Z - p1Z):    
        z = p1X + ((p2X - p1X) * (p3Z - p1Z)) / (p2Z - p1Z);
    elif p2Z == p1Z:      
        return True

    if (z>max(p3X,p4X) or z<min(p3X,p4X) or z>max(p1X,p2X) or z<min(p1X,p2X) or p3Z>max(p1Z,p2Z) or p3Z<min(p1Z,p2Z)):
        print 'нет пересечения'
        pass
    else:
        a.append(-z*2)
        a.append(p3Z)
        A.append(a)                
        return False
                                      
def papp(n,G,x,z,old_x,old_z,App=[],r=None,xc=None,zc=None):
    App.append([])
    App[n].append(G)
    App[n].append(old_x*2)
    App[n].append(old_z)                                               
    App[n].append(x)
    App[n].append(z)
    if G>1:
        App[n].append(r)
        App[n].append(xc+old_x)
        App[n].append(zc+old_z)
    return App 
def prog(array,G,x,z,i=None,k=None):
    ser=' '
    string=ser.join(['G1','X',str(x),'Z',str(z)])
    if G==0: 
        string=ser.join(['G0','X',str(x),'Z',str(z)])
    if G==2: 
        string=ser.join(['G2','X',str(x),'Z',str(z),'I',str(i),'K',str(k)])
    if G==3: 
        string=ser.join(['G3','X',str(x),'Z',str(z),'I',str(i),'K',str(k)])        
    return array.append(string) 
    
# находим A[a] двух точек с max Z (самые правые)    
def two_a(Arr,L,l, z_min = -10000):
    try: 
        for a in range(len(Arr)):    
            if Arr[a][1]==L[int(l)]:
                if Arr[a][0] > z_min:
                    z_minL = z_min
                    a0 = a
                    a1  = a-1
        return   a1,a0
    except:
        print 'error two_a'
        
# находим Z двух точек с max Z (самые правые)
def two(Arr,L,l, z_min = -10000):
    try:    
        for a in range(len(Arr)):    
            if Arr[a][1]==L[int(l)]:
                if Arr[a][0] > z_min:
                    z_minL = z_min
                    z_minR = Arr[a][0]
                    z_min  = z_minR
        return   z_minL,z_minR
    except:
        print 'error two'
        
# сколько точек на следующей линии между z_minL и z_minR
# ноль , две или более
def more_than_two(Arr,L,l,fl):
    try:
        mtt=[]   
        for a in range(len(Arr)):
            if Arr[a][1]==L[int(l)]:
                if l==0 or fl:
                    lz,rz=two(Arr,L,int(l))
                else:
                    lz,rz=two(Arr,L,int(l)-1)
                if (Arr[a][0]) >= lz and (Arr[a][0]) <= rz:
                    mtt.append(Arr[a])       
        if len(mtt) > 2:  return len(mtt)
        if len(mtt) == 2: return len(mtt)
        if len(mtt) == 0: return len(mtt)
    except:
        print 'error more_than_two'            
          
# находим самые правые две точки на следующей линии 

def two_next(Arr,L,l,D):
    try:
        for a in range(len(Arr)):            
            if Arr[a][1]==L[int(l)]:
               a1,a0=two_a(Arr,L,int(l)-0)
               D.append(Arr[a1]) 
               D.append(Arr[a0])            
        return   Arr[a1],Arr[a0]
    except:
        print 'two_next' 
            
# "подбираем"  d , что бы линия не совпадала с 
# горизонтальным отрезком 
def num(P,d,h):    
    while h>=0:
        for i in reversed(range(len(P))):                
            if i>2 and P[i][0]==1 :
                if P[i][3] == P[i][1] and P[i][3] == round(h,5):                
                    return True                              
        h = h-(1*d)  
        
def go(self,Ar,Lr,D,R,expcode):
    repeat = 100        
    try:
        while len(Ar)>0 and repeat:
            fl=0 
            for l in R:
                fl=1 # флаг первого прохода
                while more_than_two(Ar,Lr,l,fl) :
                    if more_than_two(Ar,Lr,l,fl)==2:
                        Cl,Cr = two_next(Ar,Lr,l,D)
                    elif more_than_two(Ar,Lr,l,fl)>2:
                        #R.append(l)# запоминаем позицию для "возврата"
                        R.insert(1,l)# запоминаем позицию для "возврата"
                        Cl,Cr = two_next(Ar,Lr,l,D) 
                    if  l==0 or fl:
                        old_Cl,old_Cr = Cl,Cr
                        self.execute("G0  X%f " % (Lr[l]+5))
                        expcode.write("G0 X%f\n" % (Lr[l]+5))
                         
                        self.execute("G0  Z%f" % (float(Cr[0])))
                        expcode.write("G0 Z%f\n" % (float(Cr[0])))
                                         
                    self.execute("G0   Z%f" % (float(Cr[0])))
                    expcode.write("G0 Z%f\n" % (float(Cr[0])))
                    
                    self.execute("G1   X%f " % (float(Cr[1])))
                    expcode.write("G1 X%f\n" % (float(Cr[1])))
                       
                    self.execute("G1   X%f Z%f" % (float(Cl[1]),float(Cl[0]))) 
                    expcode.write("G1 X%f Z%f\n" % (float(Cl[1]),float(Cl[0])))  
                    
                    if float(Cl[0])+0.5 > float(old_Cr[0]):
                        self.execute("G0 X%f Z%f" % (float(Cl[1])+0.01,(float(Cl[0])+0.01)))
                        expcode.write("G0 X%f Z%f\n" % (float(Cl[1])+0.01,(float(Cl[0])+0.01)))
                    else:
                        self.execute("G0   X%f Z%f" % (float(Cl[1])+0.5,float(Cl[0])+0.5)) 
                        expcode.write("G0 X%f Z%f\n" % (float(Cl[1])+0.5,float(Cl[0])+0.5)) 
                    old_Cl,old_Cr = Cl,Cr
                    l+=1
                    fl=0      
                A1=[]
                for a in Ar: 
                    if a not in D: A1.append(a)
                Ar=[]
                for a in A1:
                    Ar.append(a)                    
            repeat -= 1               
    except :
        if len(Ar):
            self.execute("(AXIS,notify, %s)" % ("something went wrong"))
        return 
    if repeat==0:        
        self.execute("(AXIS,notify, %s)" % ("something went wrong!"))
        return    
                         
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
    d = abs(float(words['d']))
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
        self.execute("F%f" % (fr))
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
    
    x=0
    c_line = 0
    while x < len(lines):
        # находим начальную точку цикла по X 
        if re.search(".*\s*G71", lines[x], re.I) and not re.search(".*\s*[(]", lines[x], re.I):
            t_Sx = x
            while not re.search(".*\s*X", lines[t_Sx], re.I) and t_Sx > 0:
                t_Sx -= 1
            ST_COORDx0 = float(re.search("X\s*([-0-9.]+)",lines[t_Sx], re.I).group(1))
            
        # находим начальную точку цикла по Z 
        if re.search(".*\s*G71", lines[x], re.I) and not re.search(".*\s*[(]", lines[x], re.I):
            t_Sz = x
            while not re.search(".*\s*Z", lines[t_Sz], re.I) and t_Sz > 0:
                t_Sz -= 1
            ST_COORDz0 = float(re.search("Z\s*([-0-9.]+)",lines[t_Sz], re.I).group(1))    
        x+=1

    self.execute("G21 G18 G49 G40 G90 G61 G7 ")
    name_file = "./fgcode.ngc" 
    fgcode = open(name_file, "w") 
    string = 'G21 G18 G49 G40 G90 G61 G7 F1000 \n'
    string += 'T1 M6\n'
    
    # добавляем в  контур "начальный отрезок"(обязательно), и "конечный"(опционально)
    for x in range(len(lines)):
        if  re.search("^\s*[(]\s*N\d", lines[x].upper()):
            if not re.search("[^\(\)\.\-\+NGZXRIK\d\s]", lines[x].upper()):
                num2 = int(re.findall("^\s*\d*",(re.split('N',lines[x].upper())[1]))[0])
                if num2 == p :
                    c_line = 1
                    if re.search("X\s*([-0-9.]+)",lines[x], re.I):
                        st_cont_X = float(re.search("X\s*([-0-9.]+)",lines[x], re.I).group(1))
        if c_line:
            if re.search("Z\s*([-0-9.]+)",lines[x], re.I):
                end_cont_Z = float(re.search("Z\s*([-0-9.]+)",lines[x], re.I).group(1))
            if re.search("X\s*([-0-9.]+)",lines[x], re.I):   
                end_cont_X = float(re.search("X\s*([-0-9.]+)",lines[x], re.I).group(1))
        if  re.search("^\s*[(]\s*N\d", lines[x].upper()):
            if not re.search("[^\(\)\.\-\+NGZXRIK\d\s]", lines[x].upper()):
                num2 = int(re.findall("^\s*\d*",(re.split('N',lines[x].upper())[1]))[0])
                if num2 == q :
                    c_line = 0                  
                
                

    if float(words['d'])<0 : # если расточка(d со знаком минус)  
        if ST_COORDx0 - end_cont_X > d :
            print 'error cycle start point '
            self.execute("(AXIS,notify, %s)" % ("error cycle start point"))
            return
    
    string += 'G1 X-30 Z30\n'
    string += 'G1 X-25 Z35\n'
    if float(words['d'])>=0 : # если НЕ расточка(d со знаком минус)
        string += 'G0 X%f Z%f\n' % (ST_COORDx0,ST_COORDz0)
        string += 'G0 X%f Z%f\n' % (st_cont_X+d,ST_COORDz0)
    if float(words['d'])<0 :
        string += 'G41\n' 
    else:
        string += 'G42\n'  
                     
    for w in lines:
        if  re.search("^\s*[(]\s*N\d", w.upper()):
            if not re.search("[^\(\)\.\-\+NGZXRIK\d\s]", w.upper()):
                num2 = int(re.findall("^\s*\d*",(re.split('N',w.upper())[1]))[0])
                if num2 == p :
                    c_line = 1
        if c_line:    
            try: 
                contour=re.split('\)',(re.split('\(',w.upper())[1]))[0]
                string += contour
                string += '\n'
            except :
                print 'error_for w in lines'

        if  re.search("^\s*[(]\s*N\d", w.upper()):
            if not re.search("[^\(\)\.\-\+NGZXRIK\d\s]", w.upper()):
                num2 = int(re.findall("^\s*\d*",(re.split('N',w.upper())[1]))[0])
                if num2 == q :
                    c_line = 0                                                    
    f.close()
    
    string += 'G1 F100 Z%f\n' % (end_cont_Z-offset*2) #"конечный" отрезок
    string += 'G1 F100 X%f Z%f\n' % (ST_COORDx0,end_cont_Z-offset*2) #"конечный" отрезок
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
            x1=float(number[0])*2
            z1=float(number[2])
            prog(pr,0,x1,z1)
            i+=1
            papp(i,0,x1,z1,old_posX,old_posZ,P)
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
    tmp1=[]
    tmp2=[] 
    for p in P: #XXX если дуга - добавлять точку максимума по X
       tmp1.append(p[1])
       tmp2.append(p[4])
                
    z_minim = min(tmp2)
    z_maxim = 50  #XXX вынести в INI ??

    A=[]    
    bounce_x = 0.5
    bounce_z = 0.5
    h1=max(tmp1)*0.5 - 0.1 #XXX разобраться с точностью вычислений 
                
    kh1= 0.0    
    while num(P,d,h1):
        kh1 = kh1 + 0.01
        d = d - kh1  #XXX может быть нужно изменять (и) h1
        print 'd=',d 
    #---------------------------------------------------ищем все точки пересечения    
    h1=max(tmp1)*0.5 - 0.1 
    while h1>=0:
        for i in reversed(range(len(P))):            
            if i>2 and P[i][0]<=1 :
                par=intersection_line_line( P[i][3], P[i][4], P[i][1], P[i][2],  h1, z_minim,h1, z_maxim,A)
            if i>2 and P[i][0]>1 :
                o=en_line_arc(P[i][0],P[i][2],P[i][4],P[i][1],P[i][3],z_minim,h1,z_maxim,h1,P[i][7],P[i][6],P[i][5],A)    
        h1 = h1-(1*d)
        
    print 'P =', P ,'\n'
    print 'A =', A ,'\n'
    #------------------------------------------------------------------ID
    if float(words['d'])<0 : # если расточка(d со знаком минус)
        for i in reversed(range(len(A))) : 
            self.execute("G1 F1000  X%f" % (A[i][1]))                          
            self.execute("G1 F1000  Z%f" % (A[i][0]))
            self.execute("G0 X%f Z%f" % (float(A[i][1]) - d + bounce_x,float(A[i][0])+bounce_z) )
            self.execute("G0 Z%f" % (ST_COORDz0))

        for w in range(2,len(pr)):
            try:  
                self.execute(pr[w])
            except InterpreterException,e:
                        msg = "%d: '%s' - %s" % (e.line_number,e.line_text, e.error_message)
                        self.set_errormsg(msg) 
                        return INTERP_ERROR 
        self.execute("G0 Z%f" % (ST_COORDz0))
        return    
    
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
    L.append(0)

    explicit = 'ngc/explicit.ngc'
    expcode = open(explicit, "r")
    exp_lines = expcode.readlines()
    exp_string=''
    if len(exp_lines):
        for el in exp_lines:
            exp_string += el
        es1=exp_string.split('M02')[0]
        expcode = open(explicit, "w")
        expcode.write(es1)
        expcode = open(explicit, "a")
    else:
        expcode = open(explicit, "w")
    expcode.write("G21 G18 G49  G90 G61 G7\n")
    if words.has_key('f'):    
        fr = float(words['f'])
        expcode.write("F%f\n" % fr)

    D=[]              
    R=[0]
    go(self,A,L,D,R,expcode)            
    self.execute("G0  X%f" % (max(tmp1)+5))#XXX 
    expcode.write("G0 X%f\n" % (max(tmp1)+5))
                   
    print 'pr=', pr 
    for w in range(2,len(pr)):
        try:  
            self.execute(pr[w])
            expcode.write(pr[w])
            expcode.write("\n")
        except InterpreterException,e:
                    msg = "%d: '%s' - %s" % (e.line_number,e.line_text, e.error_message)
                    self.set_errormsg(msg) 
                    return INTERP_ERROR 
    self.execute("G0 X%f " % (max(tmp1)+5))#XXX 
    expcode.write("G0 X%f\n" % (max(tmp1)+5)) 
    self.execute("G0 Z%f " % (ST_COORDz0))#XXX
    expcode.write("G0 Z%f\n" % (ST_COORDz0))     
    expcode.write("M02\n") 
    expcode.close()
def g700(self, **words):
    """ remap code G70 """
    p = int(words['p'])    
    q = int(words['q'])
    
    if words.has_key('f'):
        fr = float(words['f'])
        self.execute("F%f" % (fr))
    if words.has_key('d'):
        d = float(words['d'])
   
    s = linuxcnc.stat() 
    s.poll()

    filename = s.file
    f = open(filename, "r")
    lines = f.readlines()
    
    bounce_x = 0.5
    bounce_z = 0.5 
    
    explicit = 'ngc/explicit.ngc'
    expcode = open(explicit, "r")
    exp_lines = expcode.readlines()
    exp_string=''
    if len(exp_lines):
        for el in exp_lines:
            exp_string += el
        es1=exp_string.split('M02')[0]
        expcode = open(explicit, "w")
        expcode.write(es1)
        expcode = open(explicit, "a")
    else:
        expcode = open(explicit, "w")
    expcode.write("G21 G18 G49  G90 G61 G7\n")
    if words.has_key('f'):    
        fr = float(words['f'])
        expcode.write("F%f\n" % fr)   
##################################################### 

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
                expcode.write(contour)
                expcode.write("\n")
            except :
                print 'G700_error'
            if re.search("Z\s*([-0-9.]+)",w, re.I):
                end_cont_Z = float(re.search("Z\s*([-0-9.]+)",w, re.I).group(1))
            if re.search("X\s*([-0-9.]+)",w, re.I):   
                end_cont_X = float(re.search("X\s*([-0-9.]+)",w, re.I).group(1)) 
        if  re.search("^\s*[(]\s*N\d", w.upper()):
            if not re.search("[^\(\)\.\-\+NGZXRIKSF\d\s]", w.upper()):
                num2 = int(re.findall("^\s*\d*",(re.split('N',w.upper())[1]))[0])
                if num2 == q: 
                    c_line2 = 0
                              
#  завершающий отход (в зависимости : OD или ID)
    if words.has_key('d'):
        if d<0:
            self.execute("G0 X%f Z%f" % (float(end_cont_X)-bounce_x,float(end_cont_Z)+0.1))
            expcode.write("G0 X%f Z%f\n" % (float(end_cont_X)-bounce_x,float(end_cont_Z)+0.1))
            return
    self.execute("G0 X%f Z%f" % (float(end_cont_X)+bounce_x,float(end_cont_Z)+0.1))
    expcode.write("G0 X%f Z%f\n" % (float(end_cont_X)+bounce_x,float(end_cont_Z)+0.1))  
                                
    f.close()
    expcode.write("M02\n")                
    expcode.close()
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
        
        explicit = 'ngc/explicit.ngc'
        expcode = open(explicit, "r")
        exp_lines = expcode.readlines()
        exp_string=''
        if len(exp_lines):
            for el in exp_lines:
                exp_string += el
            es1=exp_string.split('M02')[0]
            expcode = open(explicit, "w")
            expcode.write(es1)
            expcode = open(explicit, "a")
        else:
            expcode = open(explicit, "w")
        expcode.write("G21 G18 G49  G90 G61 G7\n")
        if words.has_key('f'):    
            fr = float(words['f'])
            expcode.write("F%f\n" % fr)        
              
        print 'pr=', pr 
        for w in range(1,len(pr)):
            try:  
                self.execute(pr[w])
                expcode.write(pr[w])
                expcode.write("\n")
            except:
                print 'G733_error'
                return INTERP_ERROR     
        offset_mem -= offset/quantity
        pr = []
        self.execute("G91") 
        self.execute("G0 X%f Z%f" % ((0.5),(0.5))) 
        self.execute("G0 X%f " % (25))
        self.execute("G90") 
        self.execute("G0  Z0") 
    
#################################################-----G72

def g720(self, **words):
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
    
    x=0
    c_line = 0
    while x < len(lines):
        # находим начальную точку цикла по X 
        if re.search(".*\s*G72", lines[x], re.I) and not re.search(".*\s*[(]", lines[x], re.I):
            t_Sx = x
            while not re.search(".*\s*X", lines[t_Sx], re.I) and t_Sx > 0:
                t_Sx -= 1
            ST_COORDx0 = float(re.search("X\s*([-0-9.]+)",lines[t_Sx], re.I).group(1))
            
        # находим начальную точку цикла по Z 
        if re.search(".*\s*G72", lines[x], re.I) and not re.search(".*\s*[(]", lines[x], re.I):
            t_Sz = x
            while not re.search(".*\s*Z", lines[t_Sz], re.I) and t_Sz > 0:
                t_Sz -= 1
            ST_COORDz0 = float(re.search("Z\s*([-0-9.]+)",lines[t_Sz], re.I).group(1))    
        x+=1

    self.execute("G21 G18 G49 G40 G90 G61 G7 F1000")
    name_file = "./fgcode.ngc" 
    fgcode = open(name_file, "w") 
    string = 'G21 G18 G49 G40 G90 G61 G7 F1000 \n'
    string += 'T1 M6\n'

    
    # добавляем в  контур "начальный отрезок"(обязательно), и "конечный"(опционально)
    for w in lines:
        if  re.search("^\s*[(]\s*N\d", w.upper()):
            if not re.search("[^\(\)\.\-\+NGZXRIK\d\s]", w.upper()):
                num2 = int(re.findall("^\s*\d*",(re.split('N',w.upper())[1]))[0])
                if num2 == p :
                    if re.search("X\s*([-0-9.]+)",w, re.I):
                        st_cont_X = float(re.search("X\s*([-0-9.]+)",w, re.I).group(1))
                if num2 >= p and num2 <= q:
                    #contour=re.split('\)',(re.split('\(',w.upper())[1]))[0]
                    if re.search("Z\s*([-0-9.]+)",w, re.I):
                        end_cont_Z = float(re.search("Z\s*([-0-9.]+)",w, re.I).group(1))

    string += 'G1 X-30 Z30\n'
    string += 'G1 X-25 Z35\n'
    #string += 'G1 F100 X%f Z%f\n' % (ST_COORDx0,ST_COORDz0)
    #print 'st_cont_X=' ,st_cont_X
    #string += 'G1 F100 X%f Z%f\n' % (st_cont_X,ST_COORDz0)
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

    #string += 'G1 F100 X%f Z%f\n' % (ST_COORDx0,end_cont_Z) #"конечный" отрезок
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
            x1=float(number[0])*2
            z1=float(number[2])
            prog(pr,0,x1,z1)
            i+=1
            papp(i,0,x1,z1,old_posX,old_posZ,P)
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
    tmp1=[]
    tmp2=[] 
    for p in P: #XXX если дуга - добавлять точку максимума по X
       tmp1.append(p[1])
       tmp2.append(p[4])
                
    z_minim = min(tmp2)
    z_maxim = 5
    print 'z_minim=',z_minim,'z_maxim=',z_maxim
    A=[]
    bounce_x = 0.5
    bounce_z = 0.5
    #---------------------------------------------------ищем все точки пересечения
    
    h1=0
    while h1>=z_minim :
        for i in range(len(P)):          
            if i>2 and P[i][0]==1 :
                par=in_line_line_G72( P[i][3], P[i][4], P[i][1], P[i][2],   0 ,h1, 1000 ,h1,A)
            if i>2 and P[i][0]>1 :
                intersect_vertic(P[i][2],P[i][4],P[i][1],P[i][3],h1,P[i][7],P[i][6],P[i][5],A)    
        h1 = h1-(1*d)
        
    print 'P =', P ,'\n'
    print 'A =', A ,'\n'
    
    explicit = 'ngc/explicit.ngc'
    expcode = open(explicit, "r")
    exp_lines = expcode.readlines()
    exp_string=''
    if len(exp_lines):
        for el in exp_lines:
            exp_string += el
        es1=exp_string.split('M02')[0]
        expcode = open(explicit, "w")
        expcode.write(es1)
        expcode = open(explicit, "a")
    else:
        expcode = open(explicit, "w")
    expcode.write("G21 G18 G49  G90 G61 G7\n")
    if words.has_key('f'):    
        fr = float(words['f'])
        expcode.write("F%f\n" % fr)
    
    self.execute("G1 F1000  X%f Z%f" % (ST_COORDx0,0))
    expcode.write("G1 F1000  X%f Z%f\n" % (ST_COORDx0,0))
    for i in range(len(A)) :
        self.execute("G1 F1000  Z%f" % (A[i][1]))
        expcode.write("G1 F1000  Z%f\n" % (A[i][1]))
        
        self.execute("G1 F1000  X%f Z%f" % (A[i][0],A[i][1])) 
        expcode.write("G1 F1000  X%f Z%f\n" % (A[i][0],A[i][1])) 
                       
        self.execute("G1 F1000  X%f" % (ST_COORDx0))
        expcode.write("G1 F1000  X%f\n" % (ST_COORDx0))
        
    self.execute("G1 F1000  X%f" % (ST_COORDx0)) 
    expcode.write("G1 F1000  X%f\n" % (ST_COORDx0)) 
       
    self.execute("G0   Z0")
    expcode.write("G0   Z0\n")
    #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++GO            
    print 'pr=', pr 
    for w in range(2,len(pr)):
        try:  
            self.execute(pr[w])
            expcode.write(pr[w])
            expcode.write("\n")
        except InterpreterException,e:
                    msg = "%d: '%s' - %s" % (e.line_number,e.line_text, e.error_message)
                    self.set_errormsg(msg) 
                    return INTERP_ERROR 
    
    self.execute("G1 F1000  X%f " % (ST_COORDx0))
    expcode.write("G1 F1000  X%f\n " % (ST_COORDx0))    
    self.execute("G0   Z0")
    expcode.write("G0   Z0\n") 
    expcode.write("M02\n")                             
    expcode.close()   
    
