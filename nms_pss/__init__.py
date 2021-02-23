import json
import os
import time

# Opens a NMS save file and provide functions to export and import creatures
class nms_pss:
    # json key lookup
    __PlayerStateData = "6f="
    __BoxSlotUnlock = "9Lg"
    __Box = "Mcl"
    __BoxCustoms = "j30"
    __CreatureID = "XID"
    __CustomName = "fH8"

    __EmptySlot = json.loads(
    '{"main":{"unY":1.0,"XID":"^","osl":[],"WTp":[false,"0x0"],"1p=":[false,"0x0"],"m9o":0,"JrL":0,"Q6I":false,"5L6":0,"uAX":[false,"0x0"],"6fX":[false,"0x0"],"8jm":{"8jm":"Lush"},"HbY":{"HbY":"None"},"XwC":0,"tDR":0,"KY5":0,"@Hb":0,"eK9":false,"WQX":true,"fH8":"","xDJ":0.0,"JAy":[0.0,0.0,0.0],"IEo":[0.0,0.0]},"cust":{"8?J":[{"VFd":"^","wnR":{"SMP":[],"Aak":[{"RVl":{"RVl":"Paint","Ty=":"Primary"},"xEg":[1.0,0.5199999809265137,0.0,1.0]},{"RVl":{"RVl":"Paint","Ty=":"Alternative1"},"xEg":[1.0,1.0,1.0,1.0]}],"T>1":[],"gsg":[],"unY":1.0}},{"VFd":"^","wnR":{"SMP":[],"Aak":[{"RVl":{"RVl":"Paint","Ty=":"Primary"},"xEg":[1.0,0.5199999809265137,0.0,1.0]},{"RVl":{"RVl":"Paint","Ty=":"Alternative1"},"xEg":[1.0,1.0,1.0,1.0]}],"T>1":[],"gsg":[],"unY":1.0}},{"VFd":"^","wnR":{"SMP":[],"Aak":[{"RVl":{"RVl":"Paint","Ty=":"Primary"},"xEg":[1.0,0.5199999809265137,0.0,1.0]},{"RVl":{"RVl":"Paint","Ty=":"Alternative1"},"xEg":[1.0,1.0,1.0,1.0]}],"T>1":[],"gsg":[],"unY":1.0}}]}}'
    )

    __SavePath = None

    __SaveSlotPath = None
    __SaveJSON = None
    __SaveSlot = None

    def __getSavePath(self):
        if self.__SavePath:
            return self.__SavePath

        savepath = os.getenv('APPDATA')+"/HelloGames/NMS"
        if not os.path.isdir(savepath):
            raise Exception("NMS save directory not found")

        if os.path.isdir(savepath+"/DefaultUser"):
            self.__SavePath = savepath+"/DefaultUser"
            return self.__SavePath

        for f in os.scandir(savepath):
            if f.is_dir():
                if f.name.startswith('st_'):
                    self.__SavePath = f.path
                    return self.__SavePath

        raise OSError("NMS save directory not found")

    def __getPathFromSlot(self, slot, hashfile = False):
        key = str((slot*2)-1) if slot > 1 else ''
        prefix = "mf_" if hashfile else ""

        return self.__getSavePath()+"/"+prefix+"save"+key+".hg"

    def __checkOpen(self):
        if self.__SaveSlot == None:
            raise Exception("Save slot must be opened first")

    def __appendFileExt(self, fn):
        # Append .nmsc if no extension
        _, file_extension = os.path.splitext(fn)
        if file_extension == "":
            return fn + ".nmsc"
        return fn

    def __pokemonToDisk(self, fn, pkm):
        fn = self.__appendFileExt(fn)
        with open(fn, 'w', encoding = 'cp850') as savefile:
            savefile.write(json.dumps(pkm, separators=(',', ':')))

    def __pokemonFromDisk(self, fn):
        fn = self.__appendFileExt(fn)
        with open(fn, encoding = 'cp850') as savefile:
            savestr = savefile.read()
        pkm = json.loads(savestr)
        if 'main' not in pkm or 'cust' not in pkm:
            raise Exception("Invalid creature file!")
        return pkm

    def __deletePokemonFromDisk(self, fn):
        fn = self.__appendFileExt(fn)
        os.remove(fn)

    def __getPokemonFromSlot(self, slot, clear = False):
        self.__checkOpen()
        slot -= 1
        # export from slot
        export = {}
        export['main'] = self.__SaveJSON[self.__PlayerStateData][self.__Box][slot]
        export['cust'] = self.__SaveJSON[self.__PlayerStateData][self.__BoxCustoms][slot]

        # clear the slot
        if clear:
            self.__SaveJSON[self.__PlayerStateData][self.__Box][slot] = self.__EmptySlot['main']
            self.__SaveJSON[self.__PlayerStateData][self.__BoxCustoms][slot] = self.__EmptySlot['cust']

        return export

    def __putPokemonInSlot(self, slot, pkm):
        self.__checkOpen()
        slot -= 1
        self.__SaveJSON[self.__PlayerStateData][self.__Box][slot] = pkm['main']
        self.__SaveJSON[self.__PlayerStateData][self.__BoxCustoms][slot] = pkm['cust']

    def boxPokemon(self, fn, slot):
        pkm = self.__getPokemonFromSlot(slot, clear=True)
        self.__pokemonToDisk(fn, pkm)
        self.writeSaveSlot()

    def unboxPokemon(self, fn):
        pkm = self.__pokemonFromDisk(fn)
        slot = self.getFirstFreeSlot()
        self.__putPokemonInSlot(slot, pkm)
        self.writeSaveSlot()
        self.__deletePokemonFromDisk(fn)
        return slot

    def getPokemonSlotInfo(self, slot):
        self.__checkOpen()
        slot -= 1
        out = {}
        pkm = self.__SaveJSON[self.__PlayerStateData][self.__Box][slot]
        out['locked'] = not self.__SaveJSON[self.__PlayerStateData][self.__BoxSlotUnlock][slot]
        out['empty'] = (pkm[self.__CreatureID] == "^")
        out['name'] = pkm[self.__CustomName] if pkm[self.__CustomName] != "" else '<UNNAMED>'
        out['type'] = pkm[self.__CreatureID][1:]
        return out

    def getPokemonSlotDesc(self, slot):
        info = self.getPokemonSlotInfo(slot)
        if info['locked']:
            return '[LOCKED]'
        if info['empty']:
            return '[EMPTY]'
        return "Name: {}  Type: {}".format(info['name'], info['type'])

    def getUnlockedSlots(self):
        self.__checkOpen()
        slots = []
        for i in range(6):
            if self.__SaveJSON[self.__PlayerStateData][self.__BoxSlotUnlock][i] == True:
                slots.append(i+1)
        return slots

    def getUsedSlots(self):
        self.__checkOpen()
        slots = []
        for i in range(6):
            if self.__SaveJSON[self.__PlayerStateData][self.__Box][i][self.__CreatureID] != "^":
                slots.append(i+1)
        return slots

    def getFreeSlots(self):
        usedSlots = self.getUsedSlots()
        unlockedSlots = self.getUnlockedSlots()
        return [x for x in range(6) if x not in usedSlots and x in unlockedSlots]

    def getFirstFreeSlot(self):
        self.__checkOpen()
        for i in range(6):
            if self.__SaveJSON[self.__PlayerStateData][self.__BoxSlotUnlock][i] == True and \
               self.__SaveJSON[self.__PlayerStateData][self.__Box][i][self.__CreatureID] == "^":
                return i+1

    def getSaveSlotDesc(self, slot):
        mtime = os.path.getmtime(self.__getPathFromSlot(slot))
        return "SLOT {} - Saved at {}".format(slot,
            time.strftime("%d-%m-%y %H:%M", time.localtime(mtime)))

    def getAvalibleSaveSlots(self):
        slots = []
        for i in range(1,6):
            if os.path.isfile(self.__getPathFromSlot(i)):
                slots.append(i)
        return slots

    def openSaveSlot(self, slot):
        self.__SaveSlot = slot
        self.__SaveSlotPath = self.__getPathFromSlot(slot)
        with open(self.__SaveSlotPath, encoding = 'cp850') as savefile:
            savestr = savefile.read()
        self.__SaveJSON = json.loads(savestr[:-1])

    def writeSaveSlot(self):
        self.__checkOpen()
        outstr = json.dumps(self.__SaveJSON, separators=(',', ':'))
        outstr += chr(0)
        with open(self.__SaveSlotPath, 'w', encoding = 'cp850') as savefile:
            savefile.write(outstr)
        # This is horrible, but for the moment just delete the hash/checksum file
        try:
            os.remove(self.__getPathFromSlot(self.__SaveSlot, hashfile=True))
        except FileNotFoundError: pass
