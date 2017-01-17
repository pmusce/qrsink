class Model():
    def __init__(self):
        # self.quantities = []
        self.p_inf = []
        self.n_inf = []
        self.p_prop = []
        self.n_prop = []
        self.corr = []
        self.exogen = []

    def add_quantity(self, qnt):
        self.quantities.append(qnt)

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
    # model.add_quantity('inflow')
    # model.add_quantity('volume')
    # model.add_quantity('outflow')

    model.add_exogen_quantity('inflow')
    model.add_p_influence('inflow', 'volume')
    model.add_n_influence('outflow', 'volume')
    model.add_p_proportionality('volume', 'height')
    model.add_p_proportionality('height', 'pressure')
    model.add_p_proportionality('pressure', 'outflow')

    model.add_correspondence('volume', 0, 'height', 0)
    model.add_correspondence('volume', 2, 'height', 2)

    model.add_correspondence('height', 0, 'pressure', 0)
    model.add_correspondence('height', 2, 'pressure', 2)

    model.add_correspondence('pressure', 0, 'outflow', 0)
    model.add_correspondence('pressure', 2, 'outflow', 2)
    return model
