# --*-- coding:utf-8 --*--
import linuxcnc
import re
from math import *
import traceback
from interpreter import *
from emccanon import MESSAGE

throw_exceptions = 1 # raises InterpreterException if execute() or read() fail
    
def pars(array,reg ,lines): 
    a=array.insert(0,(float(re.search(reg,lines, re.I).group(1))))
def cathetus(c,b):
    a = sqrt(abs(c*c - b*b))
    return a 
def hip(a,b):
    c = sqrt(abs(a*a + b*b))
    return c
def intersection_line_arc(G,Mz1,Mx1,Mz2,Mx2,centreZ,centreX,radius):    
    if (Mz2-Mz1)!=0:
        K=(Mx2-Mx1)/(Mz2-Mz1)
        B=-(K*Mz1-Mx1)           
        a = 1 + K**2                                                                                    
        b = -2*centreZ + 2*K*B -2*K*centreX                                                         
        c = -radius**2 + (B-centreX)**2 + centreZ**2                                                 
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
        print 'окружности не пересекаются'
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
        print 'окружности соприкасаются'
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
                               
def fapp(n,G,x,z,App=[],r=1,xc=1,zc=1):
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
#################################################-----G71.2
def g712(self, **words):
    """ remap code G71.2 """
    p = int(words['p'])    
    q = int(words['q'])
    d = float(words['d'])
    offset = float(words['k'])
    
    if words.has_key('s'):
        rsv1 = float(words['s'])
    if words.has_key('l'):
        rsv2 = float(words['l'])
    only_finishing_cut = 0    
    if words.has_key('j'):
        only_finishing_cut = int(words['j'])
    quantity = 1    
    if words.has_key('i'):
        quantity = int(words['i'])
    tool = 2
    if words.has_key('t'):
        tool = int(words['t'])
    if words.has_key('t'):    
        feed_rate = float(words['f'])
    s = linuxcnc.stat() 
    s.poll()
    #backangle  =  s.tool_table #TODO 
    #frontangle =  s.tool_table
    filename = s.file
    f = open(filename, "r")
    lines = f.readlines()
    x,v = 0,-1
    line_or_arc = []
    coordZ = []
    coordX = []
    coordI = []
    coordK = []
    coordR = []
    s.poll() 
    while x < len(lines):
        if  re.search("^\s*[(]\s*N\d", lines[x], re.I):
            if not re.search("[^\(\)\.\-\+NGZXRIK\d\s]",lines[x].upper()):
                num = int(re.search("N\s*([0-9.]+)",lines[x], re.I).group(1))
                if num >= p and num <= q:
                    v+=1
                    ins = line_or_arc.insert(0,(int(re.search("G\s*([0-4.]+)",lines[x], re.I).group(1))))
                    ins = pars(coordZ,"Z\s*([-0-9.]+)",lines[x])
                    ins = pars(coordX,"X\s*([-0-9.]+)",lines[x])                    
                    if  re.search("[I]", lines[x]):
                        ins = pars(coordI,"I\s*([-0-9.]+)",lines[x])
                        ins = pars(coordK,"K\s*([-0-9.]+)",lines[x])
                    else:
                        a=coordI.insert(0,None)
                        a=coordK.insert(0,None)                       
                    if  re.search("[R]", lines[x]):
                        ins = pars(coordR,"R\s*([-0-9.]+)",lines[x])                        
                if num == p : 
                    temp_x = x
                    a=2
                    while not re.search("^\s*.*Z", lines[temp_x-a].upper()):
                        a+=1
                    coordZ_start = float(re.search("Z\s*([-0-9.]+)",lines[temp_x-a], re.I).group(1))   
        x+=1     
    angle = [] 
    angle_deg = [] #TEMP 
    for n in range(len(coordZ)-1):
        lengthZ = abs(coordZ[n] - coordZ[n+1])
        lengthX = abs(coordX[n] - coordX[n+1])                    
        app = angle.append(atan2(lengthX,lengthZ))
        DEG=int(degrees(atan2(lengthX,lengthZ)))+180
        app = angle_deg.append(DEG)
    app = angle.append(0.2914567944778671)                               
 ################################
    part_n = -1
    flag_executed = 1 
    P = [] 
    program = [] 
    offset_mem=offset
    mm=len(angle)-2
    ser=' '
    if words.has_key('t'):
        self.execute("F%f" % feed_rate)
    string=ser.join(['G18 G90 G49 ',])
    ins = program.append(string)   
    for i in range(quantity):
        if line_or_arc[len(angle)-2] ==1:
            string=ser.join(['G1','X',str(round(coordX[mm+1]+(cos(angle[mm]))*offset,10)) ,
                              'Z',str(coordZ[mm+1]+(sin(angle[mm]))*offset),]) 
            ins = program.append(string) 
            ins = program.append(string)
            part_n+=1
            P.append([])
            P[part_n].append(1)
            P[part_n].append(coordX[mm+1]+(cos(angle[mm]))*offset)
            P[part_n].append(coordZ[mm+1]+(sin(angle[mm]))*offset)
            P[part_n].append(coordX[mm+1]+(cos(angle[mm]))*offset)
            P[part_n].append(coordZ[mm+1]+(sin(angle[mm]))*offset)
            FIRST_pointZ = coordZ[mm+1]+(sin(angle[mm]))*offset
            FIRST_pointX = round(coordX[mm+1]+(cos(angle[mm]))*offset,10)
        elif line_or_arc[len(angle)-2] ==3:
            FIRST_radius = sqrt((coordK[mm])*(coordK[mm]) + (coordI[mm])*(coordI[mm]))            
            FIRST_centreX = coordX[mm+1] + coordI[mm]            
            FIRST_centreZ = coordZ[mm+1] + coordK[mm]             
            FIRST_pointZ , FIRST_pointX =  intersection_line_arc(3,coordZ[mm+1],coordX[mm+1],coordZ[mm+1]+10,coordX[mm+1],FIRST_centreZ,FIRST_centreX,FIRST_radius+offset)
       
            string=ser.join(['G1','X',str(FIRST_pointX) ,
                              'Z',str(FIRST_pointZ)]) 
            ins = program.append(string)
            part_n+=1
            P.append([])
            P[part_n].append(3)         
            P[part_n].append(FIRST_pointX)
            P[part_n].append(FIRST_pointZ)
            P[part_n].append(FIRST_pointX)
            P[part_n].append(FIRST_pointZ) 
        elif line_or_arc[len(angle)-2] ==2:
            FIRST_radius = sqrt((coordK[mm])*(coordK[mm]) + (coordI[mm])*(coordI[mm]))
            FIRST_centreX = coordX[mm+1] + coordI[mm]
            FIRST_centreZ = coordZ[mm+1] + coordK[mm] 
            FIRST_lengthZ = abs(FIRST_centreZ - coordZ[mm+1])
            FIRST_lengthX = abs(FIRST_centreX - coordX[mm+1])
            FIRST_alfa = atan2(FIRST_lengthZ,FIRST_lengthX)
            FIRST_zz= (FIRST_radius-offset)*sin(FIRST_alfa)
            FIRST_xx= (FIRST_radius-offset)*cos(FIRST_alfa)
            FIRST_pointX=FIRST_centreX-FIRST_xx
            if (coordZ[mm]<FIRST_centreZ):
                FIRST_pointZ=FIRST_centreZ-FIRST_zz
            else:
                FIRST_pointZ=FIRST_centreZ+FIRST_zz
            string=ser.join(['G1','X',str(round(coordX[mm+1]+(cos(angle[mm]))*offset,10)) ,
                              'Z',str(coordZ[mm+1]+(sin(angle[mm]))*offset),]) 
            ins = program.append(string)

            part_n+=1
            P.append([])
            P[part_n].append(2)         
            P[part_n].append(coordX[mm+1]+(cos(angle[mm]))*offset)
            P[part_n].append(coordZ[mm+1]+(sin(angle[mm]))*offset)
            P[part_n].append(coordX[mm+1]+(cos(angle[mm]))*offset)
            P[part_n].append(coordZ[mm+1]+(sin(angle[mm]))*offset)             
        for m in (reversed(range(len(angle)-1))):   
            if (line_or_arc[m] ==1): 
                if (line_or_arc[m-1] ==1): 
                    if angle[m-1] < angle[m]: 
                        print 'G01:LINE ANGLE:cw next:LINE'
                        if m==0:
                            string=ser.join(['G1','X',str(coordX[m]+cos(angle[m])*offset),
                                                  'Z',str(coordZ[m]+sin(angle[m])*offset)])
                            ins = program.append(string)
                        else:
                            string=ser.join(['G1','X',str(coordX[m]+cos(angle[m])*offset),
                                                  'Z',str(coordZ[m]+sin(angle[m])*offset),])
                            ins = program.append(string)                  
                        if m!=0:
                            string=ser.join(['G3','X',str(coordX[m]+cos(angle[m-1])*offset),
                                        'Z',str(coordZ[m]+sin(angle[m-1])*offset),'R',str(offset),])
                            ins = program.append(string)
                        part_n+=1
                        P.append([])
                        P[part_n].append(1)    
                        if m==0:
                            P[part_n].append(P[part_n-1][3])
                            P[part_n].append(P[part_n-1][4])                                               
                            P[part_n].append(coordX[m]+cos(angle[m])*offset)
                            P[part_n].append(coordZ[m]+sin(angle[m])*offset)                         
                        else:
                            P[part_n].append(P[part_n-1][3])
                            P[part_n].append(P[part_n-1][4])                                               
                            P[part_n].append(coordX[m]+cos(angle[m])*offset)
                            P[part_n].append(coordZ[m]+sin(angle[m])*offset)  
                            part_n+=1 
                            P.append([])
                            P[part_n].append(3)
                            P[part_n].append(P[part_n-1][3])
                            P[part_n].append(P[part_n-1][4])                                               
                            P[part_n].append(coordX[m]+cos(angle[m-1])*offset)
                            P[part_n].append(coordZ[m]+sin(angle[m-1])*offset)
                            P[part_n].append(offset)
                            P[part_n].append(coordX[m])
                            P[part_n].append(coordZ[m])
                    else:                               
                        print 'G01:LINE ANGLE:ccw next:LINE'
                        angl = (angle[m] - angle[m-1])/2 
                        gg =  offset / cos(angl)
                        angl1 = angle[m] - angl

                        string=ser.join(['G1','X',str(coordX[m]+cos(angl1)*gg),'Z',str(coordZ[m]+sin(angl1)*gg),])  
                        ins = program.append(string)
                        part_n+=1
                        P.append([])
                        P[part_n].append(1)
                        P[part_n].append(P[part_n-1][3])
                        P[part_n].append(P[part_n-1][4])                                                 
                        P[part_n].append(coordX[m]+cos(angl1)*gg)
                        P[part_n].append(coordZ[m]+sin(angl1)*gg)
                       
                else: #если СЛЕДУЮЩИЙ участок "дуга"
                    NEXT_radius = sqrt((coordK[m-1])*(coordK[m-1]) + (coordI[m-1])*(coordI[m-1]))
                    NEXT_centreX = coordX[m] + coordI[m-1]
                    NEXT_centreZ = coordZ[m] + coordK[m-1] 
                    NEXT_lengthZ = abs(NEXT_centreZ - coordZ[m])
                    NEXT_lengthX = abs(NEXT_centreX - coordX[m]) 
                    NEXT_alfa = atan2(NEXT_lengthZ,NEXT_lengthX)
                    NEXT_zz= (NEXT_radius-offset)*sin(NEXT_alfa)
                    NEXT_xx= (NEXT_radius-offset)*cos(NEXT_alfa)
                    NEXT_pointX=NEXT_centreX-NEXT_xx
                    if (coordZ[m]<NEXT_centreZ):
                        NEXT_pointZ=NEXT_centreZ-NEXT_zz
                    else:
                        NEXT_pointZ=NEXT_centreZ+NEXT_zz
                    if (line_or_arc[m-1] ==3): #если СЛЕДУЮЩИЙ участок "дуга" CW                        
                        if (angle[m] - NEXT_alfa<-0.2): 
                            print '(G01:LINE)(ANGLE:angle[m]-NEXT_alfa < -0.2)(next:ARC_G03)'                            
                            radius_OFF = NEXT_radius+offset
                            NEXT_arc_itrs_lineZ,NEXT_arc_itrs_lineX = intersection_line_arc(3,coordZ[m+1]+sin(angle[m])*offset,
                                                                                  coordX[m+1]+cos(angle[m])*offset,
                                                                                  coordZ[m]+sin(angle[m])*offset,
                                                                                  coordX[m]+cos(angle[m])*offset,
                                                                                  NEXT_centreZ,NEXT_centreX,radius_OFF)
                            string=ser.join(['G1','X',str(NEXT_arc_itrs_lineX ),'Z',str(NEXT_arc_itrs_lineZ)])
                            ins = program.append(string)
                            part_n+=1
                            P.append([])
                            P[part_n].append(1)
                            P[part_n].append(P[part_n-1][3])
                            P[part_n].append(P[part_n-1][4])                                               
                            P[part_n].append(NEXT_arc_itrs_lineX )
                            P[part_n].append(NEXT_arc_itrs_lineZ)

                        elif (angle[m] - NEXT_alfa>0.2): 
                            print '(G01:LINE)(ANGLE:angle[m]-NEXT_alfa > 0.2)(next:ARC_G03)'
                            cw_next_zz = (NEXT_radius+offset)*sin(NEXT_alfa)#TODO
                            cw_next_xx = (NEXT_radius+offset)*cos(NEXT_alfa)#TODO
                            OLD_cw_next_pointZ= NEXT_centreZ+cw_next_zz
                            OLD_cw_next_pointX= NEXT_centreX+cw_next_xx
                            cw_next_pointZ= coordZ[m]+sin(NEXT_alfa)*offset
                            cw_next_pointX= coordX[m]+cos(NEXT_alfa)*offset                           
                            print 'NEXT_alfa=', degrees(NEXT_alfa) 
                            print 'cw_next_pointX по старому=', OLD_cw_next_pointX
                            print 'cw_next_pointZ по старому=', OLD_cw_next_pointZ
                            print 'cw_next_pointX по НОВОМУ=', cw_next_pointX
                            print 'cw_next_pointZ по НОВОМУ=', cw_next_pointZ
                            string=ser.join(['G1','X',str(coordX[m]+cos(angle[m])*offset),'Z',str(coordZ[m]+sin(angle[m])*offset)])
                            ins = program.append(string)
                            part_n+=1
                            P.append([])
                            P[part_n].append(1)
                            P[part_n].append(P[part_n-1][3])
                            P[part_n].append(P[part_n-1][4])                                               
                            P[part_n].append(coordX[m]+cos(angle[m])*offset )
                            P[part_n].append(coordZ[m]+sin(angle[m])*offset)                            
                            string=ser.join(['G3','X',str(cw_next_pointX),'Z',str(cw_next_pointZ),'R',str(offset)])
                            ins = program.append(string)
                            part_n+=1 
                            P.append([])
                            P[part_n].append(3)
                            P[part_n].append(P[part_n-1][3])
                            P[part_n].append(P[part_n-1][4])                                               
                            P[part_n].append(cw_next_pointX)
                            P[part_n].append(cw_next_pointZ)
                            P[part_n].append(offset)
                            P[part_n].append(coordX[m])
                            P[part_n].append(coordZ[m])
                        else: #angle[m] == NEXT_alfa 
                            print '(G01:LINE)  (ANGLE:angle[m] == NEXT_alfa)(next:ARC_G03)'
                            string=ser.join(['G1','X',str(coordX[m]+cos(angle[m])*offset),'Z',str(coordZ[m]+sin(angle[m])*offset)])
                            ins = program.append(string)
                            part_n+=1
                            P.append([])
                            P[part_n].append(1)
                            P[part_n].append(P[part_n-1][3])
                            P[part_n].append(P[part_n-1][4])                                               
                            P[part_n].append(coordX[m]+cos(angle[m])*offset )
                            P[part_n].append(coordZ[m]+sin(angle[m])*offset)
                    if (line_or_arc[m-1] ==2): #если СЛЕДУЮЩИЙ участок "дуга" CCW
                        if (angle[m] - NEXT_alfa<-0.2):
                            print '(G01:LINE) (angle[m] - NEXT_alfa<-0.2) (next:ARC_G02)' 
                            string=ser.join(['G1','X',str(coordX[m]+cos(angle[m])*offset),'Z',str(coordZ[m]+sin(angle[m])*offset)])
                            ins = program.append(string)
                            part_n+=1
                            P.append([])
                            P[part_n].append(1)
                            P[part_n].append(P[part_n-1][3])
                            P[part_n].append(P[part_n-1][4])                                               
                            P[part_n].append(coordX[m]+cos(angle[m])*offset )
                            P[part_n].append(coordZ[m]+sin(angle[m])*offset)
                        elif (angle[m] - NEXT_alfa>0.2): 
                            print '(G01:LINE) (angle[m] - NEXT_alfa>0.2) (next:ARC_G02)'#DXF line_arc_G2>.dxf
                            string=ser.join(['G1','X',str(coordX[m]+cos(angle[m])*offset),'Z',str(coordZ[m]+sin(angle[m])*offset)])
                            ins = program.append(string)
                            part_n+=1
                            P.append([])
                            P[part_n].append(1)
                            P[part_n].append(P[part_n-1][3])
                            P[part_n].append(P[part_n-1][4])                                               
                            P[part_n].append(coordX[m]+cos(angle[m])*offset )
                            P[part_n].append(coordZ[m]+sin(angle[m])*offset)
                            string=ser.join(['G3','X',str(NEXT_pointX),'Z',str(NEXT_pointZ),'R',str(offset)])#TODO
                            ins = program.append(string)
                            part_n+=1 
                            P.append([])
                            P[part_n].append(3)
                            P[part_n].append(P[part_n-1][3])
                            P[part_n].append(P[part_n-1][4])                                               
                            P[part_n].append(NEXT_pointX)#TODO упростить вычисление
                            P[part_n].append(NEXT_pointZ)#TODO
                            P[part_n].append(offset)
                            P[part_n].append(coordX[m])
                            P[part_n].append(coordZ[m])
                        else:       #angle[m] == NEXT_alfa
                            print '(G01:LINE)  (next:ARC_G02 angle[m] == NEXT_alfa) (next:ARC_G02)'
                            string=ser.join(['G1','X',str(coordX[m]+cos(angle[m])*offset),'Z',str(coordZ[m]+sin(angle[m])*offset)])
                            ins = program.append(string)
                            part_n+=1
                            P.append([])
                            P[part_n].append(1)
                            P[part_n].append(P[part_n-1][3])
                            P[part_n].append(P[part_n-1][4])                                               
                            P[part_n].append(coordX[m]+cos(angle[m])*offset )
                            P[part_n].append(coordZ[m]+sin(angle[m])*offset)
         
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            else:  
                radius = sqrt((coordK[m])*(coordK[m]) + (coordI[m])*(coordI[m]))
                centreX = coordX[m+1] + coordI[m]
                centreZ = coordZ[m+1] + coordK[m]
                lengthZ = abs(centreZ - coordZ[m])
                lengthX = abs(centreX - coordX[m]) 
                alfa = atan2(lengthZ,lengthX) 
                zz= (radius-offset)*sin(alfa)
                xx= (radius-offset)*cos(alfa)
                pointZ=centreZ-zz
                if (coordX[m]<centreX):
                    pointX=centreX-xx
                else:
                    pointX=centreX+xx
                if (line_or_arc[m] == 3): 
                    if (line_or_arc[m-1] == 1): 
                        if (angle[m-1] - alfa < -0.2):
                            print '(G03:ARC)(ANGLE:angle[m-1] - alfa < -0.2)(next:LINE)'#DXF arc_G3_line<.dxf
                            cw_zz = (radius+offset)*sin(alfa)
                            cw_xx = (radius+offset)*cos(alfa)
                            cw_pointZ= centreZ+cw_zz
                            cw_pointX= centreX+cw_xx                                     
                            string=ser.join(['G3','X',str(cw_pointX),'Z',str(cw_pointZ),'R',str(radius+offset)])
                            ins = program.append(string)
                            part_n+=1
                            fapp(part_n,3,cw_pointX,cw_pointZ,P,radius+offset,centreX,centreZ)
                            '''part_n+=1 
                            P.append([])
                            P[part_n].append(3)
                            P[part_n].append(P[part_n-1][3])
                            P[part_n].append(P[part_n-1][4])                                               
                            P[part_n].append(cw_pointX)
                            P[part_n].append(cw_pointZ)
                            P[part_n].append(radius+offset)
                            P[part_n].append(centreX)
                            
                            P[part_n].append(centreZ)''' 
                            string=ser.join(['G3','X',str(coordX[m]+cos(angle[m-1])*offset),
                                                  'Z',str(coordZ[m]+sin(angle[m-1])*offset),'R',str(offset)])
                            ins = program.append(string)
                            part_n+=1 
                            P.append([])
                            P[part_n].append(3)
                            P[part_n].append(P[part_n-1][3])
                            P[part_n].append(P[part_n-1][4])                                               
                            P[part_n].append(coordX[m]+cos(angle[m-1])*offset)
                            P[part_n].append(coordZ[m]+sin(angle[m-1])*offset)
                            P[part_n].append(offset)
                            P[part_n].append(coordX[m])
                            P[part_n].append(coordZ[m])  
                        elif (angle[m-1] - alfa > 0.2):
                            print '(G03:ARC)(ANGLE:angle[m-1] - alfa > 0.2)(next:LINE)'#DXF arc_G3_line>.dxf
                            radius_and_off = radius+offset
                            if m==0:
                                arc_itrs_lineZ,arc_itrs_lineX = coordZ[m],coordX[m]+offset
                            else:
                                arc_itrs_lineZ,arc_itrs_lineX = intersection_line_arc(3,coordZ[m]+sin(angle[m-1])*offset,
                                                                                     coordX[m]+cos(angle[m-1])*offset,
                                                                                     coordZ[m-1]+sin(angle[m-1])*offset,
                                                                                     coordX[m-1]+cos(angle[m-1])*offset,
                                                                                     centreZ,centreX,radius_and_off)
                            string=ser.join(['G3','X',str(arc_itrs_lineX),'Z',str(arc_itrs_lineZ),'R',str(radius_and_off)])
                            ins = program.append(string)
                            part_n+=1 
                            P.append([])
                            P[part_n].append(3)
                            P[part_n].append(P[part_n-1][3])
                            P[part_n].append(P[part_n-1][4])                                               
                            P[part_n].append(arc_itrs_lineX)
                            P[part_n].append(arc_itrs_lineZ)
                            P[part_n].append(radius_and_off)
                            P[part_n].append(centreX)
                            P[part_n].append(centreZ) 
                        else:      
                            print 'G03:ARC   next:LINE angle[m-1] == alfa' #DXF arc_G3_line=.dxf  
                            string=ser.join(['G3','X',str(coordX[m]+cos(angle[m-1])*offset),
                                                'Z',str(coordZ[m]+sin(angle[m-1])*offset),'R',str(radius+offset)])
                            ins = program.append(string)
                            part_n+=1 
                            P.append([])
                            P[part_n].append(3)
                            P[part_n].append(P[part_n-1][3])
                            P[part_n].append(P[part_n-1][4])                                               
                            P[part_n].append(coordX[m]+cos(angle[m-1])*offset)
                            P[part_n].append(coordZ[m]+sin(angle[m-1])*offset)
                            P[part_n].append(radius+offset)
                            P[part_n].append(centreX)
                            P[part_n].append(centreZ)                              
                    else:  #если дуга G3  и следующая дуга G3 
                        NEXT_radius = sqrt((coordK[m-1])*(coordK[m-1]) + (coordI[m-1])*(coordI[m-1]))
                        NEXT_centreX = coordX[m] + coordI[m-1]
                        NEXT_centreZ = coordZ[m] + coordK[m-1] 
                        NEXT_lengthZ = abs(NEXT_centreZ - coordZ[m])
                        NEXT_lengthX = abs(NEXT_centreX - coordX[m]) 
                        NEXT_alfa = atan2(NEXT_lengthZ,NEXT_lengthX)
                        NEXT_zz= (NEXT_radius-offset)*sin(NEXT_alfa)
                        NEXT_xx= (NEXT_radius-offset)*cos(NEXT_alfa)
                        print 'NEXT_radius=', NEXT_radius
                        print 'NEXT_centreX=', NEXT_centreX
                        print 'NEXT_centreZ=', NEXT_centreZ
                        print 'NEXT_lengthZ=', NEXT_lengthZ
                        print 'NEXT_lengthX=', NEXT_lengthX
                        print 'NEXT_alfa=', NEXT_alfa
                        print 'NEXT_zz=', NEXT_zz
                        print 'NEXT_xx=', NEXT_xx
                        print 'coordX[m]=', coordX[m]
                        print 'coordZ[m]=', coordZ[m]                        
                        if (line_or_arc[m-1] == 3):   
                            print 'G03:ARC  next:ARC_G03'
                            NEXT_X,NEXT_Z=intersection_arc_arc(NEXT_centreX,NEXT_centreZ, 
                                                               NEXT_radius+offset,centreX,centreZ,radius+offset,
                                                               coordX[m],coordZ[m])                
                            string=ser.join(['G3','X',str(NEXT_X),
                                            'Z',str(NEXT_Z),'R',str(radius+offset)])
                            ins = program.append(string)
                            part_n+=1
                            fapp(part_n,3,NEXT_X,NEXT_Z,P,radius+offset,centreX,centreZ)
                                ########################################
                        if (line_or_arc[m-1] == 2): 
                            if angle[m] < angle[m-1]:#TODO
                                print 'G03:ARC ANGLE:ccw next:ARC_G02'
                            else:     #TODO
                                print 'G03:ARC ANGLE:cw next:ARC_G02' 
                else: #если участок "дуга" CCW  
                    if (line_or_arc[m-1] == 1): 
                        if (angle[m-1] - alfa < -0.2):
                            print '(G02:ARC) (angle[m-1] - alfa < -0.2) (next:LINE)'#DXF arc_G2_line<.dxf
                            string=ser.join(['G2','X',str(pointX),'Z',str(pointZ),'R',str(radius-offset)])
                            ins = program.append(string)
                            part_n+=1 
                            P.append([])
                            P[part_n].append(2)
                            P[part_n].append(P[part_n-1][3])
                            P[part_n].append(P[part_n-1][4])                                               
                            P[part_n].append(pointX)
                            P[part_n].append(pointZ)
                            P[part_n].append(radius-offset)
                            P[part_n].append(centreX)
                            P[part_n].append(centreZ) 
                            string=ser.join(['G3','X',str(coordX[m]+cos(angle[m-1])*offset),
                                                  'Z',str(coordZ[m]+sin(angle[m-1])*offset),'R',str(offset)])
                            if m:                      
                                ins = program.append(string)
                                part_n+=1 
                                P.append([])
                                P[part_n].append(3)
                                P[part_n].append(P[part_n-1][3])
                                P[part_n].append(P[part_n-1][4])                                               
                                P[part_n].append(coordX[m]+cos(angle[m-1])*offset)
                                P[part_n].append(coordZ[m]+sin(angle[m-1])*offset)
                                P[part_n].append(offset)
                                P[part_n].append(coordX[m])
                                P[part_n].append(coordZ[m]) 
                        elif (angle[m-1] - alfa > 0.2):
                            '(G02:ARC)(ANGLE:angle[m-1] - alfa > 0.2)(next:LINE)'      
                            radius_and_off = radius-offset
                            if m==0:
                                arc_itrs_lineZ,arc_itrs_lineX = coordZ[m],coordX[m]+offset
                            else:
                                arc_itrs_lineZ,arc_itrs_lineX = intersection_line_arc(2,coordZ[m]+sin(angle[m-1])*offset,
                                                                                     coordX[m]+cos(angle[m-1])*offset,
                                                                                     coordZ[m-1]+sin(angle[m-1])*offset,
                                                                                     coordX[m-1]+cos(angle[m-1])*offset,
                                                                                     centreZ,centreX,radius_and_off)
                            string=ser.join(['G2','X',str(arc_itrs_lineX),'Z',str(arc_itrs_lineZ),'R',str(radius_and_off)])
                            ins = program.append(string)
                            part_n+=1 
                            P.append([])
                            P[part_n].append(2)
                            P[part_n].append(P[part_n-1][3])
                            P[part_n].append(P[part_n-1][4])                                               
                            P[part_n].append(arc_itrs_lineX)
                            P[part_n].append(arc_itrs_lineZ)
                            P[part_n].append(radius_and_off)
                            P[part_n].append(centreX)
                            P[part_n].append(centreZ)  
                        else:
                            print 'G02:ARC   next:LINE angle[m-1] == alfa'
                            string=ser.join(['G2','X',str(coordX[m]+cos(angle[m-1])*offset),
                                                'Z',str(coordZ[m]+sin(angle[m-1])*offset),'R',str(radius-offset)])
                            ins = program.append(string)
                            part_n+=1 
                            P.append([])
                            P[part_n].append(2)
                            P[part_n].append(P[part_n-1][3])
                            P[part_n].append(P[part_n-1][4])                                               
                            P[part_n].append(coordX[m]+cos(angle[m-1])*offset)
                            P[part_n].append(coordZ[m]+sin(angle[m-1])*offset)
                            P[part_n].append(radius-offset)
                            P[part_n].append(centreX)
                            P[part_n].append(centreZ)
                            
                    else:                   
                        if (line_or_arc[m-1] == 3): 
                            if angle[m] < angle[m-1]: #TODO
                                print 'G02:ARC  ANGLE:ccw next:ARC_G03'
                            else:       #TODO
                                print 'G02:ARC  ANGLE:cw next:ARC_G03' 
                        if (line_or_arc[m-1] == 2): 
                            if angle[m] < angle[m-1]:#TODO
                                print 'G02:ARC ANGLE:ccw next:ARC_G02'
                            else:      #TODO
                                print 'G02:ARC ANGLE:cw next:ARC_G02'
        flag_micro_part = 0
        coordZ_start =FIRST_pointZ
        bounce = 0.5 
        self.execute("G21 G18")
        self.execute("G61")
        COORDx0 = P[len(P)-1][3] 
        self.execute("G1 X%f " % (COORDx0))
        if flag_executed :
            i = len(P)-1
            if only_finishing_cut==0 :
                if COORDx0 - P[len(P)-1][1] <= d:
                    d=0
                while COORDx0 - P[i][1] >= d :
                    d = float(words['d'])                                   
                    if P[i][0] == 1:
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
                        Mx1 = P[i][3]
                        Mz2 = P[i][4]
                        Mx2 = P[i][3] 
                        B=COORDx0                           
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
                    elif P[i][0] == 3:
                        Mz1 = P[i][2]
                        Mx1 = P[i][3]
                        Mz2 = P[i][4]
                        Mx2 = P[i][3] 
                        B=COORDx0                           
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
                                COORDz0=z1
                            else:
                                COORDz0=z2
                    self.execute("G1  Z%f" % ((COORDz0)))
                    if bounce > coordZ_start - COORDz0:
                        self.execute("G0 X%f Z%f" % ((COORDx0),(coordZ_start)))
                    else:
                        self.execute("G0 X%f Z%f" % ((COORDx0+bounce),(COORDz0+bounce)))
                        self.execute("G0 Z%f" % (coordZ_start))

                    COORDx0 = COORDx0 - d
                    for next_i in reversed(range(len(P))): 
                        if P[next_i][3] > COORDx0 > P[next_i][1]:
                            i=next_i                     
                    self.execute("G1 X%f " % (COORDx0)) 
                    if flag_micro_part :                    
                        if COORDx0 - P[i][1] < d and P[i][3] > COORDx0 > P[i][1]:
                            d=0
                            flag_micro_part = 1
                        else:
                            flag_micro_part = 0
                        continue
                    if COORDx0 - P[i][1] < d:
                        if P[i][0] == 1:
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
                            self.execute("G1  Z%f" % ((COORDz0)))
                            if bounce > coordZ_start - COORDz0:
                                self.execute("G0 X%f Z%f" % ((COORDx0),(coordZ_start)))
                            else:
                                self.execute("G0 X%f Z%f" % ((COORDx0+bounce),(COORDz0+bounce)))
                                self.execute("G0 Z%f" % (coordZ_start))
                            if i>1:
                                COORDx0 = COORDx0 - d 
                                for next_i in reversed(range(len(P))): 
                                    if P[next_i][3] > COORDx0 > P[next_i][1]:
                                        i=next_i                                  
                                if COORDx0 - P[i][1] < d and P[i][3] > COORDx0 > P[i][1]:
                                    d=0
                                    flag_micro_part = 1                                
                                self.execute("G1 X%f " % (COORDx0)) 
                        elif P[i][0] == 2:
                            Mz1 = P[i][2]
                            Mx1 = P[i][3]
                            Mz2 = P[i][4]
                            Mx2 = P[i][3] 
                            B=COORDx0                           
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
                            self.execute("G1  Z%f" % ((COORDz0)))                           
                            if bounce > coordZ_start - COORDz0:
                                self.execute("G0 X%f Z%f" % ((COORDx0),(coordZ_start)))
                            else:
                                self.execute("G0 X%f Z%f" % ((COORDx0+bounce),(COORDz0+bounce)))
                                self.execute("G0 Z%f" % (coordZ_start))
                            if i>1:
                                COORDx0 = COORDx0 - d 
                                for next_i in reversed(range(len(P))): 
                                    if P[next_i][3] > COORDx0 > P[next_i][1]:
                                        i=next_i                                  
                                if COORDx0 - P[i][1] < d and P[i][3] > COORDx0 > P[i][1]:
                                    d=0
                                    flag_micro_part = 1                                
                                self.execute("G1 X%f " % (COORDx0))                                 
                        elif P[i][0] == 3:
                            Mz1 = P[i][2]
                            Mx1 = P[i][3]
                            Mz2 = P[i][4]
                            Mx2 = P[i][3] 
                            B=COORDx0                           
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
                            self.execute("G1  Z%f" % ((COORDz0)))                          
                            if bounce > coordZ_start - COORDz0:
                                self.execute("G0 X%f Z%f" % ((COORDx0),(coordZ_start)))
                            else:
                                self.execute("G0 X%f Z%f" % ((COORDx0+bounce),(COORDz0+bounce)))
                                self.execute("G0 Z%f" % (coordZ_start))
                            if i>1:
                                COORDx0 = COORDx0 - d 
                                for next_i in reversed(range(len(P))): 
                                    if P[next_i][3] > COORDx0 > P[next_i][1]:
                                        i=next_i                                  
                                if COORDx0 - P[i][1] < d and P[i][3] > COORDx0 > P[i][1]:
                                    d=0
                                    flag_micro_part = 1                                
                                self.execute("G1 X%f " % (COORDx0)) 
                        
            else:
                MESSAGE("Only finishing cut") 
                self.execute("M0")                          
