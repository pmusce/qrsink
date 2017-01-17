import model
import itertools


class Value():
    def __eq__(self, other):
        return self.val == other.val and self.der == other.der

    def __ne__(self, other):
        return not self.__eq__(other)

    def is_stable(self):
        return self.der == 0

    def apply_der(self, succ):
        if self.is_stable():
            raise ValueError()
        if self.der != succ.der:
            return False
        return self.val + self.der == succ.val

    def check_continuity(self, succ):
        if abs(self.val - succ.val) > 1:
            return False
        if abs(self.der - succ.der) > 1:
            return False
        if not self.is_point() and succ.val != self.val:
            if succ.val - self.val != self.der:
                return False
        if self.is_stable() and self.val != succ.val:
            return False
        return True


class Inflow(Value):
    domain = [0, 1]
    der_domain = [-1, 0, 1]

    def __init__(self, args):
        self.val = args[0]
        self.der = args[1]

    def __str__(self):
        return "I[%s,%s]" % (self.val, self.der)

    def is_valid(self):
        if self.val == 0 and self.der == -1:
            return False
        return True

    def is_point(self):
        return self.val == 0


class Volume(Value):
    domain = [0, 1, 2]
    der_domain = [-1, 0, 1]

    def __init__(self, args):
        self.val = args[0]
        self.der = args[1]

    def __str__(self):
        return "V[%s,%s]" % (self.val, self.der)

    def is_valid(self):
        if self.val == 0 and self.der == -1:
            return False
        if self.val == 2 and self.der == 1:
            return False
        return True

    def is_point(self):
        return self.val == 0 or self.val == 2


class Outflow(Value):
    domain = [0, 1, 2]
    der_domain = [-1, 0, 1]

    def __init__(self, args):
        self.val = args[0]
        self.der = args[1]

    def __str__(self):
        return "O[%s,%s]" % (self.val, self.der)

    def is_valid(self):
        if self.val == 0 and self.der == -1:
            return False
        if self.val == 2 and self.der == 1:
            return False
        return True

    def is_point(self):
        return self.val == 0 or self.val == 2


class Height(Volume):
    def __str__(self):
        return "H[%s,%s]" % (self.val, self.der)


class Pressure(Volume):
    def __str__(self):
        return "P[%s,%s]" % (self.val, self.der)


class State():
    def __init__(self, inflow, volume, outflow, height, pressure):
        self.model = model.create()
        self.quantities = {}

        self.add_quantity('inflow', inflow)
        self.add_quantity('volume', volume)
        self.add_quantity('height', height)
        self.add_quantity('pressure', pressure)
        self.add_quantity('outflow', outflow)

    def add_quantity(self, key, value):
        self.quantities[key] = value

    def __str__(self):
        string = ""
        for key, qnt in self.quantities.iteritems():
            string += "%s " % (qnt)

        return string

    def __eq__(self, other):
        for key, qnt in self.quantities.iteritems():
            if self.quantities[key] != other.quantities[key]:
                return False
        return True

    @staticmethod
    def create(inflow, volume, outflow, height, pressure):
        return State(Inflow(inflow), Volume(volume), Outflow(outflow), Height(height), Pressure(pressure))

    def is_valid(self, debug):
        for key, qnt in self.quantities.iteritems():
            if not qnt.is_valid():
                if debug:
                    print "%s Failed: extreme value check (%s)" % self, key
                return False

        if not self.check_correspondence():
            if debug:
                print "%s Failed: correspondence check" % self
            return False
        if not self.check_proportionality():
            if debug:
                print "%s Failed: proportionality check" % self
            return False
        if not self.check_influence():
            if debug:
                print "%s Failed: influence check" % self
            return False
        return True

    def check_proportionality(self):
        for a, b in self.model.p_prop:
            if self.quantities[a].der != self.quantities[b].der:
                return False

        for a, b in self.model.n_prop:
            if self.quantities[a].der != (self.quantities[b].der * -1):
                return False

        return True

    def check_correspondence(self):
        for a, valA, b, valB in self.model.corr:
            if self.quantities[a].val == valA or self.quantities[b].val == valB:
                if self.quantities[a].val != self.quantities[b].val:
                    return False
        return True

    def check_influence(self):
        if self.quantities['inflow'].val == 0 and self.quantities['outflow'].val == 0:
            return self.quantities['volume'].der == 0
        if self.quantities['inflow'].val == 0:
            return self.quantities['volume'].der == -1
        if self.quantities['outflow'].val == 0:
            return self.quantities['volume'].der == 1
        return True

    def check_continuity(self, succ):
        for key, qnt in self.quantities.iteritems():
            if not qnt.check_continuity(succ.quantities[key]):
                print "%s -> %s Dropped: continuity check(%s)" % (self, succ, key)
                return False
        return True

    def check_points(self, succ):
        if not self.check_change_on_instable_point(succ):
            return False

        for key, qnt in self.quantities.iteritems():
            if qnt.is_point() and not qnt.is_stable():
                for key2 in self.quantities:
                    if key == key2:
                        continue

                    if key2 in self.model.exogen:
                        if not self.quantities[key2].is_stable() and self.quantities[key2].der != succ.quantities[key2].der:
                            print "%s -> %s Dropped: invalid change of derivative for exogenous(%s)" % (self, succ, key2)
                            return False
                    else:
                        if not self.quantities[key2].is_point() and self.quantities[key2].der != succ.quantities[key2].der:
                            print "%s -> %s Dropped: point to interval and not exogenous interval to point at the same time(%s)" % (self, succ, key2)
                            return False
        return True

    def check_change_on_instable_point(self, succ):
        for key, qnt in self.quantities.iteritems():
            if qnt.is_point() and not qnt.is_stable():
                if not qnt.apply_der(succ.quantities[key]):
                    print "%s -> %s Dropped: check change on instable point failed(%s)" % (self, succ, key)
                    return False
        return True

    def generate_successors(self):
        successors = []
        for s in self.generate_all_valid():
            if s == self:
                continue
            if not self.check_continuity(s):
                continue
            if not self.check_points(s):
                continue
            successors.append(s)
            print "%s -> %s Valid successor" % (self, s)

        return successors

    @staticmethod
    def generate_all_valid(debug=False):
        graph = []
        a = []
        for qnt in [Inflow, Volume, Outflow, Height, Pressure]:
            a.append(qnt.domain)
            a.append(qnt.der_domain)

        for i_val, i_der, v_val, v_der, o_val, o_der, h_val, h_der, p_val, p_der in list(itertools.product(*a)):
            s = State.create((i_val, i_der), (v_val, v_der), (o_val, o_der), (h_val, h_der), (p_val, p_der))
            if s.is_valid(debug):
                if debug:
                    print "%s is a valid state" % s
                graph.append(s)

        return graph
