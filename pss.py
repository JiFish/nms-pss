import json
import os
import time

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

def getSavePath():
    global __SavePath

    if __SavePath:
        return __SavePath

    savepath = os.getenv('APPDATA')+"/HelloGames/NMS"
    if not os.path.isdir(savepath):
        raise Exception("NMS save directory not found")

    if os.path.isdir(savepath+"/DefaultUser"):
        __SavePath = savepath+"/DefaultUser"
        return __SavePath

    for f in os.scandir(savepath):
        if f.is_dir():
            if f.name.startswith('st_'):
                __SavePath = f.path
                return __SavePath

    raise Exception("NMS save directory not found")

def getPathFromSlot(slot, hashfile = False):
    key = str((slot*2)-1) if slot > 1 else ''
    prefix = "mf_" if hashfile else ""

    return getSavePath()+"/"+prefix+"save"+key+".hg"

def getSaveSlotDesc(slot):
    mtime = os.path.getmtime(getPathFromSlot(slot))
    return "SLOT {} - Saved at {}".format(slot,
        time.strftime("%d-%m-%y %H:%M", time.localtime(mtime)))

def getAvalibleSaveSlots():
    slots = []
    for i in range(1,6):
        if os.path.isfile(getPathFromSlot(i)):
            slots.append(i)
    return slots

def getSave(slot):
    path = getPathFromSlot(slot)
    with open(path, encoding = 'cp850') as savefile:
        savestr = savefile.read()
    savedict = json.loads(savestr[:-1])
    return savedict

def writeSave(savedict, slot):
    path = getPathFromSlot(slot)
    outstr = json.dumps(savedict, separators=(',', ':'))
    outstr += chr(0)
    with open(path, 'w', encoding = 'cp850') as savefile:
        savefile.write(outstr)
    # This is horrible, but for the moment just delete the hash/checksum file
    try:
        os.remove(getPathFromSlot(slot, hashfile=True))
    except FileNotFoundError: pass

def pokemonToDisk(fn, pkm):
    fn += ".npkm"
    with open(fn, 'w', encoding = 'cp850') as savefile:
        savefile.write(json.dumps(pkm, separators=(',', ':')))

def pokemonFromDisk(fn):
    fn += ".npkm"
    with open(fn, encoding = 'cp850') as savefile:
        savestr = savefile.read()
    pkm = json.loads(savestr)
    if 'main' not in pkm or 'cust' not in pkm:
        raise Exception("Invalid creature file!")
    return pkm

def deletePokemonFromDisk(fn):
    fn += ".npkm"
    os.remove(fn)

def getPokemonOnDisk():
    out = []
    for f in os.scandir():
        if f.is_file():
            if f.name.endswith('.npkm'):
                out.append(f.name[:-5])
    return out

def getPokemonFromSlot(savedict, slot, clear = False):
    slot -= 1
    # export from slot
    export = {}
    export['main'] = savedict[__PlayerStateData][__Box][slot]
    export['cust'] = savedict[__PlayerStateData][__BoxCustoms][slot]

    # clear the slot
    if clear:
        savedict[__PlayerStateData][__Box][slot] = __EmptySlot['main']
        savedict[__PlayerStateData][__BoxCustoms][slot] = __EmptySlot['cust']

    return export

def putPokemonInSlot(savedict, slot, pkm):
    slot -= 1
    savedict[__PlayerStateData][__Box][slot] = pkm['main']
    savedict[__PlayerStateData][__BoxCustoms][slot] = pkm['cust']

def getPokemonDesc(pkm):
    if pkm['main'][__CreatureID] != "^":
        return "Name: {}  Type: {}".format(
            pkm['main'][__CustomName] if pkm['main'][__CustomName] != "" else 'UNNAMED',
            pkm['main'][__CreatureID][1:]
        )
    else:
        return '[EMPTY]'

def getUnlockedSlots(savedict):
    slots = []
    for i in range(6):
        if savedict[__PlayerStateData][__BoxSlotUnlock][i] == True:
            slots.append(i+1)
    return slots

def getUsedSlots(savedict):
    slots = []
    for i in range(6):
        if savedict[__PlayerStateData][__Box][i][__CreatureID] != "^":
            slots.append(i+1)
    return slots

def inputExiting(prompt, isNumeric=True):
    out = input(prompt)
    if out == 'x' or out == 'X':
        os._exit(0)
    if isNumeric:
        try:
            out = int(out)
        except ValueError:
            return None
    return out

def inputN(prompt, validlist, isNumeric=True):
    out = inputExiting(prompt, isNumeric)
    while out not in validlist:
        print ("Invalid choice. Try again.")
        out = inputExiting(prompt, isNumeric)
    return out

print("\n\n\n\n\n\n\n")
print("Welcome to the NMS Pokémon Storage System!\n\n")

print("Choose a save to work with...")
availableSaveSlots = getAvalibleSaveSlots()
for s in availableSaveSlots:
    print(getSaveSlotDesc(s))

saveslot = inputN(", ".join(map(str, availableSaveSlots))+", or X to exit > ", availableSaveSlots)
savedict = getSave(saveslot)

while True:
    usedSlots = getUsedSlots(savedict)
    unlockedSlots = getUnlockedSlots(savedict)
    freeSlots = [x for x in range(6) if x not in usedSlots and x in unlockedSlots]

    print("\n\nListing available creatures...")
    for i in range(1,7):
        if i not in unlockedSlots:
            print("{}: [LOCKED]".format(i))
        else:
            print("{}: {}".format(i, getPokemonDesc(getPokemonFromSlot(savedict, i))))

    print("\nChoose operation:\n1. Store creature in box\n2. Get creature from box")
    operation = inputN("1, 2, or X to exit >", [1,2])
    if operation == 1:
        print ("Box which creature?")
        creatureslot = inputN(", ".join(map(str, usedSlots))+", or X to exit > ", usedSlots)
        print ("Choose a filename for the creature")
        fn = input("> ")
        while os.path.isfile(fn):
            print("Error: The filename already exists. Choose another")
            fn = input("> ")
        # Transferring to box!
        print("\nTransfering creature to box!")
        pkm = getPokemonFromSlot(savedict, creatureslot, clear=True)
        pokemonToDisk(fn, pkm)
        writeSave(savedict, saveslot)
        print("Done!")
    else:
        # Check for free slot
        if len(freeSlots) < 1:
            print("Slots are full! Box a creature first.")
            continue
        print("\nListing boxed crearures...")
        boxedCreatures = getPokemonOnDisk()
        for i in boxedCreatures:
            print(i)
        print("Choose creature to get.")
        fn = inputN("> ", boxedCreatures, isNumeric=False)
        creatureslot = freeSlots[0]
        # Transferring from box!
        print("\nTransfering creature from box!")
        pkm = pokemonFromDisk(fn)
        putPokemonInSlot(savedict, creatureslot, pkm)
        writeSave(savedict, saveslot)
        deletePokemonFromDisk(fn)
        print("Done!")
