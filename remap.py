# --*-- coding:utf-8 --*--
import sys
sys.path.insert(0,'/home/nkp/git/linuxcnc/lib/python/')
import linuxcnc
import re
from math import *
import traceback
from interpreter import *
from emccanon import MESSAGE, SET_MOTION_OUTPUT_BIT, CLEAR_MOTION_OUTPUT_BIT,SET_AUX_OUTPUT_BIT,CLEAR_AUX_OUTPUT_BIT
from util import lineno, call_pydevd

throw_exceptions = 1 # raises InterpreterException if execute() or read() fail

    
def pars(array,reg ,lines): 
    a=array.insert(0,(float(re.search(reg,lines, re.I).group(1))))
def cathetus(c,b):
    a = sqrt(abs(c*c - b*b))
    return a 
def hip(a,b):
    c = sqrt(abs(a*a + b*b))
    return c
def intersection_line_arc(Mz1,Mx1,Mz2,Mx2,centreZ,centreX,radius):    
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
        if Mz2 < z1 < Mz1:
          pointZ1 = z1                                                            
          pointX1 = K*z1+B
          return  pointZ1,pointX1
        else:
          pointZ1 = z2
          pointX1 = K*z2+B
          return  pointZ1,pointX1  
           
#################################################-----G71.2
def g712(self, **words):
    """ remap code G71.2 """
    p = int(words['p'])
    feed_rate = int(words['f'])
    q = int(words['q'])
    d = float(words['d'])
    l = float(words['k'])
    h = float(words['i'])
    offset = float(words['j'])# чистовой проход,мм
    only_finishing_cut = int(words['s'])#  об. шпинделя при чист.обработке(вариант onli_finish_cut)
    quantity = int(words['l'])# количество чистовых проходов 
    #tool = float(words['t'])
    s = linuxcnc.stat() 
    s.poll()
    #backangle  =  s.tool_table #TODO проверка угла резца
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
                if num == p : # вычисляем Start_point по Z
                    temp_x = x
                    a=2
                    while not re.search("^\s*.*Z", lines[temp_x-a].upper()):
                        a+=1
                    coordZ_start = float(re.search("Z\s*([-0-9.]+)",lines[temp_x-a], re.I).group(1))   
        x+=1 
 ######################################################
    print ' +++++++++++++++++++++++++++++++++++++++'
    print 'coordZ=', coordZ
    print 'coordX=', coordX
    print 'line_or_arc=', line_or_arc
    print 'coordI=', coordI
    print 'coordK=', coordK
    print 'coordZ_start=', coordZ_start
    print ' +++++++++++++++++++++++++++++++++++++++'
    
    angle = [] #угол участка траектории к оси Z
    angle_deg = [] #TEMP TODO

    for n in range(len(coordZ)-1):
        print 'n =',n
        lengthZ = abs(coordZ[n] - coordZ[n+1])
        lengthX = abs(coordX[n] - coordX[n+1])             
        print 'angle =',degrees(atan2(lengthX,lengthZ))+180
        print '==========================='        
        app = angle.append(atan2(lengthX,lengthZ))
        DEG=int(degrees(atan2(lengthX,lengthZ)))+180
        app = angle_deg.append(DEG)
    app = angle.append(0.2914567944778671)
    print 'angle =',angle
    print 'angle_deg =',angle_deg
    print 'line_or_arc=', line_or_arc           
    '''for n in range(v):
        print 'n=' , n
        COORDx0 =  coordX[n]
        COORDz0 =  coordZ[n]
        lengthZ = abs(COORDz0 - coordZ[n+1])
        lengthX = abs(COORDx0 - coordX[n+1])
        if (COORDz0 - coordZ[n+1]) >= 0.01:# наклон "отрицательный"
            incline = 1   #TODO проверка угла резца
            print 'angle < 0' , incline
            self.execute("(MSG,angle < 0)",lineno())
        else: 
            incline = 0
        if lengthX == 0 :#горизонтальная линия
            delta = 0
            l = lengthZ +l
        elif lengthZ == 0 : #вертикальная линия
            delta = 0
            l = float(words['k'])
        else:  
            tangent = lengthX/lengthZ
            delta = d/tangent

            l = float(words['k'])
            if  tangent < 0.3:
                l = 4l                         
        if line_or_arc[n] > 1:
            if len(coordR) :
                pass
                #radius = coordR[n+1]
            else:
                print ' ARC  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
                radius = hip(coordK[n],coordI[n])
                centreX = coordX[n+1] + coordI[n]
                centreZ = coordZ[n+1] + coordK[n]'''                                

 ##################################07.11.2016 offset по g-коду
    part_n = -1
    flag_executed = 1 # чистовых может быть несколько ,но основной цикл только один
    P = [] #массив массивов данных по каждому контуру
    program = [] # массив строк g-кода траектории с отступом на чистовую обработку
    offset_mem=offset
    mm=int(len(angle)-2)
    ser=' '
    self.execute("F%f" % feed_rate,lineno())
    string=ser.join(['G18 G90 G49 F1000',])
    ins = program.append(string)
    for qq in range(quantity):
        string=ser.join(['G1','X',str(round(coordX[mm+1]+(cos(angle[mm]))*offset,10)) ,
                              'Z',str(coordZ[mm+1]+(sin(angle[mm]))*offset),]) # IMG 2.png
        ins = program.append(string)        
        for m in (reversed(range(len(angle)-1))):   
            print 'm =', m
            if (line_or_arc[m] ==1): #если участок "линия"
                if (line_or_arc[m-1] ==1): #если СЛЕДУЮЩИЙ участок "линия"
                    if angle[m-1] < angle[m]: #если угол следующего участка cw IMG(5.png)
                        print 'G01:LINE ANGLE:cw next:LINE'
                        if m==0:
                            print 'm =0', m
                            string=ser.join(['G1','X',str(coordX[m]+cos(angle[m])*offset),
                                                  'Z',str(coordZ[m]+sin(angle[m])*offset)])
                            ins = program.append(string)
                        else:
                            string=ser.join(['G1','X',str(coordX[m]+cos(angle[m])*offset),
                                                  'Z',str(coordZ[m]+sin(angle[m])*offset),])
                            ins = program.append(string)
                            print 'm !=0', m                   
                        if m!=0:
                            string=ser.join(['G3','X',str(coordX[m]+cos(angle[m-1])*offset),
                                        'Z',str(coordZ[m]+sin(angle[m-1])*offset),'R',str(offset),])
                            ins = program.append(string)
                        part_n+=1
                        P.append([])
                        P[part_n].append(1) 
                        if part_n == 0 and m:# если первый ,но не последний
                            P[part_n].append(coordX[mm+1]+(cos(angle[mm]))*offset)
                            P[part_n].append(coordZ[mm+1]+(sin(angle[mm]))*offset)
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
                            continue
                        if part_n == 0 and m==0:# если первый ,и он же  последний
                            P[part_n].append(coordX[mm+1]+(cos(angle[mm]))*offset)
                            P[part_n].append(coordZ[mm+1]+(sin(angle[mm]))*offset)
                            P[part_n].append(coordX[m]+cos(angle[m])*offset)
                            P[part_n].append(coordZ[m]+sin(angle[m])*offset)
                            continue    
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
                    else:       #если угол следующего участка ccw IMG(4.png)                         
                        print 'G01:LINE ANGLE:ccw next:LINE'
                        angl = (angle[m] - angle[m-1])/2 
                        gg =  offset / cos(angl)
                        angl1 = angle[m] - angl

                        string=ser.join(['G1','X',str(coordX[m]+cos(angl1)*gg),'Z',str(coordZ[m]+sin(angl1)*gg),])  
                        ins = program.append(string)
                        part_n+=1
                        P.append([])
                        P[part_n].append(1)
                        if part_n == 0:
                            P[part_n].append(coordX[mm+1]+(cos(angle[mm]))*offset)
                            P[part_n].append(coordZ[mm+1]+(sin(angle[mm]))*offset)
                            P[part_n].append(coordX[m]+cos(angl1)*gg)
                            P[part_n].append(coordZ[m]+sin(angl1)*gg)
                            continue
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
                    NEXT_alfa = atan2(NEXT_lengthZ,NEXT_lengthX)#IMG(3.png)
                    NEXT_zz= (NEXT_radius-offset)*sin(NEXT_alfa)
                    NEXT_xx= (NEXT_radius-offset)*cos(NEXT_alfa)
                    NEXT_pointX=NEXT_centreX-NEXT_xx
                    if (coordZ[m]<NEXT_centreZ):#взаиморасположение центра и начала дуги
                        NEXT_pointZ=NEXT_centreZ-NEXT_zz
                    else:
                        NEXT_pointZ=NEXT_centreZ+NEXT_zz
                    if (line_or_arc[m-1] ==3): #если СЛЕДУЮЩИЙ участок "дуга" CW
                        if (angle[m] - NEXT_alfa<-0.2): #угол line к next_arc 
                            print 'G01:LINE ANGLE:ccw next:ARC_G03'
                            radius_OFF = NEXT_radius+offset
                            NEXT_arc_itrs_lineZ,NEXT_arc_itrs_lineX = intersection_line_arc(coordZ[m+1]+sin(angle[m])*offset,
                                                                                  coordX[m+1]+cos(angle[m])*offset,
                                                                                  coordZ[m]+sin(angle[m])*offset,
                                                                                  coordX[m]+cos(angle[m])*offset,
                                                                                  NEXT_centreZ,NEXT_centreX,radius_OFF)
                            string=ser.join(['G1','X',str(NEXT_arc_itrs_lineX ),'Z',str(NEXT_arc_itrs_lineZ)])
                            ins = program.append(string)
                        elif (angle[m] - NEXT_alfa>0.2): #угол line к next_arc IMG(6.png)
                            print 'G01:LINE ANGLE:cw next:ARC_G03'
                            cw_next_zz = (NEXT_radius+offset)*sin(NEXT_alfa)
                            cw_next_xx = (NEXT_radius+offset)*cos(NEXT_alfa)
                            cw_next_pointZ= NEXT_centreZ+cw_next_zz
                            cw_next_pointX= NEXT_centreX+cw_next_xx
                            print 'cw_next_pointZ=' , cw_next_pointZ
                            print 'cw_next_pointX=' , cw_next_pointX
                            string=ser.join(['G1','X',str(coordX[m]+cos(angle[m])*offset),'Z',str(coordZ[m]+sin(angle[m])*offset)])
                            ins = program.append(string)                            
                            string=ser.join(['G3','X',str(cw_next_pointX),'Z',str(cw_next_pointZ),'R',str(offset)])
                            ins = program.append(string)
                        else: #angle[m] == NEXT_alfa 
                            print 'G01:LINE  angle[m] == NEXT_alfa'
                            string=ser.join(['G1','X',str(coordX[m]+cos(angle[m])*offset),'Z',str(coordZ[m]+sin(angle[m])*offset)])
                            ins = program.append(string)
                    if (line_or_arc[m-1] ==2): #если СЛЕДУЮЩИЙ участок "дуга" CCW
                        if (angle[m] - NEXT_alfa<-0.2):##угол следующего участка
                            print 'G01:LINE ANGLE:ccw next:ARC_G02' 
                            string=ser.join(['G1','X',str(coordX[m]+cos(angle[m])*offset),'Z',str(coordZ[m]+sin(angle[m])*offset)])
                            ins = program.append(string)
                        elif (angle[m] - NEXT_alfa>0.2): #угол line к next_arc
                            print 'G01:LINE ANGLE:cw next:ARC_G02'
                            string=ser.join(['G1','X',str(coordX[m]+cos(angle[m])*offset),'Z',str(coordZ[m]+sin(angle[m])*offset)])
                            ins = program.append(string)
                            string=ser.join(['G3','X',str(NEXT_pointX),'Z',str(NEXT_pointZ),'R',str(offset)])
                            ins = program.append(string) 
                        else:       #angle[m] == NEXT_alfa
                            print 'G01:LINE  next:ARC_G02 angle[m] == NEXT_alfa'
                            string=ser.join(['G1','X',str(coordX[m]+cos(angle[m])*offset),'Z',str(coordZ[m]+sin(angle[m])*offset)])
                            ins = program.append(string)
                            #string=ser.join(['G3','X',str(NEXT_pointX),'Z',str(NEXT_pointZ),'R',str(offset)])
                            #ins = program.append(string)          
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            else:  #если участок "дуга"
                radius = sqrt((coordK[m])*(coordK[m]) + (coordI[m])*(coordI[m]))
                centreX = coordX[m+1] + coordI[m]
                centreZ = coordZ[m+1] + coordK[m]
                lengthZ = abs(centreZ - coordZ[m])
                lengthX = abs(centreX - coordX[m]) 
                alfa = atan2(lengthZ,lengthX) #IMG(2.png)
                zz= (radius-offset)*sin(alfa)
                xx= (radius-offset)*cos(alfa)
                #pointX=centreX-xx
                pointZ=centreZ-zz
                if (coordX[m]<centreX):#взаиморасположение центра и начала дуги
                    pointX=centreX-xx
                else:
                    pointX=centreX+xx
                print 'coordX[m]=', coordX[m]
                print 'coordZ[m]=', coordZ[m] 
                print 'coordX[m+1]=', coordX[m+1]
                print 'coordZ[m+1]=', coordZ[m+1] 
                print 'coordX[m-1]=', coordX[m-1]
                print 'coordZ[m-1]=', coordZ[m-1]
                print 'pointX=', pointX
                print 'pointZ=', pointZ
                print 'radius-offset=', radius-offset
                print 'xx=', xx
                print 'zz=', zz
                print 'alfa=', degrees(alfa)
                print 'lengthZ=', lengthZ
                print 'lengthX=', lengthX
                print 'radius=', radius
                print 'centreX=', centreX
                print 'centreZ=', centreZ
                print 'angle[m]=', degrees(angle[m])
                print 'angle[m+1]=', degrees(angle[m+1])
                print 'angle[m-1]=', degrees(angle[m-1])
                if (line_or_arc[m] == 3): #если участок "дуга" CW
                    if (line_or_arc[m-1] == 1): #если СЛЕДУЮЩИЙ участок "линия" IMG(1.png)
                        if (angle[m-1] - alfa < -0.2):#угол следующего участка
                            cw_zz = (radius+offset)*sin(alfa)
                            cw_xx = (radius+offset)*cos(alfa)
                            cw_pointZ= centreZ+cw_zz
                            cw_pointX= centreX+cw_xx                                     
                            string=ser.join(['G3','X',str(cw_pointX),'Z',str(cw_pointZ),'R',str(radius+offset)])
                            ins = program.append(string)
                            string=ser.join(['G3','X',str(coordX[m]+cos(angle[m-1])*offset),
                                                  'Z',str(coordZ[m]+sin(angle[m-1])*offset),'R',str(offset)])
                            ins = program.append(string) 
                        elif (angle[m-1] - alfa > 0.2):#угол следующего участка 
                            print 'G03:ARC  ANGLE:cw next:LINE'
                            radius_and_off = radius+offset
                            arc_itrs_lineZ,arc_itrs_lineX = intersection_line_arc(coordZ[m]+sin(angle[m-1])*offset,
                                                                                 coordX[m]+cos(angle[m-1])*offset,
                                                                                 coordZ[m-1]+sin(angle[m-1])*offset,
                                                                                 coordX[m-1]+cos(angle[m-1])*offset,
                                                                                 centreZ,centreX,radius_and_off)
                            string=ser.join(['G3','X',str(arc_itrs_lineX),'Z',str(arc_itrs_lineZ),'R',str(radius_and_off)])
                            ins = program.append(string)                
                        else:       #angle[m-1] == NEXT_alfa IMG(bug.png)
                            print 'G03:ARC   next:LINE angle[m-1] == NEXT_alfa'

                            string=ser.join(['G3','X',str(coordX[m]+cos(angle[m-1])*offset),
                                                'Z',str(coordZ[m]+sin(angle[m-1])*offset),'R',str(radius+offset)])
                            ins = program.append(string)                            

                    else:                     #если СЛЕДУЮЩИЙ участок "дуга"
                        if (line_or_arc[m-1] == 3): #если СЛЕДУЮЩИЙ участок "дуга" CW 
                            if angle[m] < angle[m-1]: #угол следующего участка#TODO
                                print 'G03:ARC  ANGLE:ccw next:ARC_G03'
                            else:       #угол следующего участка#TODO
                                print 'G03:ARC  ANGLE:cw next:ARC_G03'
                                ############################################################################# 
                        if (line_or_arc[m-1] == 2): #если СЛЕДУЮЩИЙ участок "дуга" CCW
                            if angle[m] < angle[m-1]:##угол следующего участка#TODO
                                print 'G03:ARC ANGLE:ccw next:ARC_G02'
                            else:       #угол следующего участка#TODO
                                print 'G03:ARC ANGLE:cw next:ARC_G02' 
                else: #если участок "дуга" CCW
                    if (line_or_arc[m-1] == 1): #если СЛЕДУЮЩИЙ участок "линия"
                        if angle[m] < angle[m-1]:#угол следующего участка
                            print 'G02:ARC ANGLE:ccw next:LINE'
                            string=ser.join(['G2','X',str(pointX),'Z',str(pointZ),'R',str(radius)])
                            ins = program.append(string)
                            string=ser.join(['G3','X',str(coordX[m]+cos(angle[m-1])*offset),
                                                  'Z',str(coordZ[m]+sin(angle[m-1])*offset),'R',str(offset)])
                            ins = program.append(string)
                        else:       #угол следующего участка
                            print 'G02:ARC  ANGLE:cw next:LINE'
                            string=ser.join(['G2','X',str(pointX),'Z',str(pointZ),'R',str(radius)])
                            ins = program.append(string)
                            string=ser.join(['G3','X',str(coordX[m]+cos(angle[m-1])*offset),
                                                  'Z',str(coordZ[m]+sin(angle[m-1])*offset),'R',str(offset)])
                            #ins = program.append(string)
                    else:                     #если СЛЕДУЮЩИЙ участок "дуга"
                        if (line_or_arc[m-1] == 3): #если СЛЕДУЮЩИЙ участок "дуга" CW
                            if angle[m] < angle[m-1]: #угол следующего участка#TODO
                                print 'G02:ARC  ANGLE:ccw next:ARC_G03'
                            else:       #угол следующего участка#TODO
                                print 'G02:ARC  ANGLE:cw next:ARC_G03' 
                        if (line_or_arc[m-1] == 2): #если СЛЕДУЮЩИЙ участок "дуга" CCW
                            if angle[m] < angle[m-1]:##угол следующего участка#TODO
                                print 'G02:ARC ANGLE:ccw next:ARC_G02'
                            else:       #угол следующего участка#TODO
                                print 'G02:ARC ANGLE:cw next:ARC_G02'
        print 'program =', program
        flag_micro_part = 0
        coordZ_start +=(sin(angle[mm]))*offset
        bounce = 0.5 #величина отхода 45гр
        self.execute("F%f" % feed_rate,lineno())
        self.execute("G21 G18",lineno())
        self.execute("G61",lineno())
        COORDx0 = P[len(P)-1][3] #новая позиция по X (первый проход)
        self.execute("G1 X%f " % (COORDx0),lineno())#первый по X
        if flag_executed :
            i = int(len(P)-1)
            if only_finishing_cut==0 :
                MESSAGE("Only finishing cut") 
                self.execute("(MSG,Only finishing cut!\nResume: S)",lineno())
                self.execute("M0",lineno())

                while COORDx0 - P[i][1] >= d :
                    d = float(words['d'])                                   
                    #просчитываем новую COORDz0 :
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
                            COORDz0=P[i][2] #'vertical_line'
                    elif P[i][0] == 2:
                        pass
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
                            if Mz1 < z1 < Mz2:                                                               
                                COORDz0=z1
                            else:
                                COORDz0=z2
                    self.execute("G1  Z%f" % ((COORDz0)),lineno())#основной проход
                    self.execute("G0 X%f Z%f" % ((COORDx0+bounce),(COORDz0+bounce)),lineno())# отход 45гр
                    self.execute("G0 Z%f" % (coordZ_start),lineno())# выход в стартовую по Z

                    COORDx0 = COORDx0 - d
                    self.execute("G1 X%f " % (COORDx0),lineno()) #новая позиция по X
                    MESSAGE("переход")
                    self.execute("M1",lineno())#XXX
        
                    if COORDx0 - P[i][1] < d:
                        MESSAGE("COORDx0 - P[i][1] < d")
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
                                COORDz0=P[i][2] #'vertical_line'
                            self.execute("G1  Z%f" % ((COORDz0)),lineno())#основной проход
                            self.execute("G0 X%f Z%f" % ((COORDx0+bounce),(COORDz0+bounce)),lineno())# отход 45гр
                            self.execute("G0 Z%f" % (coordZ_start),lineno())# выход в стартовую по Z
                            if i:#если не последний проход
                                COORDx0 = COORDx0 - d 
                                for next_i in reversed(range(len(P))): #вычисляем нужное i
                                    if P[next_i][3] > COORDx0 > P[next_i][1]:
                                        i=next_i                                  
                                if COORDx0 - P[i][1] < d and P[i][3] > COORDx0 > P[i][1]:#IMG bug8.png
                                    d=0                                
                                self.execute("G1 X%f " % (COORDx0),lineno()) #новая позиция по X
                                MESSAGE("переходNEXT")
                                self.execute("M1",lineno())#XXX 
