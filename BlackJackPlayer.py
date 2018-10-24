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
             for i in xrange(2, 11) for j in xrange(1, 11))
    return S


def create_hit_table(S, prob):
    def update_bust(hit_dict, state, bust, p):

        bust_elements = filter(lambda s: s[0] == bust, hit_dict[state])
        if len(bust_elements) != 0:
            assert (len(bust_elements) == 1)
            bust_elem = bust_elements[0]
            hit_dict[state].remove(bust_elem)
            hit_dict[state].add((bust, bust_elem[1] + p, bust_elem[2]))
        else:
            hit_dict[state].add((bust, p, -1))

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
            for i in xrange(2, 11):
                if (X + i) > 21 or (Y + i) > 21:
                    update_bust(dH, state, B,
                                (1 - prob) / 9 if i != 10 else prob)
                else:
                    dH[state].add(('{}_{}_{}_{}_{}'.format(
                        X + i, Y + i, D, 0, 0), prob if i == 10 else
                                   (1 - prob) / 9, 0))

            if (X + 1) > 21:
                update_bust(dH, state, B, (1 - prob) / 9)

            elif (Y + 11) > 21:
                dH[state].add(('{}_{}_{}_{}_{}'.format(X + 1, X + 1, D, 0, 0),
                               (1 - prob) / 9, 0))

            else:
                dH[state].add(('{}_{}_{}_{}_{}'.format(X + 1, Y + 11, D, 0, 0),
                               (1 - prob) / 9, 0))
        else:
            for i in xrange(1, 11):
                if (X + i) > 21:
                    update_bust(dH, state, B,
                                (1 - prob) / 9 if i != 10 else prob)
                elif (Y + i) > 21:
                    dH[state].add(('{}_{}_{}_{}_{}'.format(
                        X + i, X + i, D, 0, 0), prob if i == 10 else
                                   (1 - prob) / 9, 0))
                else:
                    dH[state].add(('{}_{}_{}_{}_{}'.format(
                        X + i, Y + i, D, 0, 0), prob if i == 10 else
                                   (1 - prob) / 9, 0))

    return dH


def create_split_table(S, prob):
    dH = dict()

    for state in S:
        if 'T' in state:
            continue

        dH.setdefault(state, set())

        X, Y, D, P, I = map(int, state.split('_'))

        if P == 1 and I == 1:
            # Santiy check (as such not required)
            assert (X == Y)
            e = int(X / 2)
            if (e == 1):
                for i in xrange(1, 11):
                    if e == i:
                        dH[state].add(('{}_{}_{}_{}_{}'.format(
                            e + i, e + 10 + i, D, 1, 1), prob if i == 10 else
                                       (1 - prob) / 9, None))
                    else:
                        dH[state].add(('{}_{}_{}_{}_{}'.format(
                            e + i, e + 10 + i, D, 0, 1), prob if i == 10 else
                                       (1 - prob) / 9, None))

            else:
                for i in xrange(1, 11):
                    if i == 1:
                        dH[state].add(('{}_{}_{}_{}_{}'.format(
                            e + i, e + 10 + i, D, 0, 1), prob if i == 10 else
                                       (1 - prob) / 9, None))
                    else:
                        if e == i:
                            dH[state].add(('{}_{}_{}_{}_{}'.format(
                                e + i, e + i, D, 1, 1), prob if i == 10 else
                                           (1 - prob) / 9, None))
                        else:
                            dH[state].add(('{}_{}_{}_{}_{}'.format(
                                e + i, e + i, D, 0, 1), prob if i == 10 else
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
