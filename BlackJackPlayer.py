from __future__ import print_function, division
from pprint import pprint
import sys
from random import random, uniform
from operator import itemgetter

Table = dict()


def signum(a, b=0):
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
                sign = 1.5 * signum(pbj - dbj)
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
                        val += (p) * dealer_reward(dsum + 11, True, ten, R,
                                                   psum, pbj, prob)
                    else:
                        val += (p) * dealer_reward(dsum + 1, True, ten, R,
                                                   psum, pbj, prob)
                else:
                    val += p * dealer_reward(dsum + 1, True, ten, R, psum, pbj,
                                             prob)
            elif i == 10:
                val += p * dealer_reward(dsum + i, ace, True, R, psum, pbj,
                                         prob)
            else:
                val += p * dealer_reward(dsum + i, ace, ten, R, psum, pbj,
                                         prob)

        Table[(dsum, dbj, psum)] = val
        return val


def Qfunction(state, action, prob):

    if state == 'TB':
        if action == 'TD':
            return -2
        return -1

    if action not in {'TS', 'TD'}:
        raise ValueError('Incorrect action {} for Qfunction'.format(action))

    X, Y, D, P, I = map(int, state.split('_'))

    pbj = False
    if X == 11 and Y == 21 and P == 0:
        pbj = True

    ace = True if D == 1 else False
    ten = True if D == 10 else False

    psum = Y
    assert (Y < 22)
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
             for i in xrange(2, 11) for j in xrange(1, 11))

    # Pair containing initial hands
    S.update('{}_{}_{}_{}_{}'.format(2 * i, 2 * i, j, true, true)
             for i in xrange(2, 11) for j in xrange(1, 11))

    # Non pair non ace containing non initial hands
    S.update('{}_{}_{}_{}_{}'.format(i, i, j, false, false)
             for i in xrange(3, 22) for j in xrange(1, 11))

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

    value_table = {s: 0 if 'T' in s else uniform(-2, 2) for s in S}
    new_value_table = value_table
    policy = {s: None for s in S}
    prevmax = 0
    for _ in xrange(iterations):
        for state in value_table:
            if 'T' in state:
                continue

            X, Y, D, P, I = map(int, state.split('_'))

            maxvalue = -sys.maxint - 1
            maxaction = None

            # Hit action
            Q_state_hit = -sys.maxint - 1
            if Y < 21:
                hit_neighbors = dH[state]
                Q_state_hit = sum(
                    (n[1] * (value_table[n[0]] + n[2])) for n in hit_neighbors)

            # Split action
            Q_state_split = -sys.maxint - 1
            if P:
                split_neighbors = dP[state]
                if X == 2 and Y == 12:
                    Q_state_split = 2 * sum(n[1] * Qfunction(n[0], 'TS', prob)
                                            for n in split_neighbors)
                else:
                    Q_state_split = 2 * sum(n[2] + n[1] * value_table[n[0]]
                                            for n in split_neighbors)

            # Double action
            Q_state_double = -sys.maxint - 1
            if I:
                Q_state_double = dD[state]

            # Stand action
            Q_state_stand = dS[state]

            if (maxvalue < Q_state_stand):
                maxvalue = Q_state_stand
                maxaction = 'S'
            # if _ == iterations - 1:
            if (maxvalue < Q_state_split):
                maxvalue = Q_state_split
                maxaction = 'P'
            if (maxvalue < Q_state_double):
                maxvalue = Q_state_double
                maxaction = 'D'
            if (maxvalue < Q_state_hit):
                maxvalue = Q_state_hit
                maxaction = 'H'

            new_value_table[state] = maxvalue
            policy[state] = maxaction

        value_table = new_value_table
        maxv = max(value_table.values())
        res = maxv - prevmax
        # print('Residual @ iteration {}: {} '.format(_, res))
        # print('Minimum Value: {}'.format(min(value_table.values())))
        # print('Sum: {}'.format(sum(value_table.values())))
        prevmax = maxv

    return value_table, policy


def print_policy(policy):
    hard_actions = []
    soft_actions = []
    pairs = []

    for s, a in policy.items():
        if 'T' in s:
            continue
        X, Y, D, P, I = map(int, s.split('_'))

        if (X == Y) and P == 0 and I == 1 and X < 20:
            hard_actions.append((X, a, 11 if D == 1 else D))

        if (X != Y) and P == 0 and I == 1 and X < 11:
            soft_actions.append(('A{}'.format(X - 1), a, 11 if D == 1 else D))

        if P == 1 and I == 1:
            pairs.append(
                ('AA' if X == 2 and Y == 12 else '{0}{0}'.format(int(X / 2)),
                 a, 11 if D == 1 else D))

    hard_actions.sort(key=itemgetter(0, 2))

    with open('Policy.txt', 'w') as f:
        for i in xrange(0, len(hard_actions), 10):
            print(
                str(hard_actions[i][0]),
                ' '.join([str(h[1]) for h in hard_actions[i:i + 10]]),
                sep='\t',
                file=f)

        soft_actions.sort(key=itemgetter(0, 2))
        for i in xrange(0, len(soft_actions), 10):
            print(
                str(soft_actions[i][0]),
                ' '.join([str(h[1]) for h in soft_actions[i:i + 10]]),
                sep='\t',
                file=f)

        pairs.sort(key=itemgetter(0, 2))
        for i in xrange(10, len(pairs) - 10, 10):
            print(
                str(pairs[i][0]),
                ' '.join([str(h[1]) for h in pairs[i:i + 10]]),
                sep='\t',
                file=f)
        print(
            str(pairs[0][0]),
            ' '.join([str(h[1]) for h in pairs[0:0 + 10]]),
            sep='\t',
            file=f)
        print(
            str(pairs[len(pairs) - 10][0]),
            ' '.join([str(h[1]) for h in pairs[len(pairs) - 10:len(pairs)]]),
            sep='\t',
            file=f,
            end='')


def main():
    prob = float(sys.argv[1])
    # prob = 4 / 13
    S = create_state_space()
    print(len(S))
    _, policy = value_iteration(S, prob, 100)
    print(len(policy))
    print_policy(policy)


if __name__ == '__main__':
    main()
