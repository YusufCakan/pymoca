from collections import OrderedDict, MutableSet

# From https://code.activestate.com/recipes/576694/
class OrderedSet(MutableSet):

    def __init__(self, iterable=None):
        self.end = end = [] 
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def __getitem__(self, index):
        # Method added by JB
        if isinstance(index, slice):
            start, stop, stride = index.indices(len(self))
            return [self.__getitem__(i) for i in range(start, stop, stride)]
        else:
            end = self.end
            curr = end[2]
            i = 0
            while curr is not end:
                if i == index:
                    return curr[0]
                curr = curr[2]
                i += 1
            raise IndexError('set index {} out of range with length {}'.format(index, len(self)))

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:        
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)
# End snippet


# Code snippet from RTC-Tools, copyright Stichting Deltares, originally under the terms of the GPL
# version 3.  Relicensed with permission.
class AliasRelation:
    def __init__(self):
        self._aliases = {}
        self._canonical_variables = OrderedSet()

    def add(self, a, b):
        # Get the canonical names and signs
        canonical_a, sign_a = self.canonical_signed(a)
        canonical_b, sign_b = self.canonical_signed(b)

        # Determine if signs need to be inverted when merging the aliased sets
        opposite_signs = (sign_a + sign_b) == 0

        # Construct aliases (a set of equivalent variables)
        aliases = self.aliases(canonical_a)
        for v in self.aliases(canonical_b):
            if opposite_signs:
                v = self.__toggle_sign(v)
            aliases.add(v)

        # Update _aliases so that keys are always positive
        inverted_aliases = OrderedSet([self.__toggle_sign(v) for v in aliases])
        for v in aliases:
            if v[0] == '-':
                self._aliases[self.__toggle_sign(v)] = inverted_aliases
            else:
                self._aliases[v] = aliases

        # Update _canonical_variables with new canonical var and remove old ones
        self._canonical_variables.add(aliases[0])
        for v in aliases[1:]:
            if v[0] == '-':
                v = self.__toggle_sign(v)
            try:
                self._canonical_variables.remove(v)
            except KeyError:
                pass

    def __toggle_sign(self, v):
        if v[0] == '-':
            return v[1:]
        else:
            return '-' + v

    def aliases(self, a):
        return self._aliases.get(a, OrderedSet([a]))

    def canonical_signed(self, a):
        if a[0] == '-':
            top_alias = self.aliases(self.__toggle_sign(a))[0]
        else:
            top_alias = self.aliases(a)[0]

        if top_alias[0] == '-':
            return top_alias[1:], 1 if a[0] == '-' else -1
        else:
            return top_alias, -1 if a[0] == '-' else 1

    @property
    def canonical_variables(self):
        return self._canonical_variables

    def __iter__(self):
        return ((canonical_variable, self.aliases(canonical_variable)[1:]) for canonical_variable in self._canonical_variables)
