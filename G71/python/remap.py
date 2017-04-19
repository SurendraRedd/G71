# --*-- coding:utf-8 --*--
import linuxcnc
import re
import os
from math import *
import traceback
from interpreter import *
from emccanon import MESSAGE

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
     
def intersection_line_line(x1_1, z1_1, x1_2, z1_2):
    A1 = z1_1 - z1_2
    B1 = x1_2 - x1_1
    C1 = x1_1*z1_2 - x1_2*z1_1
    A2 = z2_1 - z2_2
    B2 = x2_2 - x2_1
    C2 = x2_1*z2_2 - x2_2*z2_1
     
    if B1*A2 - B2*A1 and A1:
        z = (C2*A1 - C1*A2) / (B1*A2 - B2*A1)
        x = (-C1 - B1*z) / A1
    elif B1*A2 - B2*A1 and A2:
        z = (C2*A1 - C1*A2) / (B1*A2 - B2*A1)
        x = (-C2 - B2*z) / A2    
    else:
        print 'нет пересечения '
        return
    if min(x1_1, x1_2) <= x <= max(x1_1, x1_2):
        return x, z 
                                      
def papp(n,G,x,z,App=[],r=None,xc=None,zc=None):
    App.append([])
    App[n].append(G)
    App[n].append(App[n-1][3])
    App[n].append(App[n-1][4])                                               
    App[n].append(x)
    App[n].append(z)
    if G>1:
        App[n].append(r)
        App[n].append(xc)
        App[n].append(zc)
    return App 
