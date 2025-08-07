### Parser
"""Encapsulates access to the input code. 
    Reads an assembly language com- mand, parses it, 
    and provides convenient access to the command’s components (fields and symbols).
    In addition, removes all white space and comments."""


def commandType(curCommand):
    """Returns the type of the current command"""
    Type = ""
    
    # remove inline command
    if "//" in lines:
        remove_inline_comment(curCommand)
    
    # remove white space before and after the command
    else:
        curCommand = curCommand.strip()

    if curCommand[0] == "@":
        Type = "A_COMMAND"
    elif (curCommand[0] == "(") and (curCommand[-1:] == ")"):
        Type = "L_COMMAND"
    else:
        Type = "C_COMMAND"
    return Type


def symbol(curCommand):
    """Returns the symbol or decimal Xxx of the current command"""
    Type = commandType(curCommand)
    if  Type == "A_COMMAND":
        symbol = str(curCommand.replace("@", ""))
        if symbol.isnumeric():
            return int(symbol)
        else:
            return symbol

    if  Type == "L_COMMAND":
        symbol = curCommand.strip("()")
        return symbol


def dest_comp_jump(curCommand):
    dest = ""
    comp = ""
    jump = ""

    if (("=" in curCommand) == True) and ((";" in curCommand) == False):
        temp1 = curCommand.split("=")
        dest = temp1[0].strip()
        comp = temp1[1].strip()
        jump = "null"

    elif ((";" in curCommand) == True) and (("=" in curCommand) == False):
        temp2 = curCommand.split(";")
        dest = "null"
        comp = temp2[0].strip()
        jump = temp2[1].strip()

    elif (("=" in curCommand) == True) and ((";" in curCommand) == True):
        temp1 = curCommand.split("=")
        dest = temp1[0].strip()
        temp2 = temp1[1].split(';')
        comp = temp2[0].strip()
        jump = temp2[1].strip()

    return dest, comp, jump


def remove_inline_comment(aline):
    aline = aline.split("//")[0]
    aline.strip()
    return aline
    

### Code
# A instruction
def Ainstruction(aline):
    global next_addr
    value = symbol(aline)
    
    if (isinstance(value, int) == False):  # 如果 @ variable
        if (contain(value, symbol_table) == False):  # 如果 variable 不在 symbol talbe 則新增變數
            addEntry(value, symbol_table, type, next_addr, instrCtr)
            next_addr += 1 
        
        value = GetAddr(value, symbol_table)

    if value > 32768:
        raise Exception("your number exceed 2^15 = 32768")
    
    value = '{0:015b}'.format(value)
    newline = f"0{value}"
    return newline

# C instruction
def Cinstruction(aline):
    dest, comp, jump = dest_comp_jump(aline)
    newline = f'111{comp_dic[comp]}{dest_dic[dest]}{jump_dic[jump]}'
    return newline

# C instruction operation tables
# Comp_Dict
comp_dic = dict()
"""comp_dic[comp]"""

comp_dic["0"] = "0101010"
comp_dic["1"] = "0111111"
comp_dic["-1"] = "0111010"
comp_dic["D"] = "0001100"
comp_dic["A"] = "0110000"
comp_dic["!D"] = "0001111"
comp_dic["!A"] = "0110001"
comp_dic["-D"] = "0001111"
comp_dic["-A"] = "0110011"
comp_dic["D+1"] = "0011111"
comp_dic["A+1"] = "0110111"
comp_dic["D-1"] = "0001110"
comp_dic["A-1"] = "0110010"
comp_dic["D+A"] = "0000010"
comp_dic["D-A"] = "0010011"
comp_dic["A-D"] = "0000111"
comp_dic["D&A"] = "0000000"
comp_dic["D|A"] = "0010101"

comp_dic["M"] = "1110000"
comp_dic["!M"] = "1110001"
comp_dic["-M"] = "1110011"
comp_dic["M+1"] = "1110111"
comp_dic["M-1"] = "1110010"
comp_dic["D+M"] = "1000010"
comp_dic["D-M"] = "1010011"
comp_dic["M-D"] = "1000111"
comp_dic["D&M"] = "1000000"
comp_dic["D|M"] = "1010101"


