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

def g886(self, **words):
    for key in words:
        MESSAGE("word '%s' = %f" % (key, words[key]))
    if words.has_key('p'):
        MESSAGE("the P word was present")
    MESSAGE("comment on this line: '%s'" % (self.blocks[self.remap_level].comment))
    return INTERP_OK
    
def pars(array,reg ,lines):
    a=array.insert(0,(float(re.search(reg,lines, re.I).group(1))))

def cathetus(c,b):
    a = sqrt(abs(c*c - b*b))
    return a   
#################################################-----G71.2
def g711(self, **words):
    """ remap code G71.1 """
    p = int(words['p'])
    feed_rate = int(words['f'])
    q = int(words['q'])
    d = float(words['d'])
    l = float(words['k'])
    h = float(words['i'])
    #tool = float(words['t'])
    s = linuxcnc.stat() 
    s.poll()
    #backangle  =  s.tool_table #TODO проверка угла резца
    #frontangle =  s.tool_table
    filename = s.file
    f = open(filename, "r")
    lines = f.readlines()
    x,v,i = 0,-1,0
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
                    g1 = line_or_arc.insert(0,(int(re.search("G\s*([0-4.]+)",lines[x], re.I).group(1))))
                    z1 = pars(coordZ,"Z\s*([-0-9.]+)",lines[x])
                    x1 = pars(coordX,"X\s*([-0-9.]+)",lines[x])                    
                    if  re.search("[I]", lines[x]):
                        i1 = pars(coordI,"I\s*([-0-9.]+)",lines[x])
                        k1 = pars(coordK,"K\s*([-0-9.]+)",lines[x])
                    if  re.search("[R]", lines[x]):
                        r1 = pars(coordR,"R\s*([-0-9.]+)",lines[x])                        
                if num == p : # вычисляем Start_point по Z
                    temp_x = x
                    a=2
                    while not re.search("^\s*.*Z", lines[temp_x-a].upper()):
                        a+=1
                    coordZ_start = float(re.search("Z\s*([-0-9.]+)",lines[temp_x-a], re.I).group(1))   
        x+=1
 
 ######################################################
    print 'coordZ=' , coordZ
    print 'coordX=' , coordX              
    for n in range(v):
        print 'n=' , n
        COORDx0 =  coordX[n]
        COORDz0 =  coordZ[n]
        lengthZ = abs(COORDz0 - coordZ[n+1])
        lengthX = abs(COORDx0 - coordX[n+1])
        if (COORDz0 - coordZ[n+1]) >= 0:# наклон "отрицательный"
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
            tan = lengthX/lengthZ
            delta = d/tan
            height_l = l*tan
            l = float(words['k'])
