from ortools.sat.python import cp_model 
from time import time
import sys

def get_data():
    N, M = 0, 0
    t, g, s, c = [0], [0], [0], [0]

    counting = 1
    for line in sys.stdin:
        temp = line.rstrip()
        try:
            if counting == 1:
                N, M = tuple([int(x) for x in line.split()])

            elif 2 <= counting and counting <= N+1:
                tmp_t, tmp_g, tmp_s =  tuple([int(x) for x in line.split()])
                t.append(tmp_t)
                g.append(tmp_g)
                s.append(tmp_s)

            elif counting == N+2:
                c.extend([int(x) for x in line.split()])
                if len(c) != M+1:
                    raise Exception()
                break

        except:
            raise Exception('Error while reading input!')

        counting += 1

    return N,M,t,g,s,c

def cp_approach():
    model = cp_model.CpModel()
    n_class,n_room,t,g,s,c = get_data()
    sp = {} # Start period: Lưu tiết học bắt đầu của từng lớp
    r = {} # room: Lưu lại phòng học được xếp cho các lớp
    before = {} # true nếu sp[i] < sp[j]
    
    check_sp = {}
    for i in range(1,n_class+1):
        sp[i] = model.NewIntVar(0, 60, f"sp_{i}")
        for j in range(1, n_room+1):
            r[i,j] = model.NewBoolVar(f"r_{i}_{j}")
        check_sp[i] = model.NewBoolVar(f"sp_{i}_is_zero")
        for j in range(i+1, n_class+1):
            before[i,j] = model.NewBoolVar(f"{i}_before_{j}")

    # Constraint:
    
    # Ràng buộc về các lớp có chung giáo viên
    for i in range(1, n_class+1):
        for j in range(i+1, n_class+1):
            if g[i] == g[j] and i != j:
                # check_i_j = model.NewBoolVar(f"{i}_before_{j}")
                model.Add(sp[j] != 0).OnlyEnforceIf(check_sp[j].Not())
                model.Add(sp[i] != 0).OnlyEnforceIf(check_sp[i].Not())
                model.Add(sp[i] - sp[j] >= t[j]).OnlyEnforceIf([before[i,j].Not(), check_sp[j].Not()])
                model.Add(sp[j] - sp[i] >= t[i]).OnlyEnforceIf([before[i,j], check_sp[i].Not()])
    
    # Ràng buộc về sĩ số lớp vs sức chứa của phòng học (Nếu lớp được xếp phòng)    
    for i in range(1, n_class + 1):
        for j in range(1, n_room+1):
            model.Add(s[i] <= c[j]).OnlyEnforceIf(r[i,j])
    
    # Ràng buộc 1 lớp nếu được xếp thì chỉ được ở 1 phòng, nếu ko thì k đc xếp phòng    
    for i in range(1,n_class+1):
        model.Add(sum(r[i,j] for j in range(1,n_room+1)) == 1).OnlyEnforceIf(check_sp[i].Not())
        model.Add(sum(r[i,j] for j in range(1,n_room+1)) == 0).OnlyEnforceIf(check_sp[i])
    
    # Ràng buộc 1 phòng tại 1 thời điểm chỉ được dạy 1 lớp
    for i in range(1, n_class+1):
        for j in range(i+1, n_class+1):
            model.Add(sp[i] < sp[j]).OnlyEnforceIf(before[i,j])
            model.Add(sp[i] >= sp[j]).OnlyEnforceIf(before[i,j].Not())
            for k in range(1, n_room+1):
                i_j_k = model.NewBoolVar(f'class_{i}_{j}_same_room_{k}')
                model.Add(r[i,k] == 1).OnlyEnforceIf(i_j_k)
                model.Add(r[j,k] == 1).OnlyEnforceIf(i_j_k)
                model.Add(r[i,k] + r[j,k] <= 1).OnlyEnforceIf(i_j_k.Not())
                model.Add(sp[i] >= sp[j] + t[j]).OnlyEnforceIf([before[i,j].Not(), i_j_k])
                model.Add(sp[j] >= sp[i] + t[i]).OnlyEnforceIf([before[i,j], i_j_k])
                
                
    
    # Ràng buộc 1 môn chỉ học trong 1 buổi 
    DC = [6*i for i in range(11)] 
    for i in range(1, n_class+1):
        check_period ={}
        for j in range(len(DC) - 1):
            check_period[j] = model.NewBoolVar(f"check_period_{j}")
        model.Add(sum(check_period[j] for j in range(len(DC) - 1)) == 1)
        for j in range(len(DC) - 1):
            model.Add(sp[i] > DC[j]).OnlyEnforceIf(check_period[j])
            model.Add(sp[i] + t[i] - 1 <= DC[j+1]).OnlyEnforceIf(check_period[j])
            
    model.Minimize(sum(sp[i] for i in range(1, n_class+1)))
    model.Minimize(sum(check_sp[i] for i in range(1, n_class+1)))
    
    # Cài solver
    solver = cp_model.CpSolver()
    time1 = time()
    status = solver.Solve(model)
    time2 = time()
    if status == cp_model.OPTIMAL:
        print('{}'.format(n_class - int(solver.ObjectiveValue())))
        for i in range(1, n_class+1):
            if solver.Value(check_sp[i]) == 0:
                for j in range(1, n_room+1):
                    if solver.Value(r[i,j]) == 1:
                        print(f"{i} {solver.Value(sp[i])} {j}")
        for i in range(1, n_class+1):
            for j in range(1, n_room+1):
                # print(solver.Value(r[i,j]), end=' ')
                pass
            # print()
    else: print('No solution found. ')

if __name__ == '__main__':
    cp_approach()