# Dest_Dict
dest_dic = dict()
"""Dest_dic[dest]"""
dest_dic['null'] = "000"
dest_dic['M'] = "001"
dest_dic['D'] = "010"
dest_dic['MD'] = "011"
dest_dic['A'] = "100"
dest_dic['AM'] = "101"
dest_dic['AD'] = "110"
dest_dic['AMD'] = "111"


# Jump_Dict
jump_dic = dict()
"""Jump_dic[jump]"""
jump_dic['null'] = "000"
jump_dic['JGT'] = "001"
jump_dic['JEQ'] = "010"
jump_dic['JGE'] = "011"
jump_dic['JLT'] = "100"
jump_dic['JNE'] = "101"
jump_dic['JLE'] = "110"
jump_dic['JMP'] = "111"


### Symbol Table
# Constructor
def symbol_table_constructor():
    """Creates a new empty symbol table"""
    symbol_table_dict = dict()
    symbol_table_dict['SP'] = 0
    symbol_table_dict['LCL'] = 1
    symbol_table_dict['ARG'] = 2
    symbol_table_dict['THIS'] = 3
    symbol_table_dict['THAT'] = 4

    for i in range(16):
        register_name = f"R{i}"
        symbol_table_dict[register_name] = i

    symbol_table_dict['SCREEN'] = 16384
    symbol_table_dict['KBD'] = 24576
    next_addr = 16

    return symbol_table_dict, next_addr


# addEntry
def addEntry(asymbol, dict, type, next_addr, instrCtr):
    """Adds the pair (symbol, address) to the table"""
    if type == "L_COMMAND":
        dict[asymbol] = instrCtr
    elif type == "A_COMMAND":
        dict[asymbol] = next_addr


# GetAddr
def GetAddr(asymbol, dict):
    """Returns the address associated with the symbol"""
    addr = dict[asymbol]
    return addr


# contain
def contain(key, my_dict):
    """Does the symbol table contain the given symbol?"""
    return key in my_dict


### main
#import and export file
file_path = input()
file = open(file_path, "r", encoding="utf-8")
file_name = file_path.split(".")[0]
new_file_name = file_name + ".hack"

print(f"Assembling {file_path}")

# constructe a new symbol table
symbol_table, next_addr = symbol_table_constructor()

# first round: add labels into symbol tabel
instrCtr = 0
for lines in file:
    # remove comment
    if lines[0:2] == "//":
        continue

    # remove white space
    if lines in ('\n'):
        continue

    # remove inline comments
    if "//" in lines:
        remove_inline_comment(lines)
    
    # remove white space before and after the command
    lines = lines.strip()

    type = commandType(lines)
    if type == "L_COMMAND":
        asymbol = symbol(lines)
        if (contain(asymbol, symbol_table) == False):
            addEntry(asymbol, symbol_table, type, next_addr, instrCtr)
    
    # 不是 L_COMMAND 才增加 instrCtr
    else:
        instrCtr += 1

file.close()


# second round
instrCtr = 0
file = open(file_path, "r", encoding="utf-8")
new_file = open(new_file_name, "w")
for lines in file:
    # remove comment
    if lines[0:2] == "//":
        continue

    # remove white space
    if lines in ('\n'):
        continue

    # remove inline comments
    if "//" in lines:
        lines = remove_inline_comment(lines)

    # remove white space before and after the command
    lines = lines.strip()
    
    # write Machine Code into the new file
    type = commandType(lines)
    result = ""

    if type == "A_COMMAND":
        result = Ainstruction(lines)

    elif type == "C_COMMAND":
        result = Cinstruction(lines)
    
    elif type == "L_COMMAND":
        instrCtr += 1
        continue

    new_file.write(result + "\n")

    instrCtr += 1

# close files
file.close()
new_file.close()
