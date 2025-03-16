#!/usr/bin/python3
import sys
import re
mnemonics = {
    "BZ" :  {"name":"BZ","type":"address", "op":0},
    "BL" :  {"name":"BL","type":"address", "op":1},
    "JMP":  {"name":"JMP","type":"address", "op":2},
    "JMPI": {"name":"JMPI","type":"noarg",   "op":3},
    "MIN":  {"name":"MIN","type":"address", "op":4},
    "MOUT": {"name":"MOUT","type":"address", "op":5},
    "STHC": {"name":"STHC","type":"noarg",   "op":6},
    "STB":  {"name":"STB","type":"bank",    "op":7},
    "LD":   {"name":"LD","type":"address", "op":8},
    "LDI":  {"name":"LDI","type":"noarg",   "op":9},
    "ADC":  {"name":"ADC","type":"noarg",   "op":10},
    "INC":  {"name":"INC","type":"noarg",   "op":11},
    "NOR":  {"name":"NOR","type":"noarg",   "op":12},
    "RLF":  {"name":"RLF","type":"noarg",   "op":13},
    "AND":  {"name":"AND","type":"noarg",   "op":14},
    "SF" :  {"name":"SF","type":"noarg",   "op":15},
    "ORG":  {"name":"ORG","type":"pseudo_op_addr"},
    "DW" :  {"name":"DW","type":"pseudo_op_word"}
}

argmax = {
    "address" : 255,
    "bank"    : 15,
    "pseudo_op_addr": 255,
    "pseudo_op_word": 0xfff
}

reLabel = re.compile("^([_a-zA-Z][_a-zA-Z0-9]*):")
reMnemonic = re.compile("^("+"|".join(mnemonics.keys())+")")
reExpression = re.compile("([^;$]+)");
#reLabel = re.compile("^([_a-zA-Z]*):")
class AsmLine:
    label=None
    mnemonic=None
    arg=None
    expression=None
    def __init__(self, line, filename, linenum):
        self.filename=filename
        self.linenum=linenum
        line = line.lstrip()
        label = reLabel.match(line)
        if label :
            self.label=label.group(1)
            line = line[len(label.group(0))::]
            line = line.lstrip()
            print(line)
        mnemonic = reMnemonic.match(line)
        if mnemonic :
            self.mnemonic = mnemonics[mnemonic.group(1)]
            line = line[len(mnemonic.group(0))::]
            line = line.lstrip()
            print(line)
            exp = reExpression.match(line)
            if exp:
                if self.mnemonic["type"] == "noarg":
                    print(f"Syntax Error argument given for mnemonic {self.mnemonic['name']} {self.filename}:{self.linenum}")
                    exit(1);
                self.expression=exp.group(1)
            else:
                if self.mnemonic["type"] != "noarg":
                    print(f"Syntax Error no argument given for mnemonic {self.mnemonic['name']} {self.filename}:{self.linenum}")
                    exit(1);

def fixAddresses(AsmLines):
    currentWord=0
    symbols={}

    for i in AsmLines: #pass one build symbol table
        
        if i.mnemonic and i.mnemonic["name"]=="ORG":
            currentWord=eval(i.expression)
        if i.label :
            symbols[i.label]=currentWord
        if i.mnemonic and i.mnemonic["name"]!="ORG":
            currentWord+=1

    for i in AsmLines: #pass 2 evaluate expressions
        if i.expression and i.mnemonic["name"] != "ORG":

            #replace symbols with their value, skip if no symbols
            symbolNames = list(symbols.keys())
            symbolNames.sort(reverse=True, key=len)
            if symbolNames :                 
                for symbol in symbolNames: #match longest symbols first
                    i.expression = re.sub(symbol,str(symbols[symbol]),i.expression)
            i.arg=eval(i.expression)

            #verify arg is legal
            if not isinstance(i.arg, int):
                print(f"Expression did not evaluate to integer {i.filename}:{i.linenum}")
                exit(1)
            if i.arg > argmax[i.mnemonic["type"]]:
                print(f"Argument exceeds legal size for mnemonic {i.mnemonc['name']}: {i.filename}:{i.linenum}")
                exit(1)
        #while we're here...explicitly set "noarg" operations' arg to 0
        if i.mnemonic and i.mnemonic["type"] == "noarg":
            i.arg=0
            
def emitCode(AsmLines,outputfile):
    #pare down AsmLines to be only operations (and datawords):
    Ops = []
    for line in AsmLines:
        if line.mnemonic and line.mnemonic["name"]!="ORG":
            Ops.append(line)
    opsLen = len(Ops)
    outputBuffer=bytes()
    for i in range(0,opsLen,2):
        op1_top = 0 #top 8 bits of op1
        op1_bottom = 0 #bottom 4 bits of op1 top 4 of op2
        op2_bottom = 0 #bottom 8 bits of op2
        if Ops[i].mnemonic["op"]:
            op1_top = Ops[i].mnemonic["op"] << 4
            op1_top |= (Ops[i].arg & 0xff) >> 4
        else: #for DB pseudo op use top 4 bits of arg
            op1_top = (Ops[i].arg >> 4) &0xff
        op1_bottom = (Ops[i].arg & 0x0f) << 4
    
        if i+1 < opsLen:
            if Ops[i+1].mnemonic["op"]:
                op1_bottom |= Ops[i+1].mnemonic["op"]
            else: #for DB pseudo op use top 4 bits of arg
                op1_bottom |= (Ops[i+1].arg >> 8) &0x0f
            op2_bottom = (Ops[i+1].arg & 0xff)
        
        outputBuffer += bytes([op1_top, op1_bottom])
        if i+1 < opsLen:
            outputBuffer += bytes([op2_bottom])
        
    output = open(outputfile, 'wb')
    output.write(outputBuffer)
    output.close()
    
def main():
    if len(sys.argv) == 1 :
        print("no file provided")
        return
    AsmLines=[]
    with open(sys.argv[1], 'r') as file:
        lines = file.readlines()
        linenum=1
        for line in lines:
            print(line)
            AsmLines.append(AsmLine(line,sys.argv[1],linenum))
            linenum+=1
    fixAddresses(AsmLines)
    print(AsmLines)
    emitCode(AsmLines,"output.bin")

if __name__=="__main__" :
    main()
