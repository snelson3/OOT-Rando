import random
from collections import namedtuple
# General helper and debug methods
toHex = lambda b: hex(b)[2:].zfill(2).upper()
def make_readable(data):
    # data is a bytearray
    # return a string with the data in a format I can easily read
    l = [] # list of byte words 
    for i in range(0, len(data), 4):
        l.append(''.join([toHex(b) for b in data[i:i+4]]))
    if i < len(data)-4:
        l.append(''.join([toHex(b) for b in data[i:]]))
    formatted_list = []
    for b in range(0, len(l), 4):
        avail_bytes = l[b:b+4]
        string = ' '.join(['{}' for b in avail_bytes])
        formatted_list.append(string.format(*avail_bytes))
    return '\n'.join(formatted_list)
def setSeed(seed):
    random.seed(seed)
def writeSpoilers(spoilers, fn="spoiler.log"):
    # Write out a spoiler object
    s = ''
    for room in spoilers:
        s += '{}\n'.format(room)
        for replacement in spoilers[room]:
            old = replacement["old"]
            new = replacement["new"]
            s +='{}({})[{}] -> {}({})[{}]\n'.format(old["filename"],old["description"],old["variable"],new["filename"],new["description"],new["variable"])
    with open(fn, "w") as f:
        f.write(s)
def parseVariableList(l):
    if len(l) == 0:
        return []
    Variable = namedtuple('Variable', 'var desc')
    vlist = []
    for v in l.split(','):
        desc = ''
        var = v
        if '(' in var and ')' in var:
            desc = var.split('(')[1].split(')')[0]
            var = var.split('(')[0]
        vlist.append(Variable(var=var.strip(), desc=desc.strip()))
    return vlist