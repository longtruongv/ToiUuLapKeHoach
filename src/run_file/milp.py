import sys

MAX_VALUE = 99999999
NEAR_ZERO = 0.01

N, M = 0, 0
t, g, s, c = [], [], [], []

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
            c = [int(x) for x in line.split()]
            if len(c) != M:
                raise Exception()
            break

    except:
        # print('Error while reading input!')
        raise Exception('Error while reading input!')

    counting += 1

from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver('SAT')#('SCIP')

#########################
## VARIABLES & DOMAINS ##
#########################

class_is_chosen = [] # Lớp có được xếp hay không
# class_half_day = [] # Buổi học
class_starting = [] # Tiết học bắt đầu (trong buổi)
class_room = [] # Phòng học
class_room_onehot = [] # Phòng học dạng vector one-hot

for i in range(N):
    class_is_chosen.append(solver.BoolVar(f'class_is_chosen[{i}]'))
    # class_half_day.append(solver.IntVar(0, 9, f'class_half_day[{i}]'))
    class_starting.append(solver.IntVar(0, 59, f'class_starting[{i}]'))

    class_room.append(solver.IntVar(-1, M-1, f'class_room[{i}]'))
    class_room_onehot.append([
        solver.BoolVar(name=f'class_room_onehot[{i},{j}]')
        for j in range(M)
    ])

###################
## CONSTRAINTS 1 ##
###################

for i in range(N):
    ## CONSTRAINT ##
    # Mỗi lớp được xếp sẽ chiếm 1 phòng duy nhất
    solver.Add(
        sum(class_room_onehot[i]) == class_is_chosen[i]
    )

    ## CONSTRAINT ##
    # Đồng bộ giữa biến phòng học dạng số và dạng vector one-hot
    solver.Add(
        sum([j * class_room_onehot[i][j] for j in range(M)]) - (1 - class_is_chosen[i]) == class_room[i]
    )

    ## CONSTRAINT ##
    # Mỗi lớp được xếp có kích thước phòng chứa đủ sĩ số lớp 
    solver.Add(
        sum(c[j] * class_room_onehot[i][j] for j in range(M)) >= class_is_chosen[i] * s[i]
    )

    ## CONSTRAINT ##
    # Lớp học giới hạn trong một buổi
    half_day = solver.IntVar(0, 9, f'half_day[{i}]')
    solver.Add(class_starting[i] >= half_day*6)
    solver.Add(class_starting[i] + NEAR_ZERO <= (half_day + 1)*6)
    solver.Add((class_starting[i] + t[i]) >= half_day*6 + NEAR_ZERO)
    solver.Add((class_starting[i] + t[i]) + NEAR_ZERO <= (half_day + 1)*6)


###################
## CONSTRAINTS 2 ##
###################
for i in range(N):
    for j in range(N):
        if i == j:
            continue


        # Biến is_i_not_overlap_j: lớp i không bị chồng giờ với lớp j hay không (coi như chung một buổi), D = {0, 1}
        # Biến thể Công thức Bằng
        is_i_not_overlap_j = solver.BoolVar(f'is_i_not_overlap_j[{i},{j}]')
        is_i_before_j = solver.BoolVar(f'is_i_before_j[{i},{j}]')
        is_i_after_j = solver.BoolVar(f'is_i_after_j[{i},{j}]')
        solver.Add((is_i_before_j - 1) * MAX_VALUE <= class_starting[j] - class_starting[i] - t[i])
        solver.Add(class_starting[j] - class_starting[i] - t[i] <= MAX_VALUE * is_i_before_j - 1)
        solver.Add((is_i_after_j - 1) * MAX_VALUE <= class_starting[i] - class_starting[j] - t[j])
        solver.Add(class_starting[i] - class_starting[j] - t[j] <= MAX_VALUE * is_i_after_j - 1)
        solver.Add(is_i_not_overlap_j >= is_i_before_j)
        solver.Add(is_i_not_overlap_j >= is_i_after_j)
        solver.Add(is_i_not_overlap_j <= is_i_before_j + is_i_after_j)


        # Biến is_i_and_j_chosen: Cả lớp i và lớp j cùng được xếp hay không, D = {0, 1}
        # Công thức AND
        is_i_and_j_chosen = solver.BoolVar(f'is_i_and_j_chosen[{i},{j}]')
        solver.Add(is_i_and_j_chosen <= class_is_chosen[i])
        solver.Add(is_i_and_j_chosen <= class_is_chosen[j])
        solver.Add(is_i_and_j_chosen >= class_is_chosen[i] + class_is_chosen[j] - 1)

        # Biến is_i_same_room_j: Nếu lớp i và lớp j chung phòng
        # Công thức Bằng
        is_i_same_room_j = solver.BoolVar(f'is_i_same_room_j[{i},{j}]')
        is_i_room_idx_before_j = solver.BoolVar(f'is_i_room_idx_before_j[{i},{j}]')
        is_i_room_idx_after_j = solver.BoolVar(f'is_i_room_idx_after_j[{i},{j}]')
        solver.Add((is_i_room_idx_before_j - 1) * MAX_VALUE <= class_room[j] - class_room[i] - 1)
        solver.Add(class_room[j] - class_room[i] - 1 <= is_i_room_idx_before_j * MAX_VALUE - 1)
        solver.Add((is_i_room_idx_after_j - 1) * MAX_VALUE <= class_room[i] - class_room[j] - 1)
        solver.Add(class_room[i] - class_room[j] - 1 <= is_i_room_idx_after_j * MAX_VALUE - 1)
        solver.Add(1 - is_i_same_room_j >= is_i_room_idx_before_j)
        solver.Add(1 - is_i_same_room_j >= is_i_room_idx_after_j)
        solver.Add(1 - is_i_same_room_j <= is_i_room_idx_before_j + is_i_room_idx_after_j)

        # Biến is_i_same_room_j_and_chosen: Nếu lớp i và lớp j cùng được xếp và xếp chung phòng
        # is_i_same_room_j_and_chosen = is_i_same_room_j AND is_i_and_j_chosen (Công thức AND)
        is_i_same_room_j_and_chosen = solver.BoolVar(f'is_i_same_room_j_and_chosen[{i},{j}]')
        solver.Add(is_i_same_room_j_and_chosen <= is_i_same_room_j)
        solver.Add(is_i_same_room_j_and_chosen <= is_i_and_j_chosen)
        solver.Add(is_i_same_room_j_and_chosen >= is_i_same_room_j + is_i_and_j_chosen - 1)


        ## CONSTRAINT ##
        # Nếu lớp được xếp và chung giáo viên, các lớp không được xếp chồng giờ nhau
        if g[i] == g[j]:
            solver.Add(is_i_not_overlap_j >= is_i_and_j_chosen)
        

        ## CONSTRAINT ##
        # Nếu lớp được xếp và xếp chung phòng, các lớp không được xếp chồng giờ nhau
        solver.Add(is_i_not_overlap_j >= is_i_same_room_j_and_chosen)


################
## OBJECTIVES ##
################

# Tối đa số lượng lớp được chọn
solver.Maximize(sum(class_is_chosen))


status = solver.Solve()
solution = {}

if status == pywraplp.Solver.OPTIMAL:
    for idx, val in enumerate(class_is_chosen):
        if val.solution_value():
            solution[idx + 1] = {
                'starting': int(
                    class_starting[idx].solution_value() + 1
                ),
                'room': int(class_room[idx].solution_value() + 1),
            }
            
# else:
#     print('No solution found.')


print(len(solution))
for i in solution:
    starting = solution[i]['starting']
    room = solution[i]['room']
    print(f'{i} {starting} {room}')