#            if  height_l < h:
#                l = h/tan
            if  tan < 0.3:
                l = 2l                         
        if line_or_arc[n] > 1:
            if len(coordR) :
                pass
                #radius = coordR[i]
            else:
                radius = cathetus(coordK[i],coordI[i])
                centreX = coordX[n+1] + coordI[i]
                centreZ = coordZ[n+1] + coordK[i]               
            i+=1
 
        while lengthX >= 0  :
            try:
                self.execute("F%f" % feed_rate,lineno())
                self.execute("G21 G18",lineno())
                self.execute("G61",lineno())
                if (COORDz0 + l) <= coordZ_start:                             
                    self.execute(" G1 Z%f" % (COORDz0 + l),lineno())
                else:
                    self.execute(" G1 Z%f" % coordZ_start,lineno())
                if (COORDz0 + 0.5 +l) <= coordZ_start:
                    self.execute(" G0 X%f Z%f" % ((COORDx0+0.5),(COORDz0+0.5+l)),lineno())# отход 45гр
               # else:
                    #self.execute(" G0  X%f Z%f" % ((COORDx0 + 0.5),(coordZ_start)),lineno())# отход 45гр
                self.execute(" G0 Z%f" % (coordZ_start),lineno())# выход в стартовую по Z
                if lengthX < d:
                    newX = COORDx0 - lengthX
                else:
                    newX = COORDx0 - d 
                self.execute(" G1  X%f" % (newX),lineno())# новая позиция по X
                COORDx0 = newX
                #просчитываем новую COORDz0 с учетом E(l) TODO пока без учета I(h):
                if line_or_arc[n] == 1:
                    if incline:
                        COORDz0 = COORDz0 - delta 
                    else:   
                        COORDz0 = COORDz0 + delta 
                elif line_or_arc[n] >1:
                    b2 = cathetus(radius,((centreX-COORDx0)-d))
                    b1 = cathetus(radius,(centreX-COORDx0))
                    COORDz0 = COORDz0 + (abs(b2-b1)) # (abs(b2-b1)) - приращение по Z                              
                lengthX = lengthX - d #d - съем за один проход
            except InterpreterException,e:
                msg = "%d: '%s' - %s" % (e.line_number,e.line_text, e.error_message)
                self.set_errormsg(msg) 
                return INTERP_ERROR 

 ##################################07.11.2016 offset по g-коду 
    coordZoff = []
    coordXoff = []
    program = []
    angle = [] #угол участка траектории к оси Z
    offset = 1
    for n in range(len(coordZ)-1):
        lengthZ = abs(coordZ[n] - coordZ[n+1])
        lengthX = abs(coordX[n] - coordX[n+1])
        if lengthX == 0 :   #горизонтальная линия
            delta = 0
        elif lengthZ == 0 : #вертикальная линия
            delta = 0
        else:  
            tangens = lengthX/lengthZ
        app = angle.append(atan2(lengthX,lengthZ))
    ser=''
    self.execute("F700",lineno()) 
    string=ser.join(['G1',' ','X',str(coordX[0]+cos(angle[0])*offset),' ','Z',str(coordZ[0]+sin(angle[0])*offset)] )
    ins = program.insert(0,string)
    for m in range(len(coordZ)-2): 
      if angle[m] < angle[m+1]:
        string=ser.join(['G3',' ','X',str(coordX[m+1]+cos(angle[m])*offset),' ','Z',str(coordZ[m+1]+sin(angle[m])*offset),' ','R',str(offset)])
        ins = program.insert(0,string)            
        string=ser.join(['G1',' ','X',str(coordX[m+1] + cos(angle[m+1])*offset),' ','Z',str(coordZ[m+1] + sin(angle[m+1])*offset)] )
        ins = program.insert(0,string)          
      else:
        an = (angle[m] - angle[m+1])/2 
        gg =  offset / cos(an)
        an1 = angle[m] - an
        string=ser.join(['G1',' ','X',str(coordX[m+1] + cos(an1)*gg),' ','Z',str(coordZ[m+1] + sin(an1)*gg)])
        ins = program.insert(0,string)   
    string=ser.join(['G1',' ','X',str(coordX[len(coordX)-1] + cos(angle[len(angle)-1])*offset),' ','Z',str(coordZ[len(coordZ)-1] + sin(angle[len(angle)-1])*offset)])
    ins = program.insert(0,string)
    for w in program: 
      self.execute(w,lineno())
    self.execute("G0  Z%f" % (coordZ_start),lineno())# выход в стартовую по Z  
 ######################################################         
 
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
    self.execute("G91",lineno())
    self.execute("G0  X0.5 Z0.5",lineno())# отход 45гр 
    self.execute("G90",lineno())
    self.execute("G0  Z%f" % (coordZ_start),lineno())# выход в стартовую по Z                              
    f.close()                 
    return INTERP_OK

