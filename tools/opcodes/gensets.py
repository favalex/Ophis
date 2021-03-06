#!/usr/bin/python
import sys

verbose = 0

prologue = '"""' + """Opcodes file.

	Tables for the assembly of 6502-family instructions, mapping
	opcodes and addressing modes to binary instructions.""" + '"""' + """

# Copyright 2002 Michael C. Martin.
# You may use, modify, and distribute this file under the BSD
# license: See LICENSE.txt for details.

# Names of addressing modes
modes = ["Implied",         #  0
	 "Immediate",       #  1
	 "Zero Page",       #  2
	 "Zero Page, X",    #  3
	 "Zero Page, Y",    #  4
	 "Absolute",        #  5
	 "Absolute, X",     #  6
	 "Absolute, Y",     #  7
	 "(Absolute)",      #  8
         "(Absolute, X)",   #  9
         "(Absolute), Y",   # 10
         "(Zero Page)",     # 11
	 "(Zero Page, X)",  # 12
	 "(Zero Page), Y",  # 13
	 "Relative"]        # 14

# Lengths of the argument
lengths = [0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 1, 1, 1, 1]
"""

# These values should match the ones in the prologue string.
modes = ["Implied",         #  0
	 "Immediate",       #  1
	 "Zero Page",       #  2
	 "Zero Page, X",    #  3
	 "Zero Page, Y",    #  4
	 "Absolute",        #  5
	 "Absolute, X",     #  6
	 "Absolute, Y",     #  7
	 "(Absolute)",      #  8
         "(Absolute, X)",   #  9
         "(Absolute), Y",   # 10
         "(Zero Page)",     # 11
	 "(Zero Page, X)",  # 12
	 "(Zero Page), Y",  # 13
	 "Relative"]        # 14

flatmodes = [x.lower() for x in modes]

# WARNING: This decommenter assumes that # never appears anywhere else
# in a line.
def decomment (l):
    if '#' in l:
        l = l[:l.index('#')]
    return l.strip()

def decomment_readlines (fname):
   result = [decomment(x) for x in file(fname).readlines()]
   return [x for x in result if len(x) > 0]

def parse_chipset_file (fname):
    result = [None] * 256
    ls = [[x.strip() for x in y] for y in [z.split(':', 1) for z in decomment_readlines (fname)]]
    for l in ls:
        if len(l) == 2:
            try:
                op = int (l[0], 16)
                syns = l[1].split(';')
                for s in syns:
                    s_p = s.split('-')
                    if len(s_p) == 2:
                        mnem = s_p[0].lower().strip()
                        mode = s_p[1].lower().strip()
                        if mode in flatmodes:
                            if result[op] == None:
                                result[op] = []
                            result[op].append((mnem, flatmodes.index(mode)))
                        else:
                            print "Unknown mode '%s'" % s_p[1]
            except ValueError:
                print "Illegal opcode '%s'" % l[0]
    return result    

def collate_chipset_map (cs_list, base):
    result = {}
    for (opcode, insts) in zip (range(256), cs_list):
        if insts != None:
            for inst in insts:
                (mnem, mode) = inst
                if mnem not in result:
                    result[mnem] = [None] * len(modes)
                if result[mnem][mode] is not None:
                    print "Warning: Reassigning %s - %s" % (mnem, modes[mode])
                result[mnem][mode] = opcode
    if base is not None:
        todel = []
        for x in result:
            if x in base:
                if result[x] == base[x]:
                    todel.append(x)
                elif verbose != 0:
                    print "# Opcode %s changed" % x
            elif verbose != 0:
                print "# Opcode %s added" % x
        for x in todel:
            del result[x]
    return result

def mapval(x):
    if x is None:
        return "None"
    else:
        return "0x%02X" % x

def dump_map (m, prologue = ''):
    mnems = m.keys()
    mnems.sort()
    for mnem in mnems:
        print "%s'%s': [%s]," % (prologue, mnem, ', '.join([mapval(x) for x in m[mnem]]))

if __name__=='__main__':
    if len(sys.argv) > 1:
        chipsets = argv[1:]
    else:
        chipsets = ['chipsets.txt']
    archs = []
    for x in chipsets:
        try:
            ls = [[x.strip() for x in y] for y in [z.split(':', 1) for z in decomment_readlines (x)]]
            for l in ls:
                if len(l) != 2:
                    print "Could not parse the chipset line '%s'" % ":".join(l)
                else:
                    archs.append((l[0], l[1]))
        except IOError:
            print "Could not read file %s" % x
    print prologue
    baseset = None
    for (field, fname) in archs:
        chipset_list = parse_chipset_file(fname)
        instruction_map = collate_chipset_map (chipset_list, baseset)
        if baseset == None:
            baseset = instruction_map
        print "%s = {" % field
        dump_map (instruction_map, ' ' * (len(field) + 4))
        print "%s}" % (' ' * (len(field) + 3))
        print ""
    
