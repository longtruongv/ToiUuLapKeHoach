import sys

MAX_VALUE = 99999999
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
        raise Exception('Error while reading input!')

    counting += 1


from ortools.sat.python import cp_model
model = cp_model.CpModel()

# VARIABLES & DOMAINS
class_is_chosen = [] # Lớp có được xếp hay không, 1 nếu được xếp, 0 nếu bỏ
class_half_day = [] # Buổi học, D = {0, ..., 9} 
class_starting = [] # Tiết học bắt đầu (trong buổi), D = {0, ..., 5}
class_room = [] # Phòng học, D = {0, ..., M-1}

for i in range(N):
    class_is_chosen.append(model.NewBoolVar(f'class_is_chosen[{i}]'))
    class_half_day.append(model.NewIntVar(0, 9, f'class_half_day[{i}]'))
    class_starting.append(model.NewIntVar(0, 5, f'class_starting[{i}]'))
    class_room.append(model.NewIntVar(0, M-1, f'clas_room[{i}]'))


# CONSTRAINTS

for i in range(N):
    # Sĩ số lớp được chọn ít hơn kích thước phòng
    temp_c = model.NewIntVar(0, MAX_VALUE, f'temp_c[{i}]')
    model.AddElement(class_room[i], c, temp_c)
    model.Add(
        temp_c >= s[i]
    ).OnlyEnforceIf(class_is_chosen[i])

    # Lớp học giới hạn trong một buổi
    model.Add(
        class_starting[i] + t[i] <= 6
    ).OnlyEnforceIf(class_is_chosen[i])

for i in range(N):
    for j in range(N):
        if i == j:
            continue

        # Biến: hai lớp có chồng giờ không
        i_same_session_j = model.NewBoolVar(f'i_same_session_j[{i},{j}]')
        model.Add(class_half_day[i] == class_half_day[j]).OnlyEnforceIf(i_same_session_j)
        model.Add(class_half_day[i] != class_half_day[j]).OnlyEnforceIf(i_same_session_j.Not())

        i_start_before_j = model.NewBoolVar(f'i_start_before_j[{i},{j}]')
        model.Add(class_starting[i] <= class_starting[j]).OnlyEnforceIf(i_start_before_j)
        model.Add(class_starting[i] > class_starting[j]).OnlyEnforceIf(i_start_before_j.Not())

        i_end_after_j_start = model.NewBoolVar(f'i_end_after_j_start[{i},{j}]')
        model.Add(class_starting[i] + t[i] - 1 >= class_starting[j]).OnlyEnforceIf(i_end_after_j_start)
        model.Add(class_starting[i] + t[i] - 1 < class_starting[j]).OnlyEnforceIf(i_end_after_j_start.Not())

        overlap_requirements = sum([i_same_session_j, i_start_before_j, i_end_after_j_start])
        
        temp_overlap_1 = model.NewBoolVar(f'temp_overlap_1[{i},{j}]')
        model.AddBoolAnd([i_start_before_j, i_end_after_j_start]).OnlyEnforceIf(temp_overlap_1)
        model.AddBoolOr([i_start_before_j.Not(), i_end_after_j_start.Not()]).OnlyEnforceIf(temp_overlap_1.Not())

        i_overlapped_by_j = model.NewBoolVar(f'i_overlapped_by_j[{i},{j}]')
        model.AddBoolAnd([i_same_session_j, temp_overlap_1]).OnlyEnforceIf(i_overlapped_by_j)
        model.AddBoolOr([i_same_session_j.Not(), temp_overlap_1.Not()]).OnlyEnforceIf(i_overlapped_by_j.Not())


        # Hai lớp cùng giáo viên không chồng lên nhau
        if g[i] == g[j]:
            model.Add(
                i_overlapped_by_j == 0
            ).OnlyEnforceIf(
                class_is_chosen[i] 
            ).OnlyEnforceIf(
                class_is_chosen[j]
            )

        # Hai lớp xếp chồng giờ không cùng phòng
        i_same_room_j = model.NewBoolVar(f'i_same_room_j[{i},{j}]')
        model.Add(class_room[i] == class_room[j]).OnlyEnforceIf(i_same_room_j)
        model.Add(class_room[i] != class_room[j]).OnlyEnforceIf(i_same_room_j.Not())

        model.Add(
            i_overlapped_by_j == 0
        ).OnlyEnforceIf(
            class_is_chosen[i] 
        ).OnlyEnforceIf(
            class_is_chosen[j]
        ).OnlyEnforceIf(
            i_same_room_j
        )


# OBJECTIVES
model.Maximize(
    sum(class_is_chosen)
)

solver = cp_model.CpSolver()
status = solver.Solve(model)

solution = {}

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    for idx, c in enumerate(class_is_chosen):
        if solver.Value(c):
            solution[idx + 1] = {
                'starting': (
                    solver.Value(class_half_day[idx]) * 6 + solver.Value(class_starting[idx]) + 1
                ),
                'room': solver.Value(class_room[idx]) + 1,
            }
            
else:
    print('No solution found.')


print(len(solution))
for i in solution:
    starting = solution[i]['starting']
    room = solution[i]['room']
    print(f'{i} {starting} {room}')