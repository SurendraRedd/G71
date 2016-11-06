# --*-- coding:utf-8 --*--
import sys
import re
from math import *

def pars(array,reg ,lines):
    a=array.insert(0,(float(re.search(reg,lines, re.I).group(1))))

def cathetus(c,b):
    a = sqrt(abs(c*c - b*b))
    return a 


filename = '/home/nkp/hlam/G71/edit_dxf.ngc'
f = open(filename, "r")
lines = f.readlines()
f.close()
x,v,i = 0,-1,0
line_or_arc = [] # указатель:линия, дуга ccw , дуга cw
coordZ = []
coordX = []
coordI = []
coordK = []
coordR = []
coordZoff = []
coordXoff = []
angle = [] #угол участка траектории к оси Z
p=5 # номер первой строки Gкода контура
q=10 # номер последней строки Gкода контура
offset = 3
filename = '/home/nkp/hlam/G71/2off.ngc'
f = open(filename, "w")
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
print 'coordZ=', coordZ
print 'coordX=', coordX
print 'line_or_arc=', line_or_arc
print 'coordZ_start=', coordZ_start
for n in range(len(coordZ)-1):
    print 'n =',n
    lengthZ = abs(coordZ[n] - coordZ[n+1])
    lengthX = abs(coordX[n] - coordX[n+1])
    if lengthX == 0 :   #горизонтальная линия
        delta = 0
    elif lengthZ == 0 : #вертикальная линия
        delta = 0
    else:  
        tangens = lengthX/lengthZ
    print 'lengthZ =',lengthZ
    print 'lengthX =',lengthX
    print 'angle =',degrees(atan2(lengthX,lengthZ))
    print '==========================='
    app = angle.append(atan2(lengthX,lengthZ))
print 'angle =',angle
app = coordZoff.append(coordZ[0] + sin(angle[0])*offset)  
app = coordXoff.append(coordX[0] + cos(angle[0])*offset) 


for m in range(len(coordZ)-2): 
  if angle[m] < angle[m+1]:
    print 'm< =',m
    app = coordZoff.append(coordZ[m+1] + sin(angle[m])*offset)    
    app = coordXoff.append(coordX[m+1] + cos(angle[m])*offset)
    app = coordZoff.append(coordZ[m+1] + sin(angle[m+1])*offset)    
    app = coordXoff.append(coordX[m+1] + cos(angle[m+1])*offset)    
  else:
    print 'm> =',m
    an = (angle[m] - angle[m+1])/2 
    gg =  offset / cos(an)
    print 'gg =',gg
    an1 = angle[m] - an
    print 'an =',degrees(an)
    print 'an1 =',degrees(an1)
    app = coordZoff.append(coordZ[m+1] + sin(an1)*gg)    
    app = coordXoff.append(coordX[m+1] + cos(an1)*gg) 
   
app = coordZoff.append(coordZ[len(coordZ)-1] + sin(angle[len(angle)-1])*offset)    
app = coordXoff.append(coordX[len(coordX)-1] + cos(angle[len(angle)-1])*offset)     
    
    
    
print '++++++++++++++++++++++++++++++'    
print 'coordZoff =',coordZoff
print 'coordXoff =',coordXoff   
print '++++++++++++++++++++++++++++++'    

ser=' '
f.write('F300') 
f.write('\n') 
for n in reversed(range(len(coordZoff))):
    s=['G1',' ' , 'X', str(coordXoff[n]), ' ' ,'Z',str(coordZoff[n]), '\n'] 
    j=ser.join(s)
    f.write(j)
    
f.write('G1 Z0') 
f.write('\n')      






f.write('F300') 
f.write('\n') 
for n in reversed(range(len(coordZ))):
    s=['G1',' ' , 'X', str(coordX[n]), ' ' ,'Z',str(coordZ[n]), '\n'] 
    j=ser.join(s)
    f.write(j)
    
f.write('G1 Z0') 
f.write('\n')      
f.write('M2')  
f.close()












