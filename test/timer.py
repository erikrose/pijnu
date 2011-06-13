# -*- coding: utf8 -*-

'''
© 2009 Denis Derman (former developer) <denis.spir@gmail.com>
© 2011 Peter Potrowl (current developer) <peter017@gmail.com>

This file is part of PIJNU.

PIJNU is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PIJNU is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PIJNU: see the file called 'GPL'.
If not, see <http://www.gnu.org/licenses/>.
'''

'''
Overall timer func -- just case needed
'''

from time import time

__all__ = ['timer']


def timer(n, f, *args, **kw_args):
    t0 = time()
    for i in range(n):
        f(*args, **kw_args)
    t = time() - t0
    arg_str = ','.join(repr(arg) for arg in args)
    kw_arg_str = (',' + str(kw_args)[1:-1]) if kw_args else ''
    print     "%s(%s%s) %s time(s) <--> %0.3f s" \
            % (f.__name__, arg_str, kw_arg_str, n, t)


########## test ##########
if __name__ == "__main__":
    def sum2(x, y):
        return x + y
    timer(100000, sum2, 2, 3)

    from math import sqrt

    def mean(seq, geom=False):

        def sum(seq):
            sum = 0
            for x in seq:
                sum += x
            return sum
        if geom:
            squares = (x * x for x in seq)
            return sqrt(sum(squares))
        else:
            return sum(seq) / len(seq)

    seq = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    timer(100000, mean, seq)
    timer(100000, mean, seq, geom=True)
