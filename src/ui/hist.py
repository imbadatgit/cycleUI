#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""hist.py: implementation of a ring buffer to store a history of numbers"""

class HistoryIter:
    """iterator over history in chronological order"""

    def __init__(self, hist):
        self.hist = hist

        # check if the container is actually full
        if self.hist.wrapped:
            self.cur = self.hist._nextpos(self.hist.cur)
        else:
            self.cur = 0
        self.done = False

    def __iter__(self):
        self.done = False
        return self

    def next(self):
        if self.done:
            raise StopIteration()
        elif self.cur == self.hist.cur:
            self.done = True

        current = self.hist.hist[self.cur]
        self.cur = self.hist._nextpos(self.cur)

        return current

class History:            
    """implementation of a history of numbers, essentially a queue"""
    def __init__(self, histlen):
        self.histlen = histlen
        self.hist = [None] * histlen
        self.cur = -1
        self.wrapped = False

    def __iter__(self):
        return HistoryIter(self)

    def _nextpos(self,i):
        """
        Calculate next position given after i
        Essentially: loop around if i+1 exceeds size
        """
        i += 1
        if i == self.histlen:
            self.wrapped = True
            return 0
        else:
            return i

    def _move(self):
        """move the position index"""
        self.cur = self._nextpos(self.cur)

    def add(self, data):
        """move to the next spot and add element"""
        self._move()
        self.hist[self.cur] = data

    def mean(self):
        s = 0
        n = 0
        for el in self.hist:
            if el != None:
                s += el
                n += 1
        if n == 0:
            return 0
        return s/float(n)

    

if __name__ == "__main__":
    h = History(5)
    print h.mean()

    h.add(1.)
    h.add(9.)
    print h.mean()

    for i in xrange(5):
        h.add(i)
    print h.mean()

    # test iter
    h2 = History(5)
    h2.add(1)
    h2.add(2)

    hi = HistoryIter(h2)
    for i in hi:
        print i