def prog(array,G,x,z,r=None):
    ser=' '
    string=ser.join(['G1','X',str(x),'Z',str(z)])
    if G==2: 
        string=ser.join(['G2','X',str(x),'Z',str(z),'R',str(r)])
    if G==3: 
        string=ser.join(['G3','X',str(x),'Z',str(z),'R',str(r)])        
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
    s = linuxcnc.stat() 
    s.poll()
    filename = s.file
    f = open(filename, "r")
    lines = f.readlines()

    line_or_arc = []
    coordZ = []
    coordX = []
    coordI = []
    coordK = []
    coordR = []
    s.poll()
    x = 0
    diameter_mode = 1 #XXX (нужен ли вообще G8 ??? )
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
                        
        # подача ,если задается до цикла   
        if re.search(".*\s*G71", lines[x], re.I) and not re.search(".*\s*[(]", lines[x], re.I):
            t_f = x
            while not re.search(".*\s*F", lines[t_f], re.I) and t_f > 0:
                t_f -= 1
            try:
                feed_rate = float(re.search("F\s*([-0-9.]+)",lines[t_f], re.I).group(1))
            except:
                print 'feed rate is set directly in the cycle'
                  
        if re.search("\s*G0?7[^0-9]", lines[x], re.I):
            diameter_mode = 1

        if  re.search("^\s*[(]\s*N\d", lines[x], re.I):
            if not re.search("[^\(\)\.\-\+NGZXRIKSF\d\s]",lines[x].upper()):
                num = int(re.search("N\s*([0-9.]+)",lines[x], re.I).group(1))
                if num == p: 
                    c_line = 1
        if c_line:
            if re.search("G\s*([0-4.]+)",lines[x], re.I):
                ins = line_or_arc.insert(0,(int(re.search("G\s*([0-4.]+)",lines[x], re.I).group(1))))
            else:
                t_l = x
                while not re.search("G\s*([0-4.]+)",lines[t_l], re.I) and t_l > 0:
                    t_l -= 1
                try:
                    ins = line_or_arc.insert(0,(int(re.search("G\s*([0-4.]+)",lines[t_l], re.I).group(1))))
                except:
                    print 'command G :something went wrong'
                    
            if re.search("X\s*([-0-9.]+)",lines[x], re.I):
                ins = pars(coordX,"X\s*([-0-9.]+)",lines[x])
            else:
                t_x = x
                while not re.search("X\s*([-0-9.]+)",lines[t_x], re.I) and t_x > 0:
                    t_x -= 1
                try:
                    ins = pars(coordX,"X\s*([-0-9.]+)",lines[t_x])
                except:
                    print 'coord X :something went wrong'
                    
            if re.search("Z\s*([-0-9.]+)",lines[x], re.I):
                ins = pars(coordZ,"Z\s*([-0-9.]+)",lines[x])
            else:
                t_z = x
                while not re.search("Z\s*([-0-9.]+)",lines[t_z], re.I) and t_z > 0:
                    t_z -= 1
                try:
                    ins = pars(coordZ,"Z\s*([-0-9.]+)",lines[t_z])
                except:
                    print 'coord Z :something went wrong'
                                                                                               
            if  re.search("[I]", lines[x]):
                ins = pars(coordI,"I\s*([-0-9.]+)",lines[x])
                ins = pars(coordK,"K\s*([-0-9.]+)",lines[x])
            else:
                ins=coordI.insert(0,None)
                ins=coordK.insert(0,None)                       
            if  re.search("[R]", lines[x]):
                ins = pars(coordR,"R\s*([-0-9.]+)",lines[x])
            else:
                ins=coordR.insert(0,None)
            if num == p:
                if re.search("X\s*([-0-9.]+)",lines[x], re.I):
                    st_pointX_finishing = float(re.search("X\s*([-0-9.]+)",lines[x], re.I).group(1))
            else:
                t_Sf = x
                while not re.search("X\s*([-0-9.]+)",lines[t_Sf], re.I) and t_Sf > 0:
                    t_Sf -= 1
                try:
                    st_pointX_finishing = float(re.search("X\s*([-0-9.]+)",lines[t_Sf], re.I).group(1))
                except:
                    print 'st_pointX_finishing :something went wrong'
                                
        if  re.search("^\s*[(]\s*N\d", lines[x], re.I):
            if not re.search("[^\(\)\.\-\+NGZXRIKSF\d\s]",lines[x].upper()):
                num = int(re.search("N\s*([0-9.]+)",lines[x], re.I).group(1))
                if num == q: 
                    c_line =0
        x+=1 
        
    #coordZ_start = max(coordZ) + offset_StartZ  
    d_m=1
    if diameter_mode:
        d_m = 2
        d = d * d_m   
    angle = []
    for n in range(len(coordZ)-1):
        lengthZ = abs(coordZ[n] - coordZ[n+1])
        lengthX = abs(coordX[n]/d_m - coordX[n+1]/d_m)                   
        app = angle.append(atan2(lengthX,lengthZ))
        if line_or_arc[n]>1 and coordR[n]!=None:
            lh=(hip(lengthZ,lengthX))/2
            par=acos(lh/coordR[n])
            if line_or_arc[n]==2:
                ar=angle[n]+par
                indK=abs(cos(ar)*coordR[n])
            elif line_or_arc[n]==3:
                ar=angle[n]-par
                indK=-(cos(ar)*coordR[n])
            indI=sin(ar)*coordR[n] 
            pp=coordI.pop(n) 
            pp=coordK.pop(n) 
            ins=coordK.insert(n,indK) 
            ins=coordI.insert(n,indI)               
    app = angle.append(0.2914567944778671)                               
 ################################    
    name_file = './fgcode.ngc'
    fgcode = open(name_file, "w")
    if words.has_key('f'):    
        feed_rate = fr
    self.execute("F%f" % feed_rate)#TODO
    if inifile.find("G71", "BOUNCE_X") != None :
        bounce_x = float(inifile.find("G71", "BOUNCE_X"))*d_m 
    if inifile.find("G71", "BOUNCE_Z") != None :
        bounce_z = float(inifile.find("G71", "BOUNCE_Z"))
    if words.has_key('t'):      
        bounce_x = R_Fanuc*d_m
        bounce_z = R_Fanuc              
    part_n = -1
    flag_executed = 1 
    P = [] 
    program = [] 
    offset_mem=offset
    mm=len(angle)-2  
    for i in range(quantity):
        offsetX=offset*d_m
        loa = line_or_arc[len(angle)-2]
        if loa==0 or loa==1:
            part_n+=1
            P.append([])
            P[part_n].append(loa)
            P[part_n].append(round(coordX[mm+1]+(cos(angle[mm]))*offsetX,10))
            P[part_n].append(coordZ[mm+1]+(sin(angle[mm]))*offset)
            P[part_n].append(round(coordX[mm+1]+(cos(angle[mm]))*offsetX,10))
            P[part_n].append(coordZ[mm+1]+(sin(angle[mm]))*offset)
            FIRST_pointZ = coordZ[mm+1]+(sin(angle[mm]))*offset
            FIRST_pointX = round(coordX[mm+1]+(cos(angle[mm]))*offsetX,10)
            prog(program,loa,FIRST_pointX,FIRST_pointZ)
        elif line_or_arc[len(angle)-2] ==3:
            FIRST_radius = sqrt((coordK[mm])*(coordK[mm]) + (coordI[mm])*(coordI[mm]))            
            FIRST_centreX = coordX[mm+1]/d_m + coordI[mm]            
            FIRST_centreZ = coordZ[mm+1] + coordK[mm]             
            FIRST_pointZ, FIRST_pointX=intersection_line_arc(3,coordZ[mm+1],coordX[mm+1]/d_m,
                                                                coordZ[mm+1]+10,coordX[mm+1]/d_m,
                                                                FIRST_centreZ,FIRST_centreX,
                                                                FIRST_radius+offset)
            FIRST_pointX = FIRST_pointX*d_m                                                   
            part_n+=1
            P.append([])
            P[part_n].append(3)         
            P[part_n].append(FIRST_pointX)
            P[part_n].append(FIRST_pointZ)
            P[part_n].append(FIRST_pointX)
            P[part_n].append(FIRST_pointZ)
            prog(program,1,FIRST_pointX,FIRST_pointZ) 
        elif line_or_arc[len(angle)-2] ==2:
            FIRST_radius = sqrt((coordK[mm])*(coordK[mm]) + (coordI[mm])*(coordI[mm]))            
            FIRST_centreX = coordX[mm+1]/d_m + coordI[mm]            
            FIRST_centreZ = coordZ[mm+1] + coordK[mm]                           
            FIRST_pointZ,FIRST_pointX = coordZ[mm+1], FIRST_centreX-cathetus(FIRST_radius-offset,
                                            abs(FIRST_centreZ-coordZ[mm+1]))
            FIRST_pointX = FIRST_pointX*d_m
            part_n+=1
            P.append([])
            P[part_n].append(2)     
            P[part_n].append(FIRST_pointX)
            P[part_n].append(FIRST_pointZ)
            P[part_n].append(FIRST_pointX)
            P[part_n].append(FIRST_pointZ)
            prog(program,1,FIRST_pointX,FIRST_pointZ)           
        coordZ_start =FIRST_pointZ
        if words.has_key('l'): #только int ???
            coordZ_start =FIRST_pointZ  + offset_StartZ            
        for m in (reversed(range(len(angle)-1))):
            loa = line_or_arc[m]
            if loa==0 or loa==1:
                loa_m = line_or_arc[m-1]
                if loa_m==0 or loa_m==1: 
                    if angle[m-1] < angle[m]: 
                        print 'G01:LINE ANGLE:cw next:LINE'#OK_G7!
                        if m==0:
                            prog(program,loa_m,coordX[m]+cos(angle[m])*offsetX,
                                 coordZ[m]+sin(angle[m])*offset)
                            part_n+=1
                            papp(part_n,loa_m,coordX[m]+cos(angle[m])*offsetX,
                                  coordZ[m]+sin(angle[m])*offset,P)                             
                        else:
                            prog(program,loa_m,coordX[m]+cos(angle[m])*offsetX,
                                 coordZ[m]+sin(angle[m])*offset)
                            part_n+=1
                            papp(part_n,loa_m,coordX[m]+cos(angle[m])*offsetX,coordZ[m]+sin(angle[m])*offset,P) 
                            part_n+=1
                            papp(part_n,3,coordX[m]+cos(angle[m-1])*offsetX,coordZ[m]+sin(angle[m-1])*offset,
                                   P,offset,coordX[m]/d_m,coordZ[m])                 
                            prog(program,3,coordX[m]+cos(angle[m-1])*offsetX,
                                 coordZ[m]+sin(angle[m-1])*offset,offset)                           
                    else:                               
                        print 'G01:LINE ANGLE:ccw next:LINE' #OK_G7! 
                        angl = (angle[m] - angle[m-1])/2 
                        ggX =  offsetX / cos(angl)
                        gg =  offset / cos(angl)
                        angl1 = angle[m] - angl
                        prog(program,loa_m,coordX[m]+cos(angl1)*ggX,
                                 coordZ[m]+sin(angl1)*gg)  
                        part_n+=1
                        papp(part_n,loa_m,coordX[m]+cos(angl1)*ggX,coordZ[m]+sin(angl1)*gg,P)
                else: #если СЛЕДУЮЩИЙ участок "дуга"
                    NEXT_radius = sqrt((coordK[m-1])*(coordK[m-1]) + (coordI[m-1])*(coordI[m-1]))

                    NEXT_centreX = coordX[m]/d_m + coordI[m-1]

                    NEXT_centreZ = coordZ[m] + coordK[m-1] 
                    NEXT_lengthZ = abs(NEXT_centreZ - coordZ[m])
                    NEXT_lengthX = abs(NEXT_centreX - coordX[m]/d_m) 
                    NEXT_alfa = atan2(NEXT_lengthZ,NEXT_lengthX)
                    cw_next_pointZ= coordZ[m]+sin(NEXT_alfa)*offset
                    cw_next_pointX= coordX[m]+cos(NEXT_alfa)*offsetX                   
                    if (line_or_arc[m-1] ==3): #если СЛЕДУЮЩИЙ участок "дуга" CW 
                        if (angle[m] - NEXT_alfa<-0.00349): 
                            print '(G01:LINE)(ANGLE:angle[m]-NEXT_alfa < -0.00349)(next:ARC_G03)'#OK!! G7
                            radius_OFF = NEXT_radius+offset
                            NEXT_arc_itrs_lineZ,NEXT_arc_itrs_lineX = intersection_line_arc(3,coordZ[m+1]+sin(angle[m])*offset,
                                                                                  coordX[m+1]/d_m+cos(angle[m])*offset,
                                                                                  coordZ[m]+sin(angle[m])*offset,
                                                                                  coordX[m]/d_m+cos(angle[m])*offset,
                                                                                  NEXT_centreZ,NEXT_centreX,radius_OFF)
                            prog(program,1,NEXT_arc_itrs_lineX*d_m,NEXT_arc_itrs_lineZ)
                            part_n+=1
                            papp(part_n,1,NEXT_arc_itrs_lineX*d_m,NEXT_arc_itrs_lineZ,P)
                        elif (angle[m] - NEXT_alfa>0.00349): 
                            print '(G01:LINE)(ANGLE:angle[m]-NEXT_alfa > 0.00349)(next:ARC_G03)'#OK!! G7
                            prog(program,1,coordX[m]+cos(angle[m])*offsetX,
                                 coordZ[m]+sin(angle[m])*offset)
                            part_n+=1
                            papp(part_n,1,coordX[m]+cos(angle[m])*offsetX,
                                 coordZ[m]+sin(angle[m])*offset,P)
                            prog(program,3,cw_next_pointX,cw_next_pointZ,offset)
                            part_n+=1 
                            papp(part_n,3,cw_next_pointX,cw_next_pointZ,P,
                                              offset,coordX[m]/d_m,coordZ[m])                           
                        else: #angle[m] == NEXT_alfa 
                            print '(G01:LINE)  (ANGLE:angle[m] == NEXT_alfa)(next:ARC_G03)'#OK!! G7
                            prog(program,1,coordX[m]+cos(angle[m])*offsetX,
                                 coordZ[m]+sin(angle[m])*offset)
                            part_n+=1
                            papp(part_n,1,coordX[m]+cos(angle[m])*offsetX,
                                 coordZ[m]+sin(angle[m])*offset,P)                                 
                    if (line_or_arc[m-1] ==2): #если СЛЕДУЮЩИЙ участок "дуга" CCW
                        if (angle[m] - NEXT_alfa<-0.00349):
                            print '(G01:LINE) (angle[m] - NEXT_alfa<-0.00349) (next:ARC_G02)'#OK!! G7
                            NEXT_arc_itrs_lineZ,NEXT_arc_itrs_lineX = intersection_line_arc(3,coordZ[m+1]+sin(angle[m])*offset,
                                                                                  coordX[m+1]/d_m+cos(angle[m])*offset,
                                                                                  coordZ[m]+sin(angle[m])*offset,
                                                                                  coordX[m]/d_m+cos(angle[m])*offset,
                                                                                  NEXT_centreZ,NEXT_centreX,NEXT_radius-offset) 
                            prog(program,1,NEXT_arc_itrs_lineX*d_m,NEXT_arc_itrs_lineZ)
                            part_n+=1
                            papp(part_n,1,NEXT_arc_itrs_lineX*d_m,NEXT_arc_itrs_lineZ,P)

                        elif (angle[m] - NEXT_alfa>0.00349): 
                            print '(G01:LINE) (angle[m] - NEXT_alfa>0.00349) (next:ARC_G02)'#OK!! G7
                            prog(program,1,coordX[m]+cos(angle[m])*offsetX,
                                 coordZ[m]+sin(angle[m])*offset)
                            part_n+=1
                            papp(part_n,1,coordX[m]+cos(angle[m])*offsetX,
                                 coordZ[m]+sin(angle[m])*offset,P)
                            prog(program,3,cw_next_pointX,cw_next_pointZ,offset)
                            part_n+=1
                            papp(part_n,3,cw_next_pointX,cw_next_pointZ,P,offset,coordX[m]/d_m,coordZ[m])
                        else:       #angle[m] == NEXT_alfa
                            print '(G01:LINE)  (next:ARC_G02 angle[m] == NEXT_alfa) (next:ARC_G02)'#OK!! G7
                            prog(program,1,coordX[m]+cos(angle[m])*offsetX,
                                 coordZ[m]+sin(angle[m])*offset)
                            part_n+=1
                            papp(part_n,1,coordX[m]+cos(angle[m])*offsetX,
                                 coordZ[m]+sin(angle[m])*offset,P)
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            else:  
                radius = sqrt((coordK[m])*(coordK[m]) + (coordI[m])*(coordI[m]))
                centreX = (coordX[m+1]/d_m + coordI[m])
                centreZ = coordZ[m+1] + coordK[m]
                lengthZ = abs(centreZ - coordZ[m])
                lengthX = abs(centreX - coordX[m]/d_m) 
                alfa = atan2(lengthZ,lengthX)
                zz= (radius-offset)*sin(alfa)
                xx= (radius-offset)*cos(alfa)
                pointZ=centreZ-zz
                if (coordX[m]/d_m < centreX):
                    pointX=centreX-xx
                else:
                    pointX=centreX+xx
                if (line_or_arc[m] == 3): 
                    loa_m = line_or_arc[m-1]
                    if loa_m==0 or loa_m==1:
                        if (angle[m-1] - alfa < -0.00349):
                            print '(G03:ARC)(ANGLE:angle[m-1] - alfa < -0.00349)(next:LINE)'#OK!! G7
                            cw_zz = (radius+offset)*sin(alfa)
                            cw_xx = (radius+offset)*cos(alfa)
                            cw_pointZ= centreZ+cw_zz
                            cw_pointX= centreX+cw_xx                                     
                            prog(program,3,cw_pointX*d_m,cw_pointZ,radius+offset)                            
                            part_n+=1
                            papp(part_n,3,cw_pointX*d_m,cw_pointZ,P,radius+offset,centreX,centreZ)
                            
                            prog(program,3,coordX[m]+cos(angle[m-1])*offsetX,
                                 coordZ[m]+sin(angle[m-1])*offset,offset)
                            part_n+=1
                            papp(part_n,3,coordX[m]+cos(angle[m-1])*offsetX,
                                  coordZ[m]+sin(angle[m-1])*offset,P,offset,coordX[m]/d_m,coordZ[m]) 
                        elif (angle[m-1] - alfa > 0.00349):
                            print '(G03:ARC)(ANGLE:angle[m-1] - alfa > 0.00349)(next:LINE)'#OK!! G7
                            radius_and_off = radius+offset
                            if m==0:
                                
                                arc_itrs_lineZ,arc_itrs_lineX = coordZ[m], centreX+cathetus(radius+offset,
                                                                                    abs(centreZ-coordZ[m]))
                            else:
                                arc_itrs_lineZ,arc_itrs_lineX = intersection_line_arc(3,coordZ[m]+sin(angle[m-1])*offset,
                                                                                     coordX[m]/d_m+cos(angle[m-1])*offset,
                                                                                     coordZ[m-1]+sin(angle[m-1])*offset,
                                                                                     coordX[m-1]/d_m+cos(angle[m-1])*offset,
                                                                                     centreZ,centreX,radius_and_off)
                            prog(program,3,arc_itrs_lineX*d_m,arc_itrs_lineZ,radius+offset)
                            part_n+=1 
                            papp(part_n,3,arc_itrs_lineX*d_m,arc_itrs_lineZ,P,radius_and_off,centreX,centreZ) 
                        else:
                            print '(G03:ARC)(ANGLE:angle[m-1] == alfa ) (next:LINE)'#OK!! G7                                
                            prog(program,3,coordX[m]+cos(angle[m-1])*offsetX,
                                 coordZ[m]+sin(angle[m-1])*offset,radius+offset)
                            part_n+=1
                            papp(part_n,3,coordX[m]+cos(angle[m-1])*offsetX,
                                 coordZ[m]+sin(angle[m-1])*offset,P,radius+offset,centreX,centreZ)                               
                    else:  #если дуга G3
                        NEXT_radius = sqrt((coordK[m-1])*(coordK[m-1]) + (coordI[m-1])*(coordI[m-1]))
                        NEXT_centreX = coordX[m]/d_m + coordI[m-1]
                        NEXT_centreZ = coordZ[m] + coordK[m-1]                      
                        if (line_or_arc[m-1] == 3):   # и следующая дуга G3 
                            print 'G03:ARC  next:ARC_G03'                                 #OK_G7!
                            NEXT_X,NEXT_Z=intersection_arc_arc(NEXT_centreX,NEXT_centreZ, 
                                                               NEXT_radius+offset,centreX,centreZ,radius+offset,
                                                               coordX[m]/d_m,coordZ[m])                
                            prog(program,3,NEXT_X*d_m,NEXT_Z,radius+offset)
                            part_n+=1
                            papp(part_n,3,NEXT_X*d_m,NEXT_Z,P,radius+offset,centreX,centreZ)
                        if (line_or_arc[m-1] == 2): # и следующая дуга G2 
                            print 'G03:ARC ANGLE:ccw next:ARC_G02'
                            NEXT_X,NEXT_Z=intersection_arc_arc(NEXT_centreX,NEXT_centreZ, 
                                                               NEXT_radius-offset,centreX,centreZ,radius+offset,
                                                               coordX[m]/d_m,coordZ[m])                
                            prog(program,3,NEXT_X*d_m,NEXT_Z,radius+offset)
                            part_n+=1
                            papp(part_n,3,NEXT_X*d_m,NEXT_Z,P,radius+offset,centreX,centreZ)
                else: #если участок "дуга" CCW  
                    loa_m = line_or_arc[m-1]
                    if loa_m==0 or loa_m==1:
                        if (angle[m-1] - alfa < -0.00349):
                            print '(G02:ARC) (angle[m-1] - alfa < -0.00349) (next:LINE)'  #OK_G7!
                            prog(program,2,pointX*d_m,pointZ,radius-offset)
                            part_n+=1
                            papp(part_n,2,pointX*d_m,pointZ,P,radius-offset,centreX,centreZ)
                            if m:
                                prog(program,3,coordX[m]+cos(angle[m-1])*offsetX,
                                     coordZ[m]+sin(angle[m-1])*offset,offset)
                                part_n+=1
                                papp(part_n,3,coordX[m]+cos(angle[m-1])*offsetX,
                                     coordZ[m]+sin(angle[m-1])*offset,P,offset,coordX[m]/d_m,coordZ[m]) 
                        elif (angle[m-1] - alfa > 0.00349):
                            print '(G02:ARC)(ANGLE:angle[m-1] - alfa > 0.00349)(next:LINE)' #OK_G7!     
                            radius_and_off = radius-offset
                            if m==0:
                                arc_itrs_lineZ,arc_itrs_lineX = coordZ[m],coordX[m]-offsetX #XXX
                            else:
                                arc_itrs_lineZ,arc_itrs_lineX = intersection_line_arc(2,coordZ[m]+sin(angle[m-1])*offset,
                                                                                     coordX[m]/d_m+cos(angle[m-1])*offset,
                                                                                     coordZ[m-1]+sin(angle[m-1])*offset,
                                                                                     coordX[m-1]/d_m+cos(angle[m-1])*offset,
                                                                                     centreZ,centreX,radius_and_off)
                            prog(program,2,arc_itrs_lineX*d_m,arc_itrs_lineZ,radius-offset)
                            part_n+=1
                            papp(part_n,2,arc_itrs_lineX*d_m,arc_itrs_lineZ,P,radius_and_off,centreX,centreZ) 
 
                        else:
                            print 'G02:ARC   next:LINE angle[m-1] == alfa'   #OK_G7!
                            prog(program,2,coordX[m]+cos(angle[m-1])*offsetX,
                                     coordZ[m]+sin(angle[m-1])*offset,radius-offset)
                            part_n+=1
                            papp(part_n,2,coordX[m]+cos(angle[m-1])*offsetX,
                                 coordZ[m]+sin(angle[m-1])*offset,P,radius-offset,centreX,centreZ)                              
                            
                    else: 
                        NEXT_radius = sqrt((coordK[m-1])*(coordK[m-1]) + (coordI[m-1])*(coordI[m-1]))
                        NEXT_centreX = coordX[m]/d_m + coordI[m-1]
                        NEXT_centreZ = coordZ[m] + coordK[m-1]                  
                        if (line_or_arc[m-1] == 2): 
                            print 'G02:ARC  next:ARC_G02'
                            NEXT_X,NEXT_Z=intersection_arc_arc(NEXT_centreX,NEXT_centreZ, 
                                                               NEXT_radius-offset,centreX,centreZ,radius-offset,
                                                               coordX[m]/d_m,coordZ[m])                
                            prog(program,2,NEXT_X*d_m,NEXT_Z,radius-offset)
                            part_n+=1
                            papp(part_n,2,NEXT_X*d_m,NEXT_Z,P,radius-offset,centreX,centreZ)
                            ########################################
                        if (line_or_arc[m-1] == 3): 
                            print 'G02:ARC ANGLE:ccw next:ARC_G03'
                            NEXT_X,NEXT_Z=intersection_arc_arc(NEXT_centreX,NEXT_centreZ, 
                                                               NEXT_radius+offset,centreX,centreZ,radius-offset,
                                                               coordX[m]/d_m,coordZ[m])                
                            prog(program,2,NEXT_X*d_m,NEXT_Z,radius-offset)
                            part_n+=1
                            papp(part_n,2,NEXT_X*d_m,NEXT_Z,P,radius-offset,centreX,centreZ)
