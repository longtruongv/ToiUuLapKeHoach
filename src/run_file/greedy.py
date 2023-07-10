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
        # print('Error while reading input!')
        raise Exception('Error while reading input!')

    counting += 1

STARTING_OPTIONS = [i for i in range(60)]
ROOM_OPTIONS = [i for i in range(M)]


curr_solution = {}
curr_candidates = set()
assigned_g = {}
assigned_c = {}

def init():
    global curr_solution, curr_candidates, assigned_g, assigned_c

    curr_solution = {} # {class_id: (starting, room)}
    curr_candidates = set([i for i in range(N)])

    assigned_g = {
        i: { # teacher_id
            'num_assigned': 0, # số lần được xếp
            'periods': [0 for _ in range(60)], # vector tiết được xếp (1 được xếp, 0 chưa)
        } for i in set(g)
    }

    assigned_c = {
        i: { # room_id
            'num_assigned': 0, # số lần được xếp
            'periods': [0 for _ in range(60)], # vector tiết được xếp (1 được xếp, 0 chưa)
        } for i in range(len(c))
    }


# Các hàm chọn candidate cho lớp và phòng học


def creat_feature_dict(candidates_list, features_list):
    if len(candidates_list) != len(features_list):
        return {}
    
    return {
        candidates_list[i]: features_list[i]
        for i in range(len(candidates_list))
    }

def get_priority_from_features(features_dict, is_get_min=True): 
    # features_dict = dict{candidate: feature}
    features_set = list(set([features_dict[cand] for cand in features_dict]))
    features_set.sort(reverse=is_get_min)
    
    output = {} # {candidate: priority}
    for cand in features_dict:
        feat = features_dict[cand]
        output[cand] = features_set.index(feat)
    
    return output

def argmax(iterable):
    return max(enumerate(iterable), key=lambda x: x[1])[0]

def get_best_candidate(*priorities):
    candidates = list(priorities[0].keys())
    sum_priority = []

    for cand in candidates:
        sum_priority.append(sum([
            priority[cand] 
            if cand in priority
            else -MAX_VALUE
            for priority in priorities 
        ]))

    best_cand_idx = argmax(sum_priority)
    if sum_priority[best_cand_idx] < 0:
        return None
    return candidates[best_cand_idx]


# Các hàm chọn giờ 

def get_valid_startings(class_id):
    global N, M, t, g, s, c
    
    num_periods = t[class_id]
    valid_startings = set()
    
    for i in range(10): # 10 buổi
        temp = [(i * 6 + j) for j in range(6 - num_periods + 1)]
        valid_startings.update(temp)
    
    return valid_startings

def get_startings_with_teacher(class_id):
    global N, M, t, g, s, c, assigned_g

    teacher_id = g[class_id]
    num_periods = t[class_id]
    periods = assigned_g[teacher_id]['periods']

    feasible_startings = set()

    i = 0
    while i < len(periods):
        if periods[i] == 1:
            i += 1
            continue

        first_zero = i
        counting = 0
        while i < len(periods) and periods[i] == 0:
            counting += 1
            i += 1

        feasible_startings.update([
            first_zero + j 
            for j in range(counting - num_periods + 1)
        ])

    return feasible_startings
    

def get_startings_with_room(class_id, room_id):
    global N, M, t, g, s, c, assigned_c

    num_periods = t[class_id]
    periods = assigned_c[room_id]['periods']

    feasible_startings = set()

    i = 0
    while i < len(periods):
        if periods[i] == 1:
            i += 1
            continue

        first_zero = i
        counting = 0
        while i < len(periods) and periods[i] == 0:
            counting += 1
            i += 1

        feasible_startings.update([
            first_zero + j 
            for j in range(counting - num_periods + 1)
        ])

    return feasible_startings

init()
while curr_candidates:
    # Chọn lớp
    class_candidates = list(curr_candidates)

    class_teacher_num_assigned = creat_feature_dict(
        class_candidates,
        [assigned_g[g[cand]]['num_assigned'] for cand in class_candidates]
    )
    class_teacher_num_assigned_priority = get_priority_from_features(class_teacher_num_assigned)

    class_teacher_sum_periods = creat_feature_dict(
        class_candidates,
        [sum(assigned_g[g[cand]]['periods']) for cand in class_candidates]
    )
    class_teacher_sum_periods_priority = get_priority_from_features(class_teacher_sum_periods)

    class_num_periods = creat_feature_dict(
        class_candidates,
        [t[cand] for cand in class_candidates]
    )
    class_num_periods_priority = get_priority_from_features(class_num_periods)

    class_num_pupils = creat_feature_dict(
        class_candidates,
        [s[cand] for cand in class_candidates]
    )
    class_num_pupils_priority = get_priority_from_features(class_num_pupils)

    curr_class = get_best_candidate(
        class_teacher_num_assigned_priority,
        class_teacher_sum_periods_priority,
        class_num_periods_priority,
        class_num_pupils_priority,
    )

    # print('class:', curr_class)
    if curr_class is None:
        raise Exception('Candidate None!')

    curr_candidates.remove(curr_class)

    # Chọn phòng
    room_candidates = [idx for idx, size in enumerate(c)]

    room_size = dict(filter(
        lambda x: x[1] >= s[curr_class], 
        enumerate(c)
    ))
    if not room_size:
        # print('No room valid!')
        continue
    room_size_priority = get_priority_from_features(room_size)

    room_num_assigned = creat_feature_dict(
        room_candidates,
        [assigned_c[cand]['num_assigned'] for cand in room_candidates]
    )
    room_num_assigned_priority = get_priority_from_features(room_num_assigned)
    
    room_sum_periods = creat_feature_dict(
        room_candidates,
        [sum(assigned_c[cand]['periods']) for cand in room_candidates]
    )
    room_sum_periods_priority = get_priority_from_features(room_sum_periods)
    
    curr_room = get_best_candidate(
        room_size_priority,
        room_num_assigned_priority,
        room_sum_periods_priority
    )

    if curr_room is None:
        raise Exception('Room None!')

    # print('room:', curr_room)
    
    # Chọn giờ
    valid_startings = get_valid_startings(curr_class)
    startings_with_teacher = get_startings_with_teacher(curr_class)
    startings_with_room = get_startings_with_room(curr_class, curr_room)

    all_valid_startings = valid_startings & startings_with_teacher & startings_with_room

    if not all_valid_startings:
        # print('No starting valid!')
        continue
    
    curr_starting = min(all_valid_startings)

    # Cập nhật biến
    assigned_g[g[curr_class]]['num_assigned'] += 1
    assigned_c[curr_room]['num_assigned'] += 1
    
    for temp in range(curr_starting, curr_starting + t[curr_class]):
        assigned_g[g[curr_class]]['periods'][temp] = 1
        assigned_c[curr_room]['periods'][temp] = 1

    curr_solution[curr_class] = (curr_starting, curr_room)


curr_solution = dict(sorted(curr_solution.items()))

print(len(curr_solution))
for class_id, data in curr_solution.items():
    print(class_id+1, data[0]+1, data[1]+1)