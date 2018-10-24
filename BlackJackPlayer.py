from __future__ import print_function, division
from pprint import pprint


def create_state_space():
    S = {'B', 'L', 'W', 'P'}

    false = 0
    true = 1

    # Non pair non ace containing initial hands
    S.update('{}_{}_{}_{}_{}'.format(i, i, j, false, true)
             for i in xrange(5, 21) for j in xrange(1, 11))

    # Non pair ace containing initial hands
    S.update('{}_{}_{}_{}_{}'.format(i+1, i+11, j, false, true)
             for i in xrange(2, 10) for j in xrange(1, 11))

    # Pair containing initial hands
    S.update('{}_{}_{}_{}_{}'.format(2*i, 2*i, j, true, true)
             for i in xrange(1, 11) for j in xrange(1, 11))

    # Non pair non ace containing non initial hands
    S.update('{}_{}_{}_{}_{}'.format(i, i, j, false, false)
             for i in xrange(5, 22) for j in xrange(1, 11))

    # Non pair ace containing non initial hands
    S.update('{}_{}_{}_{}_{}'.format(i+1, i+11, j, false, false)
             for i in xrange(2, 10) for j in xrange(1, 11))
    return S


def main():
    states = create_state_space()

    pprint(states)
    print(len(states))


if __name__ == '__main__':
    main()