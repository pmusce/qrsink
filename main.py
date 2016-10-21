from states import *


def main():
    g = State.generate_all_valid()
    for i, s in enumerate(g):
        print "%d) %s" % (i + 1, s)
        for x in s.generate_successors():
            print "--> %d | %s" % (g.index(x) + 1, x)

    print "# states = %d" % len(g)


if __name__ == "__main__":
    main()