#######################################################                                                           
        flag_executed = 0                                            
        for w in program:
            try:  
                self.execute(w)
            except InterpreterException,e:
                        msg = "%d: '%s' - %s" % (e.line_number,e.line_text, e.error_message)
                        self.set_errormsg(msg) 
                        return INTERP_ERROR  
        offset-=offset_mem/quantity
        program = []
        self.execute("G0  Z%f" % (coordZ_start))     
 #####################################################
    print 'P =', P 
    self.execute("G40 " )
    self.execute("M6 T%d " % (tool))  

    #self.execute("G42" )
 #   self.execute("G0 X%f Z%f" % ((FIRST_pointX),(coordZ_start)))
#    self.execute("G1 X%f " % FIRST_pointX)                 
    for w in lines:
        if  re.search("^\s*[(]\s*N\d", w.upper()):
            if not re.search("[^\(\)\.\-\+NGZXRIK\d\s]", w.upper()):
                num2 = int(re.findall("^\s*\d*",(re.split('N',w.upper())[1]))[0])
                if num2 >= p and num2 <= q:
                    try: 
                        contour=re.split('\)',(re.split('\(',w.upper())[1]))[0]
                        self.execute(contour)
                    except InterpreterException,e:
                        msg = "%d: '%s' - %s" % (e.line_number,e.line_text, e.error_message)
                        self.set_errormsg(msg) 
                        return INTERP_ERROR 
    self.execute("G40 " )   
    self.execute("G1  Z%f" % (coordZ_start))                            
    f.close()                 
    return INTERP_OK