#####################################################################################################-----G72.2
def g722(self, **words):
    """ remap code G72.2 """
    #TODO edit в меню Axis открывает .ngc 
    p = int(words['p'])
    feed_rate = int(words['f'])
    q = int(words['q'])
    d = float(words['d'])
    l = float(words['k'])
    h = float(words['i'])
    s = linuxcnc.stat() 
    s.poll() 
    filename = s.file
    f = open(filename, "r")
    lines = f.readlines()
    x,v,i = 0,-1,0
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
                    g1 = line_or_arc.insert(0,(int(re.search("G\s*([0-4.]+)",lines[x], re.I).group(1))))
                    z1 = coordZ.insert(0,(float(re.search("Z\s*([-0-9.]+)",lines[x], re.I).group(1))))
                    x1 = coordX.insert(0,(float(re.search("X\s*([-0-9.]+)",lines[x], re.I).group(1))))                   
                    if  re.search("[I]", lines[x]):
                        i1 = coordI.insert(0,(float(re.search("I\s*([-0-9.]+)",lines[x], re.I).group(1))))
                        k1 = coordK.insert(0,(float(re.search("K\s*([-0-9.]+)",lines[x], re.I).group(1))))
                    if  re.search("[R]", lines[x]):
                        r1 = coordR.insert(0,(float(re.search("R\s*([-0-9.]+)",lines[x], re.I).group(1))))                        
                if num == p : # вычисляем Start_point по Z
                    temp_x = x
                    a=2
                    while not re.search("^\s*.*X", lines[temp_x-a].upper()):
                        a+=1
                    coordX_start = float(re.search("X\s*([-0-9.]+)",lines[temp_x-a], re.I).group(1))
                    coordX_start =coordX_start +2# пробуем сделать безопастный заход(на 2мм ниже контура)
                    print 'coordX_start=' , coordX_start
        x+=1
    print 'coordZ=' , coordZ
    print 'coordX=' , coordX
    for n in range(v):
        COORDx0 =  coordX[n]
        COORDz0 =  coordZ[n]
        lengthZ = abs(COORDz0 - coordZ[n+1])
        lengthX = abs(COORDx0 - coordX[n+1])
        if (COORDx0 - coordX[n+1]) >= 0:
            pocket = 0
        else: 
            pocket = 1
        if lengthX == 0 :#горизонтальная линия
            delta = 0
            #l = lengthZ +l
            print 'deltaG=' , delta, delta , 'l=' , l
        elif lengthZ == 0 : #вертикальная линия
            delta = h
            l = float(words['k'])
            print 'deltaV=' , delta , 'l=' , l
        else:  
            tan = lengthX/lengthZ
            delta = d*tan
            height_l = l*tan
            l = float(words['k'])
#            if  height_l < h:
#                l = h/tan
            #if  tan < 0.3:
                #l = 2l                         
        if line_or_arc[n] > 1:
            if len(coordR) :
                pass
                #radius = coordR[i]TODO востребован ли R ?
            else:
                radius = sqrt((coordK[i])*(coordK[i]) + (coordI[i])*(coordI[i]))
                centreX = coordX[n+1] + coordI[i]
                centreZ = coordZ[n+1] + coordK[i]               
            i+=1 
                   
        while lengthZ -3 > 0:#3 - ширина резца для обработки паза
            try:

                self.execute("F%f" % feed_rate,lineno())
                self.execute("G21 G18",lineno())
                self.execute("G61",lineno())
                if(COORDx0 + l) <= 0:
                    self.execute(" G1  X0",lineno())
                elif (COORDx0 + l) <= coordX_start:                             
                    self.execute(" G1  X%f" % (COORDx0 + l),lineno())
                else:
                    self.execute(" G1  X%f" % coordX_start,lineno())
   #отходы 45гр -------------------------------------------
                if pocket: #для карманов
 
                    if(COORDx0 + 0.5 +l) <= 0:
                        self.execute(" G0  X%f Z%f" % (0,(COORDz0 + 0.5 )),lineno())                       
                    elif (COORDx0 + 0.5 +l) <= coordX_start:
                        self.execute(" G0  X%f Z%f" % ((COORDx0 + 0.5 + l),(COORDz0 + 0.5 )),lineno())# отход 45гр
                    else:
                        self.execute(" G0  Z%f X%f" % ((COORDz0 + 0.5),(coordX_start)),lineno())# отход 45гр
                #else:--------------------------------------
                    
                
                self.execute(" G0  X%f" % (coordX_start),lineno())# выход в стартовую по X
                if lengthZ < d:
                    newZ = COORDz0 - lengthZ
                else:
                    newZ = COORDz0 - 3 #3  - ширина пазового резца
                self.execute(" G1  Z%f" % (newZ),lineno())# новая позиция по Z
                COORDz0 = newZ
                #просчитываем новую COORDx0 с учетом E(l) TODO пока без учета I(h):
                if line_or_arc[n] == 1:
                        COORDx0 = COORDx0 + delta  
                elif line_or_arc[n] >1:
                    b2 = sqrt(radius*radius - ((centreZ-COORDz0)-d)*((centreZ-COORDz0)-d))
                    b1 = sqrt(radius*radius - (centreZ-COORDz0)*(centreZ-COORDz0))
                    COORDx0 = COORDx0 + (abs(b2-b1))                                    
                lengthZ = lengthZ - 3 #3  - ширина пазового резца
            except InterpreterException,e:
                msg = "%d: '%s' - %s" % (e.line_number,e.line_text, e.error_message)
                self.set_errormsg(msg) 
                return INTERP_ERROR    
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
    self.execute("G91",lineno())
