import os
from nms_pss import nms_pss

# Some helper functions

def getPokemonOnDisk():
    out = []
    for f in os.scandir():
        if f.is_file():
            if f.name.endswith('.nmsc'):
                out.append(f.name[:-5])
    return out

def inputConvert(prompt, isNumeric=True):
    out = input(prompt)
    if out == 'x' or out == 'X':
        return 'x'
    if isNumeric:
        try:
            out = int(out)
        except ValueError:
            return None
    return out

def inputIn(prompt, validlist, isNumeric=True):
    out = inputConvert(prompt, isNumeric)
    while out not in validlist and out != 'x':
        print ("Invalid choice. Try again.")
        out = inputConvert(prompt, isNumeric)
    return out

pss = nms_pss()

# Text Interface
print("\n\n\n\n")
print("Welcome to the NMS Companion Storage System!\n\n")

print("Choose a save to work with...")
availableSaveSlots = pss.getAvalibleSaveSlots()
for s in availableSaveSlots:
    print(pss.getSaveSlotDesc(s))

saveslot = inputIn(", ".join(map(str, availableSaveSlots))+", or X to exit > ", availableSaveSlots)
if saveslot == 'x': os._exit(0)

pss.openSaveSlot(saveslot)

while True:
    usedSlots = pss.getUsedSlots()
    freeSlots = pss.getFreeSlots()

    print("\n\nListing available creatures...")
    for i in range(1, 7):
        print("{}: {}".format(i, pss.getPokemonSlotDesc(i)))

    # Check for free slot, otherwise we can't get from box
    if len(freeSlots) < 1:
        print("\nChoose operation:\n1. Store creature in box")
        operation = inputIn("1 or X to exit >", [1])
    else:
        print("\nChoose operation:\n1. Store creature in box\n2. Get creature from box")
        operation = inputIn("1, 2, or X to exit >", [1,2])

    if operation == 'x': os._exit(0)
    if operation == 1:
        print ("Box which creature?")
        creatureslot = inputIn(", ".join(map(str, usedSlots))+", or X to return > ", usedSlots)
        if creatureslot == 'x': continue
        print ("Choose a filename for the creature")
        fn = input("filename, or x to return > ")
        if fn == 'x': continue
        while os.path.isfile(fn):
            print("Error: The filename already exists. Choose another")
            fn = input("> ")
        # Transferring to box!
        print("\nTransfering creature to box!")
        pss.boxPokemon(fn, creatureslot)
        print("Done!")
    else:
        print("\nListing boxed crearures...")
        boxedCreatures = getPokemonOnDisk()
        for i in boxedCreatures:
            print(i)
        print("Choose creature to get.")
        fn = inputIn("filename, or x to return > ", boxedCreatures, isNumeric=False)
        if fn == 'x': continue
        # Transferring from box!
        print("\nTransfering creature from box!")
        pss.unboxPokemon(fn)
        print("Done!")
