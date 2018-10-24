from __future__ import print_function, division
from pprint import pprint


def create_state_space():
    S = {'TB', 'TL', 'TW', 'TP'}

    false = 0
    true = 1

    # Non pair non ace containing initial hands
    S.update('{}_{}_{}_{}_{}'.format(i, i, j, false, true)
             for i in xrange(5, 21) for j in xrange(1, 11))

    # Non pair ace containing initial hands
    S.update('{}_{}_{}_{}_{}'.format(i + 1, i + 11, j, false, true)
             for i in xrange(2, 10) for j in xrange(1, 11))

    # Pair containing initial hands
    S.update('{}_{}_{}_{}_{}'.format(2 * i, 2 * i, j, true, true)
             for i in xrange(1, 11) for j in xrange(1, 11))

    # Non pair non ace containing non initial hands
    S.update('{}_{}_{}_{}_{}'.format(i, i, j, false, false)
             for i in xrange(5, 22) for j in xrange(1, 11))

    # Non pair ace containing non initial hands
    S.update('{}_{}_{}_{}_{}'.format(i + 1, i + 11, j, false, false)
             for i in xrange(2, 10) for j in xrange(1, 11))
    return S


def create_hit_table(S, prob):
    dH = dict()

    B = 'TB'
    L = 'TL'
    W = 'TW'
    P = 'TP'

    for state in S:
        if 'T' in state:
            continue

        dH.setdefault(state, set())

        X, Y, D, P, I = map(int, state.split('_'))

        if X == Y:
            dH[state].update({(B, None,
                               None) if (X + i) > 21 or (Y + i) > 21 else
                              ('{}_{}_{}_{}_{}'.format(X + i, Y + i, D, 0, 0),
                               prob if i == 10 else (1 - prob) / 9, None)
                              for i in xrange(2, 11)})
            if (X + 1) > 21:
                dH[state].add((B, None, None))

            elif (Y + 11) > 21:
                dH[state].add(('{}_{}_{}_{}_{}'.format(X + 1, X + 1, D, 0, 0),
                               (1 - prob) / 9, None))

            else:
                dH[state].add(('{}_{}_{}_{}_{}'.format(X + 1, Y + 11, D, 0, 0),
                               (1 - prob) / 9, None))
        else:
            for i in xrange(1, 11):
                if (X + i) > 21:
                    dH[state].add((B, None, None))
                elif (Y + i) > 21:
                    dH[state].add(('{}_{}_{}_{}_{}'.format(
                        X + i, X + i, D, 0, 0), prob if i == 10 else
                                   (1 - prob) / 9, None))
                else:
                    dH[state].add(('{}_{}_{}_{}_{}'.format(
                        X + i, Y + i, D, 0, 0), prob if i == 10 else
                                   (1 - prob) / 9, None))

    return dH


def create_transition_table(S, prob):
    dH = create_hit_table(S, prob)

    pprint(dH)
    raise NotImplementedError


def main():
    states = create_state_space()
    ttable = create_hit_table(states, 4 / 13)
    pprint(ttable)


if __name__ == '__main__':
    main()