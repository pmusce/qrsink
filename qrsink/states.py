# inflow = (0, 1)
class Value():
    def __eq__(self, other):
        return self.val == other.val and self.der == other.der

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


class State():
    def __init__(self, inflow, volume, outflow):
        self.inflow = inflow
        self.volume = volume
        self.outflow = outflow

    def __str__(self):
        return "%s %s %s" % (self.inflow, self.volume, self.outflow)

    def __eq__(self, other):
        return self.inflow == other.inflow and self.volume == other.volume and self.outflow == other.outflow

    @staticmethod
    def create(inflow, volume, outflow):
        return State(Inflow(inflow), Volume(volume), Outflow(outflow))

    def is_valid(self, debug):
        if not self.inflow.is_valid():
            if debug:
                print "%s Failed: extreme value check (inflow)" % self
            return False
        if not self.volume.is_valid():
            if debug:
                print "%s Failed: extreme value check (volume)" % self
            return False
        if not self.outflow.is_valid():
            if debug:
                print "%s Failed: extreme value check (outflow)" % self
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
                print "%s Failed: proportionality check" % self
            return False
        return True

    def check_proportionality(self):
        return self.volume.der == self.outflow.der

    def check_correspondence(self):
        if self.volume.val == 0 or self.outflow.val == 0:
            if self.volume.val != self.outflow.val:
                return False
        if self.volume.val == 2 or self.outflow.val == 2:
            if self.volume.val != self.outflow.val:
                return False
        return True

    def check_influence(self):
        if self.inflow.val == 0 and self.outflow.val == 0:
            return self.volume.der == 0
        if self.inflow.val == 0:
            return self.volume.der == -1
        if self.outflow.val == 0:
            return self.volume.der == 1
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

    def check_continuity(self, succ):
        if not self.inflow.check_continuity(succ.inflow):
            print "%s -> %s Dropped: continuity check(inflow)" % (self, succ)
            return False
        if not self.volume.check_continuity(succ.volume):
            print "%s -> %s Dropped: continuity check(volume)" % (self, succ)
            return False
        if not self.outflow.check_continuity(succ.outflow):
            print "%s -> %s Dropped: continuity check(outflow)" % (self, succ)
            return False

        return True

    def check_points(self, succ):
        if not self.check_change_on_instable_point(succ):
            return False
        if self.inflow.is_point() and not self.inflow.is_stable():
            # point to interval and interval to point at the same time
            if not self.volume.is_point() and self.volume.der != succ.volume.der:
                print "%s -> %s Dropped: point to interval and not exogenous interval to point at the same time(volume)" % (self, succ)
                return False
            if not self.outflow.is_point() and self.outflow.der != succ.outflow.der:
                print "%s -> %s Dropped: point to interval and not exogenous interval to point at the same time(outflow)" % (self, succ)
                return False

        if self.volume.is_point() and not self.volume.is_stable():
            if not self.inflow.is_stable() and self.inflow.der != succ.inflow.der:
                print "%s -> %s Dropped: invalid change of derivative for exogenous(inflow)" % (self, succ)
                return False

            # point to interval and interval to point at the same time
            if not self.outflow.is_point() and self.outflow.der != succ.outflow.der:
                print "%s -> %s Dropped: point to interval and not exogenous interval to point at the same time(outflow)" % (self, succ)
                return False

        if self.outflow.is_point() and not self.outflow.is_stable():
            if not self.inflow.is_stable() and self.inflow.der != succ.inflow.der:
                print "%s -> %s Dropped: invalid change of derivative for exogenous(inflow)" % (self, succ)
                return False

            # point to interval and interval to point at the same time
            if not self.volume.is_point() and self.volume.der != succ.volume.der:
                print "%s -> %s Dropped: point to interval and not exogenous interval to point at the same time(volume)" % (self, succ)
                return False

        return True

    def check_change_on_instable_point(self, succ):
        if self.inflow.is_point() and not self.inflow.is_stable():
            if not self.inflow.apply_der(succ.inflow):
                print "%s -> %s Dropped: check change on instable point failed(inflow)" % (self, succ)
                return False
        if self.volume.is_point() and not self.volume.is_stable():
            if not self.volume.apply_der(succ.volume):
                print "%s -> %s Dropped: check change on instable point failed(volume)" % (self, succ)
                return False
        if self.outflow.is_point() and not self.outflow.is_stable():
            if not self.outflow.apply_der(succ.outflow):
                print "%s -> %s Dropped: check change on instable point failed(outflow)" % (self, succ)
                return False
        return True

    @staticmethod
    def generate_all_valid(debug=False):
        graph = []
        for i_val in Inflow.domain:
            for v_val in Volume.domain:
                for i_der in Inflow.der_domain:
                    for v_der in Volume.der_domain:
                        for o_val, o_der in [(o_val, o_der) for o_val in Outflow.domain for o_der in Outflow.der_domain]:
                            s = State.create(
                                (i_val, i_der), (v_val, v_der), (o_val, o_der))
                            if s.is_valid(debug):
                                if debug:
                                    print "%s is a valid state" % s
                                graph.append(s)
        return graph