########################################################################                                                            
        flag_executed = 0 #исключить повторный основной цикл
        print 'P =', P                                             
        for w in program:
            try:  
                self.execute(w,lineno())
            except InterpreterException,e:
                        msg = "%d: '%s' - %s" % (e.line_number,e.line_text, e.error_message)
                        self.set_errormsg(msg) 
                        return INTERP_ERROR  
        offset-=offset_mem/quantity
        program = []
        self.execute("G0  Z%f" % (coordZ_start),lineno())# выход в стартовую по Z       
 ###################################################### непосредственно по контуру         
    for w in lines:
        if  re.search("^\s*[(]\s*N\d", w.upper()):
            if not re.search("[^\(\)\.\-\+NGZXRIK\d\s]", w.upper()):
                num2 = int(re.findall("^\s*\d*",(re.split('N',w.upper())[1]))[0])
                if num2 >= p and num2 <= q:
                    try: 
                        contour=re.split('\)',(re.split('\(',w.upper())[1]))[0]
                        self.execute(contour,lineno())
                    except InterpreterException,e:
                        msg = "%d: '%s' - %s" % (e.line_number,e.line_text, e.error_message)
                        self.set_errormsg(msg) 
                        return INTERP_ERROR   
    self.execute("G0  Z%f" % (coordZ_start),lineno())# выход в стартовую по Z                              
    f.close()                 
    return INTERP_OK

