from __future__ import print_function, division
from pprint import pprint


def create_state_space():
    S = {'B'}

    # Hard numbers
    S.update(
        'H_{}_{}'.format(i, j) for i in xrange(5, 22) for j in xrange(1, 11))

    # Soft numbers
    S.update(
        'S_{}_{}'.format(i, j) for i in xrange(2, 10) for j in xrange(1, 11))

    # Doubled hard numbers
    S.update(
        'DH_{}_{}'.format(i, j) for i in xrange(5, 21) for j in xrange(1, 11))

    # Doubled soft numbers
    S.update(
        'DS_{}_{}'.format(i, j) for i in xrange(2, 10) for j in xrange(1, 11))

    # Split numbers
    S.update(
        'P_{}_{}'.format(i, j) for i in xrange(1, 11) for j in xrange(1, 11))

    return S


def main():
    states = create_state_space()

    pprint(states)
    print(len(states))


if __name__ == '__main__':
    main()