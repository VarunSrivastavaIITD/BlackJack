import random

def expected_dealer(sum, p):

    #since the hand must be soft
    for x in range(2, 12):
        if(sum + x <= 17):
            if(x == 10):
                sum = sum + (p * expected_dealer( sum+x, p))
            else:
                sum = sum + (((1-p)/9)*expected_dealer(sum+x, p))

    return sum


p = 4/13
sum = 1
ans = expected_dealer(sum, p)
print(ans)
