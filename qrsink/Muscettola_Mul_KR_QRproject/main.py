#!/usr/bin/python
from graphviz import Digraph
from states import *
import string

# translate 0, 1 scale to max, + as in exercise statement?


def main():
    dot = Digraph(comment='Transition Graph')

    g = State.generate_all_valid()

    # j = 1
    for i, state in enumerate(g):
        description = string.replace(str(state), '2', 'max')
        description = string.replace(description, '-1', '-')
        description = string.replace(description, '1', '+')
        dot.node(str(i), description)

    for i, s in enumerate(g):

        print "%d) %s" % (i + 1, s)
        for x in s.generate_successors():

            dot.edge(str(i), str(g.index(x)))
    print "# states = %d" % len(g)

    dot.render('test-output/state-graph.gv', view=True)


if __name__ == "__main__":
    main()