##################################################################### GO!
        #print 'program =', program 
        #print 'P =', P                            
        flag_micro_part = 0        

        if diameter_mode:
            self.execute("G21 G18 G49  G90 G61 G7")
            fgcode.write("G21 G18 G49  G90 G61 G7\n")
        else:
            self.execute("G21 G18 G49  G90 G61 G8")
            fgcode.write("G21 G18 G49  G90 G61 G8\n") 
                   
        fgcode.write("F%f \n" % feed_rate)

        COORDx0 = P[len(P)-1][3]
        
        #съем "до начала контура"
        t_COORDz0 =  P[len(P)-1][4]
        t2_COORDx0 = COORDx0 
        self.execute("G1 X%f Z%f" % ((ST_COORDx0),(ST_COORDz0)))

        while  ST_COORDx0 - t2_COORDx0 > d :
            self.execute("G1  Z%f" % (t_COORDz0))
            self.execute("G0 X%f Z%f" % ((ST_COORDx0+bounce_x),(t_COORDz0+bounce_z)))
            self.execute("G0 Z%f" % (coordZ_start))                   
            ST_COORDx0 -= d
            self.execute("G1 X%f" % (ST_COORDx0))
            
        self.execute("G1  Z%f" % (t_COORDz0))
        self.execute("G0 X%f Z%f" % ((ST_COORDx0+bounce_x),(t_COORDz0+bounce_z)))
        self.execute("G0 Z%f" % (coordZ_start))    
        self.execute("G1 X%f Z%f" % ((COORDx0),(coordZ_start+bounce_z))) 
           
        if flag_executed :
            i = len(P)-1
            if only_finishing_cut==0 :
                if COORDx0 - P[len(P)-1][1] <= d:
                    d=0
                while COORDx0 - P[i][1] >= d :
                    d = (float(words['d']))*d_m  
                    if P[i][0] == 1 or P[i][0] == 0:
                        Mz1 = P[i][2]
                        Mx1 = P[i][1]
                        Mz2 = P[i][4]
                        Mx2 = P[i][3]  
                        if (Mz2-Mz1)!=0:
                            K=(Mx2-Mx1)/(Mz2-Mz1)
                            B=-(K*Mz1-Mx1)
                            COORDz0 = (COORDx0 - B)/K
                        else:
                            COORDz0=P[i][2] 
                    elif P[i][0] == 2:
                        Mz1 = P[i][2]
                        Mx1 = P[i][3]/d_m 
                        Mz2 = P[i][4]
                        Mx2 = P[i][3]/d_m 
                        B=COORDx0 /d_m                          
                        center = [P[i][7],P[i][6]] 
                        radius = P[i][5]                   
                        b = -2*center[0]   
                        c = -radius**2 + (B-center[1])**2 + center[0]**2  
                        D = b**2 - 4*c                         
                        if D < 0:  
                            print 'D<0  G2'
                        else:   
                            z1 = (-b-sqrt(D))/2 
                            z2 = (-b+sqrt(D))/2
                            if Mz1 < z1 < Mz2:#TODO 
                                COORDz0=z2
                            else:
                                COORDz0=z1
                    elif P[i][0] == 3:
                        Mz1 = P[i][2]
                        Mx1 = P[i][3]/d_m 
                        Mz2 = P[i][4]
                        Mx2 = P[i][3]/d_m 
                        B=COORDx0/d_m   
                        center = [P[i][7],P[i][6]]
                        radius = P[i][5] 
                        b = -2*center[0]  
                        c = -radius**2 + (B-center[1])**2 + center[0]**2  
                        D = b**2 - 4*c 
                        if D < 0: 
                            print 'D<0  G3'
                        else:  
                            z1 = (-b-sqrt(D))/2 
                            z2 = (-b+sqrt(D))/2 
                            if Mz1 < z1 < Mz2:
                                COORDz0=z1
                            else:
                                COORDz0=z2
                    self.execute("G1 Z%f" % ((COORDz0)))
                    fgcode.write("G1 Z%f\n" % ((COORDz0)))
                    if bounce_z > coordZ_start - COORDz0:
                        self.execute("G0 X%f Z%f" % ((COORDx0),(coordZ_start)))
                        fgcode.write("G0 X%f Z%f\n" % ((COORDx0),(coordZ_start)))
                    else:
                        self.execute("G0 X%f Z%f" % ((COORDx0+bounce_x),(COORDz0+bounce_z)))
                        fgcode.write("G0 X%f Z%f\n" % ((COORDx0+bounce_x),(COORDz0+bounce_z)))
                        self.execute("G0 Z%f" % (coordZ_start))
                        fgcode.write("G0 Z%f\n" % (coordZ_start))

                    COORDx0 = COORDx0 - d
                    for next_i in reversed(range(len(P))): 
                        if P[next_i][3] >= COORDx0 > P[next_i][1]:
                            i=next_i                     
                    self.execute("G1 X%f" % (COORDx0))
                    fgcode.write("G1 X%f\n" % (COORDx0)) 
                    if flag_micro_part :                    
                        if COORDx0 - P[i][1] < d and P[i][3] > COORDx0 > P[i][1]:
                            d=0
                            flag_micro_part = 1
                        else:
                            flag_micro_part = 0
                        continue
                    if COORDx0 - P[i][1] < d:
                        if P[i][0] == 1 or P[i][0] == 0:
                            Mz1 = P[i][2]
                            Mx1 = P[i][1]
                            Mz2 = P[i][4]
                            Mx2 = P[i][3]  
                            if (Mz2-Mz1)!=0:
                                K=(Mx2-Mx1)/(Mz2-Mz1)
                                B=-(K*Mz1-Mx1)
                                COORDz0 = (COORDx0 - B)/K
                            else:
                                COORDz0=P[i][2] 
                            self.execute("G1 Z%f" % ((COORDz0)))
                            fgcode.write("G1 Z%f\n" % ((COORDz0)))
                            if bounce_z > coordZ_start - COORDz0:
                                self.execute("G0 X%f Z%f" % ((COORDx0),(coordZ_start)))
                                fgcode.write("G0 X%f Z%f\n" % ((COORDx0),(coordZ_start)))
                            else:
                                self.execute("G0 X%f Z%f" % ((COORDx0+bounce_x),(COORDz0+bounce_z)))
                                fgcode.write("G0 X%f Z%f\n" % ((COORDx0+bounce_x),(COORDz0+bounce_z)))
                                self.execute("G0 Z%f" % (coordZ_start))
                                fgcode.write("G0 Z%f\n" % (coordZ_start))
                            if i>1:
                                COORDx0 = COORDx0 - d 
                                for next_i in reversed(range(len(P))): 
                                    if P[next_i][3] >= COORDx0 > P[next_i][1]:
                                        i=next_i                                  
                                if COORDx0 - P[i][1] < d and P[i][3] > COORDx0 > P[i][1]:
                                    d=0
                                    flag_micro_part = 1   
                                self.execute("G1 X%f" % (COORDx0))
                                fgcode.write("G1 X%f\n" % (COORDx0))
                        elif P[i][0] == 2:
                            Mz1 = P[i][2]
                            Mx1 = P[i][3]/d_m
                            Mz2 = P[i][4]
                            Mx2 = P[i][3]/d_m
                            B=COORDx0 /d_m                       
                            center = [P[i][7],P[i][6]]
                            radius = P[i][5]  
                            b = -2*center[0]  
                            c = -radius**2 + (B-center[1])**2 + center[0]**2
                            D = b**2 - 4*c 
                            if D < 0:
                                print 'D<0'
                            else: 
                                z1 = (-b-sqrt(D))/2
                                z2 = (-b+sqrt(D))/2 
                                if Mz1 < z1 < Mz2:#TODO
                                    COORDz0=z2
                                else:
                                    COORDz0=z1
                            self.execute("G1 Z%f" % ((COORDz0)))
                            fgcode.write("G1 Z%f\n" % ((COORDz0)))                          
                            if bounce_z > coordZ_start - COORDz0:
                                self.execute("G0 X%f Z%f" % ((COORDx0),(coordZ_start)))
                                fgcode.write("G0 X%f Z%f\n" % ((COORDx0),(coordZ_start)))
                            else:
                                self.execute("G0 X%f Z%f" % ((COORDx0+bounce_x),(COORDz0+bounce_z)))
                                fgcode.write("G0 X%f Z%f\n" % ((COORDx0+bounce_x),(COORDz0+bounce_z)))
                                self.execute("G0 Z%f" % (coordZ_start))
                                fgcode.write("G0 Z%f\n" % (coordZ_start))
                            if i>1:
                                COORDx0 = COORDx0 - d 
                                for next_i in reversed(range(len(P))): 
                                    if P[next_i][3] >= COORDx0 > P[next_i][1]:
                                        i=next_i                                  
                                if COORDx0 - P[i][1] < d and P[i][3] > COORDx0 > P[i][1]:
                                    d=0
                                    flag_micro_part = 1
                                self.execute("G1 X%f" % (COORDx0))
                                fgcode.write("G1 X%f\n" % (COORDx0))
                        elif P[i][0] == 3:
                            Mz1 = P[i][2]
                            Mx1 = P[i][3]/d_m
                            Mz2 = P[i][4]
                            Mx2 = P[i][3]/d_m
                            B=COORDx0/d_m 
                            center = [P[i][7],P[i][6]]
                            radius = P[i][5]
                            b = -2*center[0]
                            c = -radius**2 + (B-center[1])**2 + center[0]**2
                            D = b**2 - 4*c
                            if D < 0:  
                                print 'D<0'
                            else:   
                                z1 = (-b-sqrt(D))/2   
                                z2 = (-b+sqrt(D))/2 
                                if Mz1 < z1 < Mz2: #TODO сделать "умнее" расчет
                                    COORDz0=z1
                                else:
                                    COORDz0=z2
                            self.execute("G1 Z%f" % ((COORDz0)))
                            fgcode.write("G1 Z%f\n" % ((COORDz0)))
                            if bounce_z > coordZ_start - COORDz0:
                                self.execute("G0 X%f Z%f" % ((COORDx0),(coordZ_start)))
                                fgcode.write("G0 X%f Z%f\n" % ((COORDx0),(coordZ_start)))
                            else:
                                self.execute("G0 X%f Z%f" % ((COORDx0+bounce_x),(COORDz0+bounce_z)))
                                fgcode.write("G0 X%f Z%f\n" % ((COORDx0+bounce_x),(COORDz0+bounce_z)))
                                self.execute("G0 Z%f" % (coordZ_start))
                                fgcode.write("G0 Z%f\n" % (coordZ_start))
                            if i>1:
                                COORDx0 = COORDx0 - d 
                                for next_i in reversed(range(len(P))): 
                                    if P[next_i][3] >= COORDx0 > P[next_i][1]:
                                        i=next_i                                  
                                if COORDx0 - P[i][1] < d and P[i][3] > COORDx0 > P[i][1]:
                                    d=0
                                    flag_micro_part = 1
                                self.execute("G1 X%f" % (COORDx0))
                                fgcode.write("G1 X%f\n" % (COORDx0))                         
            else:
                MESSAGE("Only finishing cut") 
                self.execute("M0")                          
