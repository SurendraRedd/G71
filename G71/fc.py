#!/usr/bin/python
# --*-- coding:utf-8 --*--

#[FILTER]
#PROGRAM_EXTENSION = .fc  FanucScript
#fc = ./fc.py


import re
from math import *
import sys

def main(argv):
    
    filename = open(argv[0], 'r')
    lines = filename.readlines()
    strings = ''
    x = 0
    code = 'G01'
    k=0
    flag=0
    n=1
    while x < len(lines):
        if re.search("N\s*([0-9.]+)",lines[x], re.I):
            numC = int(re.search("N\s*([0-9.]+)",lines[x], re.I).group(1))
            if numC == t_P :
                flag=1
            if  numC == t_Q:
                flag=0 
                l = re.sub("^\s+|\n|\r|\s+$", '',  lines[x] )
                lines[x] = '(' + l+ ')'+'\n'   
        if flag:
            if not re.search("N\s*([0-9.]+)",lines[x], re.I):
                l = re.sub("^\s+|\n|\r|\s+$", '',  lines[x] )
                lines[x] = '('+'N'+str(numC+n)+' ' + l + ')'+'\n'                    
                n+= 1
            else:
                l = re.sub("^\s+|\n|\r|\s+$", '',  lines[x] )
                lines[x] = '(' + l+ ')'+'\n'                     
        if re.search(".*\s*G71", lines[x], re.I) and not re.search(".*\s*[(]", lines[x], re.I):
            if k==0:
                try:
                    t_U = int(re.search("U\s*([-0-9.]+)",lines[x], re.I).group(1))
                except:
                    pass
                try:
                    t_R = float(re.search("R\s*([-0-9.]+)",lines[x], re.I).group(1))
                except:
                    pass        
            try:
                t_P = int(re.search("P\s*([-0-9.]+)",lines[x], re.I).group(1))
            except:
                pass        
            try:
                t_Q = int(re.search("Q\s*([-0-9.]+)",lines[x], re.I).group(1))
            except:
                pass
            try:
                t_W = float(re.search("W\s*([-0-9.]+)",lines[x], re.I).group(1))
            except:
                pass        
            if k:
                strings += 'G71.2'+'P'+str(t_P)+'Q'+str(t_Q)+'D'+str(t_R)+'K'+str(t_W)+'L'+str(t_U)+'\n'
            k += 1          
        if re.search(".*\s*G0?0[^0-9]", lines[x], re.I):
            try:
                Xcont = float(re.search("X\s*([-0-9.]+)",lines[x], re.I).group(1))
                Xcont_temp +=  Ucont               
            except:
                pass
            try:
                Zcont = float(re.search("Z\s*([-0-9.]+)",lines[x], re.I).group(1)) 
                Zcont_temp = Zcont               
            except:
                pass                
            if re.search("\s*[UW]",lines[x],re.I):
                try:
                    Ucont = float(re.search("U\s*([-0-9.]+)",lines[x], re.I).group(1))
                    Wcont = float(re.search("W\s*([-0-9.]+)",lines[x], re.I).group(1))
                except:
                    pass
            strings += lines[x]
            code = 'G00'
        elif re.search(".*\s*G0?1[^0-9]", lines[x], re.I):
            try:
                Xcont = float(re.search("X\s*([-0-9.]+)",lines[x], re.I).group(1))
                Xcont_temp +=  Ucont
            except:
                pass 
            try:
                Zcont = float(re.search("Z\s*([-0-9.]+)",lines[x], re.I).group(1))
                Zcont_temp = Zcont
            except:
                pass                         
            strings += lines[x]
            code = 'G01'            
        elif re.search("\s*G0?2[^0-9]", lines[x], re.I):
            strings += lines[x]
            code = 'G02'             
        elif re.search("\s*G0?3[^0-9]", lines[x], re.I):
            strings += lines[x]
            code = 'G03'             
        else:
            if re.search("\s*[XZUW]",lines[x],re.I) and not re.search("\s*[G]",lines[x],re.I):   
                if re.search("\s*N", lines[x], re.I):
                    num = int(re.search("N\s*([0-9.]+)",lines[x], re.I).group(1))
                    lineUW = re.sub("\s*N[0-9]+","N"+str(num)+' '+ code,lines[x])
                else:
                    lineUW = code + ' ' + lines[x] 
                if re.search("\s*[UW]",lines[x],re.I):
                    try:
                        Ucont = float(re.search("U\s*([-0-9.]+)",lines[x], re.I).group(1))
                    except:
                        pass
                    try:
                        Wcont = float(re.search("W\s*([-0-9.]+)",lines[x], re.I).group(1))
                    except:
                        pass
                    try:                        
                        Xcont_temp +=  Ucont
                        lineUW = re.sub("U\s*([-0-9.]+)","X"+str(Xcont_temp)+' ',lineUW)
                    except:
                        pass 
                    try:                        
                        Zcont_temp +=  Wcont
                        lineUW = re.sub("W\s*([-0-9.]+)","Z"+str(Zcont_temp)+' ',lineUW)
                    except:
                        pass                                           
                strings +=  lineUW                                               
        x+=1 
    f=open('fc.ngc','w')
    f.write(strings) 
    f.close                            
    print  strings
    print  'M2'    
if __name__ == "__main__":
   main(sys.argv[1:])



























