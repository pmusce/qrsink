from graphviz import Digraph
from states import *


def main():
    dot = Digraph(comment='Transition Graph')

    g = State.generate_all_valid()

    for i, state in enumerate(g):
        dot.node(str(i), str(state))
    for i, s in enumerate(g):

        print "%d) %s" % (i + 1, s)
        for x in s.generate_successors():
            print "--> %d | %s" % (g.index(x) + 1, x)

            dot.edge(str(i), str(g.index(x)))
    print "# states = %d" % len(g)

    dot.render('test-output/state-graph.gv', view=True)


if __name__ == "__main__":
    main()
