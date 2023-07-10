class Problem:
    def __init__(self, input_file):
        with open(input_file) as file:
            lines = [line.rstrip() for line in file]

        self.num_classes, self.num_rooms = tuple(int(x) for x in lines[0].split())

        self.classes = []
        for i in range(self.N):
            self.classes.append(tuple(int(x) for x in lines[i + 1].split()))

        self.room_capacities = [int(x) for x in lines[-1].split()]

    def slots_constraint(self, slots, rooms, k=None):
        if k is None:
            k = self.num_classes

        for i in range(k):
            if slots[i] == -1:
                continue
            slot_session = int(slots[i] / 6) * 6
