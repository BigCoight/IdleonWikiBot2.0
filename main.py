from re import T
import extractInfo
import updateItems
import updateNPCs


def main():
    extractInfo.main(r"./input/codefile/idleon114b.txt")
    updateNPCs.main(True, False)
    extractInfo.main(r"./input/codefile/idleon120b.txt")
    updateNPCs.main(False, True)


if __name__ == "__main__":
    main()
