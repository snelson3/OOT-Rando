from .Utils import toHex

class Header():
    def __init__(self, accessor, addr,):
        self.accessor = accessor
        self.start_addr = addr
        self.end_addr = self.findEndAddr()
        self.header = self.accessor.getData(self.start_addr, self.end_addr)
        self.objectListDef = self.getObjectListDef()
        self.actorListDef = self.getActorListDef()
    def findEndAddr(self):
        curr_addr = self.start_addr
        while self.accessor.getData(curr_addr) != int(0x14):
            curr_addr += 8
        return curr_addr + 8
    def getObjectListDef(self):
        defn = self.lookupCommand('0B')
        if not defn:
            return {"num": 0, "offset": 0}
        return {"num": defn[1], "offset": int(''.join([toHex(b) for b in defn[-3:]]),16)}
    def getActorListDef(self):
        defn = self.lookupCommand('01')
        if not defn:
            return {"num": 0, "offset": 0}
        return {"num": defn[1], "offset": int(''.join([toHex(b) for b in defn[-3:]]),16)}
    def getAlternateHeaders(self, limit=3):
        # Limit is 3 because afaik there are 4 available scenes 
        c = self.lookupCommand('18')
        if not c: # Some rooms don't have any alternate headers (e.g. dungeons)
            return None
        list_addr = self.start_addr + int(''.join([str(i) for i in c[5:]]))
        header_addresses = []
        for i in range(limit):
            addr = self.accessor.getData(list_addr+(i*4), size=4)
            if addr[0] != 0x03:
                if int(''.join([str(i) for i in addr]),16) == 0:
                    continue # Offset of 0 means it uses the original header
                raise Exception("Adress Segment is not 3, I probably wouldn't handle it correctly")
            header_addresses.append(self.start_addr + int(''.join([toHex(i) for i in addr[1:]]), 16))
        return header_addresses 
    def lookupCommand(self, num, isHex=True):
        dec_num = int(num, 16) if isHex else num
        possibleCommands = []
        for b in range(0, len(self.header), 8): # Each command is 8 bytes
            if self.header[b] == dec_num:
                possibleCommands.append(self.header[b:b+8])
        if len(possibleCommands) < 1:
            return None
        if len(possibleCommands) > 1:
            raise NotImplementedError("Looking up nonunique commands not yet implemented")
        return possibleCommands[0]