#    self.execute(" G0  X0.5 Z0.5",lineno())# отход 45гр 
    self.execute("G90",lineno())
    self.execute(" G0  X%f" % (coordX_start),lineno())# выход в стартовую по Z                              
    f.close()                 
    return INTERP_OK
########################################################################################-------end G72.2

#################################################-----G71.3 обработка с пазами
def g713(self, **words):
    """ remap code G71.3 """
    p = int(words['p'])
    feed_rate = int(words['f'])
    q = int(words['q'])
    d = float(words['d'])
    l = float(words['k'])
    h = float(words['i'])
    s = linuxcnc.stat() 
    s.poll() 
    filename = s.file
    f = open(filename, "r")
    lines = f.readlines()
    x,v,i = 0,-1,0
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
                    g1 = line_or_arc.insert(0,(int(re.search("G\s*([0-4.]+)",lines[x], re.I).group(1))))
                    z1 = coordZ.insert(0,(float(re.search("Z\s*([-0-9.]+)",lines[x], re.I).group(1))))
                    x1 = coordX.insert(0,(float(re.search("X\s*([-0-9.]+)",lines[x], re.I).group(1))))                    
                    if  re.search("[I]", lines[x]):
                        i1 = coordI.insert(0,(float(re.search("I\s*([-0-9.]+)",lines[x], re.I).group(1))))
                        k1 = coordK.insert(0,(float(re.search("K\s*([-0-9.]+)",lines[x], re.I).group(1))))
                    if  re.search("[R]", lines[x]):
                        r1 = coordR.insert(0,(float(re.search("R\s*([-0-9.]+)",lines[x], re.I).group(1))))                        
                if num == p : # вычисляем Start_point по Z
                    temp_x = x
                    a=2
                    while not re.search("^\s*.*Z", lines[temp_x-a].upper()):
                        a+=1
                    coordZ_start = float(re.search("Z\s*([-0-9.]+)",lines[temp_x-a], re.I).group(1))
   
        x+=1

    for n in range(v):
        COORDx0 =  coordX[n]
        COORDz0 =  coordZ[n]
        lengthZ = abs(COORDz0 - coordZ[n+1])
        lengthX = abs(COORDx0 - coordX[n+1])
        if lengthX == 0 :#горизонтальная линия
            delta = 0
            l = lengthZ +l
        elif lengthZ == 0 : #вертикальная линия
            delta = 0
            l = float(words['k'])
        else:  
            tan = lengthX/lengthZ
            delta = d/tan
            height_l = l*tan
            l = float(words['k'])
