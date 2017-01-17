class Model():
    def __init__(self):
        self.p_inf = []
        self.n_inf = []
        self.p_prop = []
        self.n_prop = []
        self.corr = []
        self.exogen = []

    def add_exogen_quantity(self, qnt):
        self.exogen.append(qnt)

    def add_p_influence(self, a, b):
        self.p_inf.append((a, b))

    def add_n_influence(self, a, b):
        self.n_inf.append((a, b))

    def add_p_proportionality(self, a, b):
        self.p_prop.append((a, b))

    def add_n_proportionality(self, a, b):
        self.n_prop.append((a, b))

    def add_correspondence(self, a, valA, b, valB):
        self.corr.append((a, valA, b, valB))


def create():
    model = Model()
    model.add_exogen_quantity('inflow')
    model.add_p_influence('inflow', 'volume')
    model.add_n_influence('outflow', 'volume')
    model.add_p_proportionality('volume', 'outflow')
    model.add_correspondence('volume', 2, 'outflow', 2)
    model.add_correspondence('volume', 0, 'outflow', 0)
    return model
