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

#####################################################################################################-----G71.1
def g711(self, **words):
    """ remap code G71.1 """
    p = int(words['p'])
    feed_rate = int(words['f'])
    q = int(words['q'])
    d = float(words['d'])
    l = float(words['e'])
    h = float(words['h'])
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
    s.poll() 
    coordZ_start = 0
    while x < len(lines):
        if  re.search("^\s*[(]\s*N\d", lines[x]):
            if not re.search("[^\(\)\.\-\+NGZXRIK\d\s]", lines[x]):
                num = int(re.findall("^\s*\d*",(re.split('N',lines[x])[1]))[0])
                if num >= p and num <= q:
                    v+=1
                    g1 = line_or_arc.insert(0,(int(re.findall("^\s*\d*",(re.split('G',lines[x])[1]))[0])))
                    z1 = coordZ.insert(0,(float(re.findall("^\s*\-?\d*\.?\d*",(re.split('Z',lines[x])[1]))[0])))
                    x1 = coordX.insert(0,(float(re.findall("^\s*\-?\d*\.?\d*",(re.split('X',lines[x])[1]))[0])))                    
                    if  re.search("[I]", lines[x]):
                        i1 = coordI.insert(0,(float(re.findall("^\s*\-?\d*\.?\d*",(re.split('I',lines[x])[1]))[0])))
                        k1 = coordK.insert(0,(float(re.findall("^\s*\-?\d*\.?\d*",(re.split('K',lines[x])[1]))[0]))) 
        x+=1
    for n in range(v):
        COORDx0 =  coordX[n]
        COORDz0 =  coordZ[n]
        lengthZ = abs(COORDz0 - coordZ[n+1])
        lengthX = COORDx0 - coordX[n+1]
        try:
            tan = lengthX/lengthZ
            print "tan=", tan
        except ZeroDivisionError:
            tan = 0 
        if l*tan < h:
            try:
               l = h/tan
            except ZeroDivisionError:
                l = 2l 
        else:
            l = float(words['e'])   
         
        
        if line_or_arc[n] > 1:
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
                else:
                    self.execute(" G0  X%f Z%f" % ((COORDx0 + 0.5),(coordZ_start)),lineno())# отход 45гр
                self.execute(" G0  Z%f" % (coordZ_start),lineno())# выход в стартовую по Z
                if lengthX < d:
                    newX = COORDx0 - lengthX
                else:
                    newX = COORDx0 - d 
                self.execute(" G1  X%f" % (newX),lineno())# новая позиция по X
                COORDx0 = newX
                #просчитываем новую COORDz0 с учетом L(l) TODO пока без учета H(h):
                if line_or_arc[n] == 1:
                    try:
                        COORDz0 = COORDz0 + d/tan  
                    except ZeroDivisionError:
                        COORDz0 = COORDz0
                elif line_or_arc[n] >1:
                    b2 = sqrt(radius*radius - ((centreX-COORDx0)-d)*((centreX-COORDx0)-d))
                    b1 = sqrt(radius*radius - (centreX-COORDx0)*(centreX-COORDx0))
                    COORDz0 = COORDz0 + (abs(b2-b1))                                    
                lengthX = lengthX - d #d - съем за один проход
            except InterpreterException,e:
                print "execute_ERROR"
    #заключительный проход по заданному контуру    
    repeat = 2
    for e in range(repeat): #возможность повторного прохода
        w=0 
        if  e ==88:#TODO
            self.execute(" G0  Z%f" % (coordZ_start),lineno())# выход в стартовую по Z         
        while w < len(lines):
            if  re.search("^\s*[(]\s*N\d", lines[w]):
                if not re.search("[^\(\)\.\-\+NGZXRIK\d\s]", lines[w]):
                    num2 = int(re.findall("^\s*\d*",(re.split('N',lines[w])[1]))[0])
                    if num2 >= p and num2 <= q:
                        try: 
                            contur=re.split('\)',(re.split('\(',lines[w])[1]))[0]
                            self.execute(contur,lineno())
                        except InterpreterException,e:
                            msg = "%d: '%s' - %s" % (e.line_number,e.line_text, e.error_message)
                            self.set_errormsg(msg) 
                            return INTERP_ERROR
            w+=1
        
        self.execute("G91",lineno())
        self.execute(" G0  X0.5 Z0.5",lineno())# отход 45гр 
        self.execute("G90",lineno())
        self.execute(" G0  Z%f" % (coordZ_start),lineno())# выход в стартовую по Z                              
    f.close()                 
    return INTERP_OK
########################################################################################-------end G71.1

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