#            if  height_l < h:
#                l = h/tan
            if  tan < 0.3:
                l = 2l                         
        if line_or_arc[n] > 1:
            if len(coordR) :
                pass
                #radius = coordR[i]
            else:
                radius = sqrt((coordK[i])*(coordK[i]) + (coordI[i])*(coordI[i]))
                centreX = coordX[n+1] + coordI[i]
                centreZ = coordZ[n+1] + coordK[i]               
            i+=1                      
        while lengthX >= 0:
            try:
                self.execute("F%f" % feed_rate,lineno())
                self.execute("G21 G18",lineno())
                self.execute("G61",lineno())
                if (COORDz0 + l) <= coordZ_start:                             
                    self.execute(" G1  Z%f" % (COORDz0 + l),lineno())
                else:
                    self.execute(" G1  Z%f" % coordZ_start,lineno())
                if (COORDz0 + 0.5 +l) <= coordZ_start:
                    self.execute(" G0  X%f Z%f" % ((COORDx0 + 0.5),(COORDz0 + 0.5 + l)),lineno())# отход 45гр
               # else:
                    #self.execute(" G0  X%f Z%f" % ((COORDx0 + 0.5),(coordZ_start)),lineno())# отход 45гр
                self.execute(" G0  Z%f" % (coordZ_start),lineno())# выход в стартовую по Z
                if lengthX < d:
                    newX = COORDx0 - lengthX
                else:
                    newX = COORDx0 - d 
                self.execute(" G1  X%f" % (newX),lineno())# новая позиция по X
                COORDx0 = newX
                #просчитываем новую COORDz0 с учетом E(l) TODO пока без учета I(h):
                if line_or_arc[n] == 1:
                        COORDz0 = COORDz0 + delta  
                elif line_or_arc[n] >1:
                    b2 = sqrt(radius*radius - ((centreX-COORDx0)-d)*((centreX-COORDx0)-d))
                    b1 = sqrt(radius*radius - (centreX-COORDx0)*(centreX-COORDx0))
                    COORDz0 = COORDz0 + (abs(b2-b1)) # (abs(b2-b1)) - приращение по Z                              
                lengthX = lengthX - d #d - съем за один проход
            except InterpreterException,e:
                msg = "%d: '%s' - %s" % (e.line_number,e.line_text, e.error_message)
                self.set_errormsg(msg) 
                return INTERP_ERROR    
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
    self.execute("G91",lineno())
    self.execute(" G0  X0.5 Z0.5",lineno())# отход 45гр 
    self.execute("G90",lineno())
    self.execute(" G0  Z%f" % (coordZ_start),lineno())# выход в стартовую по Z                              
    f.close()                 
    return INTERP_OK
    ########################################################################################-------end G71.3
def involute(self, **words):
    """ remap function with raw access to Interpreter internals """

    if self.debugmask & 0x20000000: call_pydevd() # USER2 debug flag

    if equal(self.feed_rate,0.0):
        self.set_errormsg("feedrate > 0 required")
        return INTERP_ERROR

    if equal(self.speed,0.0):
        self.set_errormsg("spindle speed > 0 required")
        return INTERP_ERROR

    plunge = 0.1 # if Z word was given, plunge - with reduced feed

    # inspect controlling block for relevant words
    c = self.blocks[self.remap_level]
    x0 = c.x_number if c.x_flag else 0
    y0 = c.y_number if c.y_flag else 0
    a  = c.p_number if c.p_flag else 10
    old_z = self.current_z

    if self.debugmask & 0x10000000:   # USER1 debug flag
        print "x0=%f y0=%f a=%f old_z=%f" % (x0,y0,a,old_z)

    try:
        #self.execute("G3456")  # would raise InterpreterException
        self.execute("G21",lineno())
        self.execute("G64 P0.001",lineno())
        self.execute("G0 X%f Y%f" % (x0,y0),lineno())

        if c.z_flag:
            feed = self.feed_rate
            self.execute("F%f G1 Z%f" % (feed * plunge, c.z_number),lineno())
            self.execute("F%f" % (feed),lineno())

        for i in range(100):
            t = i/10.
            x = x0 + a * (cos(t) + t * sin(t))
            y = y0 + a * (sin(t) - t * cos(t))
            self.execute("G1 X%f Y%f" % (x,y),lineno())

        if c.z_flag: # retract to starting height
            self.execute("G0 Z%f" % (old_z),lineno())

    except InterpreterException,e:
        msg = "%d: '%s' - %s" % (e.line_number,e.line_text, e.error_message)
        self.set_errormsg(msg) # replace builtin error message
        return INTERP_ERROR

    return INTERP_OK


def m462(self, **words):
    """ remap function which does the equivalent of M62, but via Python """

    p = int(words['p'])
    q = int(words['q'])

    if q:
        SET_MOTION_OUTPUT_BIT(p)
    else:
        CLEAR_MOTION_OUTPUT_BIT(p)
    return INTERP_OK

def m465(self, **words):
    """ remap function which does the equivalent of M65, but via Python """

    p = int(words['p'])
    q = int(words['q'])

    if q:
        SET_AUX_OUTPUT_BIT(p)
    else:
        CLEAR_AUX_OUTPUT_BIT(p)
    return INTERP_OK
