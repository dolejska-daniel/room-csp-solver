from constraint import Solver


class CommentedBacktrackingSolver(Solver):
    """ XXX. """

    def __init__(self, forwardcheck=True):
        """
        @param forwardcheck: If false forward checking will not be requested
                             to constraints while looking for solutions
                             (default is true)
        @type  forwardcheck: bool
        """
        self._forwardcheck = forwardcheck

    def getSolutionIter(self, domains, constraints, vconstraints):
        forwardcheck = self._forwardcheck
        assignments = {}

        queue = []

        while True:

            # Mix the Degree and Minimum Remaing Values (MRV) heuristics
            lst = [
                (-len(vconstraints[variable]), len(domains[variable]), variable)
                for variable in domains
            ]
            lst.sort()
            print("-> foreach variable")
            for item in lst:
                if item[-1] not in assignments:
                    # Found unassigned variable
                    variable = item[-1]
                    values = domains[variable][:]
                    print("\t-> variable without assignment:", variable)
                    print("\t-> possible assignments:", values)
                    if forwardcheck:
                        print("\t-> FORWARDCHECKING ON")
                        pushdomains = [
                            domains[x]
                            for x in domains
                            if x not in assignments and x != variable
                        ]
                        print("\t\t-> pushdomains:", pushdomains)
                    else:
                        pushdomains = None

                    print("\t-> using this vairable, continuing...")
                    break
            else:
                # No unassigned variables. We've got a solution. Go back
                # to last variable, if there's one.
                print("\t-> NO unassigned variables! solution found!")
                yield assignments.copy()
                if not queue:
                    return
                variable, values, pushdomains = queue.pop()
                if pushdomains:
                    for domain in pushdomains:
                        domain.popState()

            print("-> assigning variable values!")
            while True:
                # We have a variable. Do we have any values left?
                if not values:
                    print("\t-> NO possible assignment!")
                    # No. Go back to last variable, if there's one.
                    del assignments[variable]
                    print("\t-> while queue not empty")
                    while queue:
                        variable, values, pushdomains = queue.pop()
                        if pushdomains:
                            print("\t\t-> FORWARDCHECKING ON, foreach domain")
                            for domain in pushdomains:
                                print("\t\t\t-> poping domain")
                                domain.popState()
                        if values:
                            print("\t\t-> assignment possible again!")
                            break
                        del assignments[variable]
                    else:
                        print("\t\t-> NO SOULUTION FOR PROBLEM!")
                        return

                # Got a value. Check it.
                assignments[variable] = values.pop()
                print("\t-> assigning (and removing from domain):", assignments[variable])

                if pushdomains:
                    print("\t-> FORWARDCHECKING!")
                    for domain in pushdomains:
                        print("\t\t-> PUSHing new domain state")
                        domain.pushState()

                print("\t-> foreach constraint")
                for constraint, variables in vconstraints[variable]:
                    print("\t\t-> checking:", constraint)
                    if not constraint(variables, domains, assignments, pushdomains):
                        # Value is not good.
                        print("\t\t-> WRONG ASSIGNMENT!")
                        break

                    print("\t\t-> CORRECT ASSIGNMENT!")
                else:
                    print("\t\t-> assignment done correctly!")
                    break

                if pushdomains:
                    print("\t-> domain states available")
                    for domain in pushdomains:
                        print("\t\t-> POPing new domain state")
                        domain.popState()

            # Push state before looking for next variable.
            queue.append((variable, values, pushdomains))
            print("\t-> adding state to queue:", (variable, values, pushdomains))

        raise RuntimeError("Can't happen")

    def getSolution(self, domains, constraints, vconstraints):
        iter = self.getSolutionIter(domains, constraints, vconstraints)
        try:
            return next(iter)
        except StopIteration:
            return None

    def getSolutions(self, domains, constraints, vconstraints):
        return list(self.getSolutionIter(domains, constraints, vconstraints))
