from graphviz import Digraph

dot = Digraph(comment='Transition Graph')

states = range(24)
transitions = [(1,2), (2,3), (3,4)]

for s in states:
    name = str(s) # state description goes here
    description = name
    dot.node(name, description)

for t in transitions:
    node_1 = str(t[0])
    node_2 = str(t[1])
    dot.edge(node_1, node_2)

#dot.edges(['AB', 'AL'])
#dot.edge('B', 'L', constraint='false')

dot.render('test-output/state-graph.gv', view=True)