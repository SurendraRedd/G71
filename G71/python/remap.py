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
    string=ser.join(['G18 G90 G49 F1000',])
    ins = program.append(string)
    for i in range(quantity):
        string=ser.join(['G1','X',str(round(coordX[mm+1]+(cos(angle[mm]))*offset,10)) ,
                              'Z',str(coordZ[mm+1]+(sin(angle[mm]))*offset),]) 
        ins = program.append(string)        
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
                        if part_n == 0 and m:
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
                        if part_n == 0 and m==0:
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
                       
                else: 
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
                    if (line_or_arc[m-1] ==3): 
                        if (angle[m] - NEXT_alfa<-0.2): 
                            print 'G01:LINE ANGLE:ccw next:ARC_G03'
                            radius_OFF = NEXT_radius+offset
                            NEXT_arc_itrs_lineZ,NEXT_arc_itrs_lineX = intersection_line_arc(coordZ[m+1]+sin(angle[m])*offset,
                                                                                  coordX[m+1]+cos(angle[m])*offset,
                                                                                  coordZ[m]+sin(angle[m])*offset,
                                                                                  coordX[m]+cos(angle[m])*offset,
                                                                                  NEXT_centreZ,NEXT_centreX,radius_OFF)
                            string=ser.join(['G1','X',str(NEXT_arc_itrs_lineX ),'Z',str(NEXT_arc_itrs_lineZ)])
                            ins = program.append(string)
                        elif (angle[m] - NEXT_alfa>0.2): 
                            print 'G01:LINE ANGLE:cw next:ARC_G03'
                            cw_next_zz = (NEXT_radius+offset)*sin(NEXT_alfa)
                            cw_next_xx = (NEXT_radius+offset)*cos(NEXT_alfa)
                            cw_next_pointZ= NEXT_centreZ+cw_next_zz
                            cw_next_pointX= NEXT_centreX+cw_next_xx
                            string=ser.join(['G1','X',str(coordX[m]+cos(angle[m])*offset),'Z',str(coordZ[m]+sin(angle[m])*offset)])
                            ins = program.append(string)                            
                            string=ser.join(['G3','X',str(cw_next_pointX),'Z',str(cw_next_pointZ),'R',str(offset)])
                            ins = program.append(string)
                        else: #angle[m] == NEXT_alfa 
                            print 'G01:LINE  angle[m] == NEXT_alfa'
                            string=ser.join(['G1','X',str(coordX[m]+cos(angle[m])*offset),'Z',str(coordZ[m]+sin(angle[m])*offset)])
                            ins = program.append(string)
                    if (line_or_arc[m-1] ==2): 
                        if (angle[m] - NEXT_alfa<-0.2):
                            print 'G01:LINE ANGLE:ccw next:ARC_G02' 
                            string=ser.join(['G1','X',str(coordX[m]+cos(angle[m])*offset),'Z',str(coordZ[m]+sin(angle[m])*offset)])
                            ins = program.append(string)
                        elif (angle[m] - NEXT_alfa>0.2): 
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
                            cw_zz = (radius+offset)*sin(alfa)
                            cw_xx = (radius+offset)*cos(alfa)
                            cw_pointZ= centreZ+cw_zz
                            cw_pointX= centreX+cw_xx                                     
                            string=ser.join(['G3','X',str(cw_pointX),'Z',str(cw_pointZ),'R',str(radius+offset)])
                            ins = program.append(string)
                            string=ser.join(['G3','X',str(coordX[m]+cos(angle[m-1])*offset),
                                                  'Z',str(coordZ[m]+sin(angle[m-1])*offset),'R',str(offset)])
                            ins = program.append(string) 
                        elif (angle[m-1] - alfa > 0.2):
                            print 'G03:ARC  ANGLE:cw next:LINE'
                            radius_and_off = radius+offset
                            arc_itrs_lineZ,arc_itrs_lineX = intersection_line_arc(coordZ[m]+sin(angle[m-1])*offset,
                                                                                 coordX[m]+cos(angle[m-1])*offset,
                                                                                 coordZ[m-1]+sin(angle[m-1])*offset,
                                                                                 coordX[m-1]+cos(angle[m-1])*offset,
                                                                                 centreZ,centreX,radius_and_off)
                            string=ser.join(['G3','X',str(arc_itrs_lineX),'Z',str(arc_itrs_lineZ),'R',str(radius_and_off)])
                            ins = program.append(string)                
                        else:      
                            print 'G03:ARC   next:LINE angle[m-1] == NEXT_alfa'

                            string=ser.join(['G3','X',str(coordX[m]+cos(angle[m-1])*offset),
                                                'Z',str(coordZ[m]+sin(angle[m-1])*offset),'R',str(radius+offset)])
                            ins = program.append(string)                            
                    else:                    
                        if (line_or_arc[m-1] == 3): 
                            if angle[m] < angle[m-1]: #TODO
                                print 'G03:ARC  ANGLE:ccw next:ARC_G03'
                            else:    #TODO
                                print 'G03:ARC  ANGLE:cw next:ARC_G03'
                                ########################################
                        if (line_or_arc[m-1] == 2): 
                            if angle[m] < angle[m-1]:#TODO
                                print 'G03:ARC ANGLE:ccw next:ARC_G02'
                            else:     #TODO
                                print 'G03:ARC ANGLE:cw next:ARC_G02' 
                else: 
                    if (line_or_arc[m-1] == 1): 
                        if angle[m] < angle[m-1]:
                            print 'G02:ARC ANGLE:ccw next:LINE'
                            string=ser.join(['G2','X',str(pointX),'Z',str(pointZ),'R',str(radius)])
                            ins = program.append(string)
                            string=ser.join(['G3','X',str(coordX[m]+cos(angle[m-1])*offset),
                                                  'Z',str(coordZ[m]+sin(angle[m-1])*offset),'R',str(offset)])
                            ins = program.append(string)
                        else:       
                            print 'G02:ARC  ANGLE:cw next:LINE'
                            string=ser.join(['G2','X',str(pointX),'Z',str(pointZ),'R',str(radius)])
                            ins = program.append(string)
                            string=ser.join(['G3','X',str(coordX[m]+cos(angle[m-1])*offset),
                                                  'Z',str(coordZ[m]+sin(angle[m-1])*offset),'R',str(offset)])
                            #ins = program.append(string)
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
        coordZ_start +=(sin(angle[mm]))*offset
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
                    self.execute("G1  Z%f" % ((COORDz0)))
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
                            self.execute("G0 X%f Z%f" % ((COORDx0+bounce),(COORDz0+bounce)))
                            self.execute("G0 Z%f" % (coordZ_start))
                            if i:
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
    self.execute("M6 T%d " % (tool))         
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
    self.execute("G0  Z%f" % (coordZ_start))                            
    f.close()                 
    return INTERP_OK

