import sys

N = 0
M = 0
t, g, s, c = [], [], [], []

######################
## BEGIN Constraint ##
######################

def sp_constraint(sp, r, k=N):
    global N, M, t, g, s, c

    for i in range(k):
        if sp[i] == -1:
            continue
        DC = int(sp[i] / 6) * 6
        if sp[i] + t[i] > DC + 6:
            return False

    for i in range(k):
        if sp[i] == -1:
            continue
        for j in range(i+1, k):
            if sp[j] == -1:
                continue
            if g[i] == g[j]:
                start1 = sp[i]
                end1 = sp[i] + t[i]
                start2 = sp[j]
                end2 = sp[j] + t[j]

                if (start1 <= end2) and (end1 >= start2):
                    return False
            
    return True

def r_constraint(sp, r, k=N):
    global N, M, t, g, s, c

    for i in range(k):
        if r[i] == -1:
            continue
        if s[i] > c[r[i]]:
            return False
        
    for i in range(k):
        if r[i] == -1:
            continue
        for j in range(i+1, k):
            if r[j] == -1:
                continue
            if r[i] == r[j]:
                start1 = sp[i]
                end1 = sp[i] + t[i]
                start2 = sp[j]
                end2 = sp[j] + t[j]

                if (start1 <= end2) and (end1 >= start2):
                    return False

    return True

def sp_r_constraint(sp, r, k=N):
    global N, M, t, g, s, c

    for i in range(k):
        if (sp[i] == -1) != (r[i] == -1):
            return False
    
    if not sp_constraint(sp, r, k):
        return False
    if not r_constraint(sp, r, k):
        return False
    
    return True

####################
## END Constraint ##
####################

#######################
## BEGIN Brute Force ##
#######################

MAX = -99999999
SP = []
R = []

def TRY(k, sp_candidates: set, r_candidates: set):
    global N, M, t, g, s, c, sp, r, MAX, SP, R
    if k == N:
        if sp_r_constraint(sp, r, k):
            # eval result
            temp = sum(map(lambda x: x>=0, sp))
            if temp > MAX:
                MAX = temp
                SP = sp.copy()
                R = r.copy()
            
        return
    
    for sp_candidate in sp_candidates:
        sp[k] = sp_candidate

        if sum(map(lambda x: x>=0, sp[0:k+1])) + N - k - 1 <= MAX + 1:
            continue

        for r_candidate in r_candidates:
            r[k] = r_candidate
            if sp_r_constraint(sp, r, k):
                TRY(k+1, sp_candidates, r_candidates)
            r[k] = -1
        sp[k] = -1

#####################
## END Brute Force ##
#####################

if __name__ == "__main__":
    counting = 1
    for line in sys.stdin:
        line = line.rstrip()
        try:
            if counting == 1:
                N, M = tuple([int(x) for x in line.split()])

            elif 2 <= counting and counting <= N+1:
                tmp_t, tmp_g, tmp_s =  tuple([int(x) for x in line.split()])
                t.append(tmp_t)
                g.append(tmp_g)
                s.append(tmp_s)

            elif counting == N+2:
                c = [int(x) for x in line.split()]
                if len(c) != M:
                    raise Exception()
                break

        except:
            # print('Error while reading input!')
            raise Exception('Error while reading input!')

        counting += 1

    sp = [-1] * N # value = {-1} or {0, ..., 59}
    r = [-1] * N # value = {-1} or {0, ..., M-1}

    sp_candidates = set(range(-1, 60))
    r_candidates = set(range(-1, M))
    try:
        TRY(0, sp_candidates, r_candidates)
    finally:
        print(MAX)
        for i in range(N):
            tiet_bat_dau = SP[i]
            phong = R[i]
            thoi_luong = t[i]
            # gv = g[i]
            # si_so = s[i]
            # max_si_so = c[R[i]]

            if tiet_bat_dau != -1:
                # print(f"id:{i}\t tbd:{tiet_bat_dau}\t tl:{thoi_luong}\t gv:{gv}\t p:{phong}\t ss:{si_so}\t mss:{max_si_so}")
                print(f"{i+1} {tiet_bat_dau+1} {phong+1}")

