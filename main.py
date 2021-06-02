from re import T
import extractInfo
import updateItems
import updateNPCs
import updateEnemies


def main(oldFn, newFn):
    extractInfo.main(fr"./input/codefile/idleon{oldFn}.txt")
    updateItems.main(True, False)
    updateNPCs.main(True, False)
    updateEnemies.main(True, False)
    extractInfo.main(fr"./input/codefile/idleon{newFn}.txt")
    updateItems.main(False, True)
    updateNPCs.main(False, True)
    updateEnemies.main(False, True)


if __name__ == "__main__":
    main("114b", "120b")
