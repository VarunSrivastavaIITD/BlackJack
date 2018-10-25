from __future__ import print_function, division
from pprint import pprint

Table = dict()


def signum(a, b):
    if (a > b):
        return 1
    elif (a == b):
        return 0
    else:
        return -1


def dealer_reward(dsum, ace, ten, R, psum, pbj, prob):
    dbj = ace and ten and (dsum == 21)
    assert ((not dbj) or (dsum == 21))

    if (dsum, dbj, psum) in Table:
        return Table[(dsum, dbj, psum)]

    if dsum >= 17:
        sign = 0
        if dsum < 21:
            sign = signum(psum - dsum)
        elif dsum == 21:
            if psum != 21:
                sign = -1
            if psum == 21:
                sign = signum(pbj - dbj)
        else:
            sign = 1
        Table[(dsum, dbj, psum)] = sign * R
        return sign * R
    else:
        val = 0
        for i, p in zip(range(1, 11), [(1 - prob) / 9] * 9 + [prob]):
            if i == 1:
                if not ace:
                    if (dsum + 11) <= 21:
                        val += (1 - p) * dealer_reward(dsum + 11, True, ten, R,
                                                       psum, pbj, prob) / 9
                    else:
                        val += (1 - p) * dealer_reward(dsum + 1, True, ten, R,
                                                       psum, pbj, prob) / 9
                else:
                    val += (1 - p) * dealer_reward(dsum + 1, True, ten, R,
                                                   psum, pbj, prob) / 9
            elif i == 10:
                val += p * dealer_reward(dsum + i, ace, True, R, psum, pbj,
                                         prob)
            else:
                val += (1 - p) * dealer_reward(dsum + i, ace, ten, R, psum,
                                               pbj, prob) / 9

        Table[(dsum, dbj, psum)] = val
        return val


def Qfunction(state, action, prob):

    if action not in {'TS', 'TD'}:
        raise ValueError('Incorrect action {} for Qfunction'.format(action))

    X, Y, D, P, I = map(int, state.split('_'))

    pbj = False
    if X == 11 and Y == 21 and P == False and I == False:
        pbj = True

    if D == 1:
        ace = True
    if D == 10:
        ten = True

    psum = Y
    dsum = 11 if D == 1 else D

    qval = dealer_reward(dsum, ace, ten, 1, psum, pbj, prob)

    if action == 'TD':
        qval *= 2

    return qval


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
             for i in xrange(2, 11) for j in xrange(1, 11))

    # Non pair non ace containing non initial hands
    S.update('{}_{}_{}_{}_{}'.format(i, i, j, false, false)
             for i in xrange(5, 22) for j in xrange(1, 11))

    # Non pair ace containing non initial hands
    S.update('{}_{}_{}_{}_{}'.format(i + 1, i + 11, j, false, false)
             for i in xrange(2, 11) for j in xrange(1, 11))

    # Pair ace containing initial bounds
    S.update(
        '{}_{}_{}_{}_{}'.format(2, 12, j, true, true) for j in xrange(1, 11))

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
    dS = dict()

    for state in S:
        if 'T' in state:
            continue

        dS.setdefault(state, set())

        X, Y, D, P, I = map(int, state.split('_'))

        if P == 1 and I == 1:
            # Santiy check (as such not required)
            e = int(X / 2)
            if (e == 1):
                for i in xrange(1, 11):
                    if e == i:
                        dS[state].add(('{}_{}_{}_{}_{}'.format(
                            e + i, e + 10 + i, D, 1, 1), prob if i == 10 else
                                       (1 - prob) / 9, 0))
                    else:
                        dS[state].add(('{}_{}_{}_{}_{}'.format(
                            e + i, e + 10 + i, D, 0, 1), prob if i == 10 else
                                       (1 - prob) / 9, 0))

            else:
                for i in xrange(1, 11):
                    if i == 1:
                        dS[state].add(('{}_{}_{}_{}_{}'.format(
                            e + i, e + 10 + i, D, 0, 1), prob if i == 10 else
                                       (1 - prob) / 9, 0))
                    else:
                        if e == i:
                            dS[state].add(('{}_{}_{}_{}_{}'.format(
                                e + i, e + i, D, 1, 1), prob if i == 10 else
                                           (1 - prob) / 9, 0))
                        else:
                            dS[state].add(('{}_{}_{}_{}_{}'.format(
                                e + i, e + i, D, 0, 1), prob if i == 10 else
                                           (1 - prob) / 9, 0))

    return dS


def create_double_table(S, prob, hit_table=None):

    if hit_table is False:
        hit_table = create_hit_table(S, prob)

    double_table = {
        k: sum(val[1] * Qfunction(val[0], 'TD', prob) for val in v)
        for k, v in hit_table.items() if 'T' not in k
    }

    return double_table


def create_stand_table(S, prob):
    stand_table = {s: Qfunction(s, 'TS', prob) for s in S if 'T' not in s}
    return stand_table


def create_transition_table(S, prob):
    dH = create_hit_table(S, prob)

    pprint(dH)
    raise NotImplementedError


def value_iteration(S, prob, iterations=100):

    dH = create_hit_table(S, prob)
    dD = create_double_table(S, prob, dH)
    dP = create_split_table(S, prob)
    dS = create_stand_table(S, prob)

    value_table = {s: 0 for s in S}
    policy = {s: None for s in S}

    for _ in xrange(iterations):
        for state in value_table:
            if 'T' in state:
                continue

            X, Y, D, P, I = map(int, state.split('_'))

            maxvalue = -sys.maxint - 1
            maxaction = None

            # Hit action
            if Y < 21:
                hit_neighbors = dH[state]
                Q_state_hit = sum(
                    n[2] + n[1] * value_table[n[0]] for n in hit_neighbors)

            # Split action
            if P:
                split_neighbors = dP[state]
                if X == 2 and Y == 12:
                    Q_state_split = 2 * sum(n[1] * Qfunction(n[0], 'TS', prob)
                                            for n in split_neighbors)
                else:
                    Q_state_split = 2 * sum(n[2] + n[1] * value_table[n[0]]
                                            for n in split_neighbors)

            # Double action
            if I:
                Q_state_double = dD[state]

            # Stand action
            Q_state_stand = dS[state]

            if (maxvalue < Q_state_hit):
                maxvalue = Q_state_hit
                maxaction = 'H'
            if (maxvalue < Q_state_split):
                maxvalue = Q_state_split
                maxaction = 'P'
            if (maxvalue < Q_state_stand):
                maxvalue = Q_state_stand
                maxaction = 'S'
            if (maxvalue < Q_state_double):
                maxvalue = Q_state_double
                maxaction = 'D'

            value_table[state] = maxvalue
            policy[state] = maxaction

    return value_table, policy


def main():
    states = create_state_space()
    ttable = create_hit_table(states, 4 / 13)
    pprint(ttable)


if __name__ == '__main__':
    main()