#####################################################                                                          
        flag_executed = 0                                            
        for w in program:
            try:  
                self.execute(w)
                fgcode.write(w)
                fgcode.write("\n")
            except InterpreterException,e:
                        msg = "%d: '%s' - %s" % (e.line_number,e.line_text, e.error_message)
                        self.set_errormsg(msg) 
                        return INTERP_ERROR  
        offset-=offset_mem/quantity
        program = []
        self.execute("G0 Z%f" % (coordZ_start)) 
        fgcode.write("G0 Z%f\n" % (coordZ_start))   
#####################################################
    '''self.execute("G40 " ) 
    self.execute("G0 X%f Z%f" % ((st_pointX_finishing),(coordZ_start+bounce_z))) 
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
                fgcode.write(contour)
                fgcode.write("\n")
            except InterpreterException,e:
                msg = "%d: '%s' - %s" % (e.line_number,e.line_text, e.error_message)
                self.set_errormsg(msg) 
                return INTERP_ERROR
        if  re.search("^\s*[(]\s*N\d", w.upper()):
            if not re.search("[^\(\)\.\-\+NGZXRIKSF\d\s]", w.upper()):
                num2 = int(re.findall("^\s*\d*",(re.split('N',w.upper())[1]))[0])
                if num2 == q: 
                    c_line2 = 0''' 
                                   
    self.execute("G40" )   
    self.execute("G0 Z0")
    fgcode.write("G0 Z0\n")
    fgcode.write("M02\n")                             
    f.close() 
    fgcode.close()               
    return INTERP_OK
    
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
    self.execute("G0 Z0")                            
    f.close()               
    return INTERP_OK    
    
    
    
    
    
    
    
    
