# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

class VertexCollisionError(Exception):
    pass


class EdgeCollisionError(Exception):
    pass


def simulate(paths, arrival_times, dummy):
    paths = [path[::-1] for path in paths]
    # print(paths)
    arrival_times = [time[::-1] for time in arrival_times]
    current_locations = [path.pop() for path in paths]
    for time in arrival_times:
        time.pop()
    # print(arrival_times)
    time = 1
    some_remaining = True
    while some_remaining:
        prev_locations = current_locations[::]
        some_remaining = False
        for agent in range(len(paths)):
            if not arrival_times[agent]:
                # agent has already reached its goal
                continue
            else:
                # print(agent, arrival_times[agent][-1], time)
                if arrival_times[agent][-1] == time:
                    # move agent
                    if paths[agent][-1] != dummy:
                        current_locations[agent] = paths[agent].pop()
                        arrival_times[agent].pop()
                        some_remaining = True
                    else:
                        paths[agent] = []
                        arrival_times[agent] = []
                else:
                    # agent doesn't move to it's next location yet
                    continue
        # check for vertex collisions
        if len(list(set(current_locations))) != len(current_locations):
            overlapping_loc = [i for i in current_locations if current_locations.count(i) > 1]
            overlapping_agents = [i for i in range(len(current_locations)) if current_locations.count(current_locations[i]) > 1]
            raise VertexCollisionError(f"Collision at time={time} at location={overlapping_loc} between agents={overlapping_agents}")
        # check for edge collisions
        for i in range(len(current_locations)):
            loc = current_locations[i]
            following_agent = get_index(prev_locations, loc, i)
            if following_agent >= 0:
                if current_locations[following_agent] == prev_locations[i]: # swapped locations
                    raise EdgeCollisionError(f"Collision at time={time} between locations={loc, prev_locations[i]} and agents={i, following_agent}")
        time += 1


def get_index(locations, location, excl):
    for i in range(len(locations)):
        if i != excl:
            if locations[i] == location:
                return i
    return -1

