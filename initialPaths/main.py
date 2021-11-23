import io
from subprocess import Popen, PIPE
import sys
import json
from parse_times import parse_times
from minizinc import Instance, Model, Solver
from minizinc.CLI import CLIInstance
from pathlib import Path
from minizinc import Status

import run_mzn
from evaluate_lazy_cbs import eval_lazy_cbs
from pp import prioritised_planning
from simulation import simulate

dummy_loc = (-1, -1)

def get_locations(r):
    locations = set([])
    for path in r.values():
        for location in path:
            locations.add((location[0], location[1]))
    locations = list(locations)
    return locations


def get_agents(r):
    agents = []
    for a in r.keys():
        agents.append(a)
    return agents


def get_paths(r, dummy):
    paths = []
    longest_path = len(max(r.values(), key=len))
    sources = []
    targets = []
    length_all_paths = 0
    for path in r.values():
        sources.append(tuple(path[0]))
        targets.append(tuple(path[-1]))
        new_path = []
        for location in path:
            length_all_paths += 1
            new_path.append(tuple(location))
        length_all_paths -= 1
        while len(new_path) < longest_path:
            new_path.append(dummy)
        paths.append(new_path)
    return paths, longest_path, sources, targets, length_all_paths


def get_dists(paths, targets, dummy):
    dists = []
    time =0
    for agent in range(len(paths)):
        agent_dists = []
        for location in paths[agent]:
            if not (location == targets[agent] or location == dummy):
                agent_dists.append(1)
            else:
                agent_dists.append(0)
            time += sum(agent_dists)
        dists.append(agent_dists)
    return dists, time


# def get_edge_swaps(paths, agents, dummy):
#     # TODO: only get the end points of these corridoors for faster computation?
#     num_swaps = 0
#     agent_swaps = [[],[]]
#     location_swaps = [[],[]]
#     def swap(a1, a2, l1, l2):
#         if l1 != dummy and l2 != dummy:
#             agent_swaps[0].append(agents[a1])
#             agent_swaps[1].append(agents[a2])
#             location_swaps[0].append(l1)
#             location_swaps[1].append(l2)
#             return True
#         return False
#     for a1 in range(len(paths)):
#         for a2 in range(a1 + 1, len(paths)):
#             for l in range(len(paths[a1])):
#                 try:
#                     i = paths[a2].index(paths[a1][l])
#                     # paths[a1][l] == paths[a2][i]
#                     if l > 0:
#                         if i < len(paths[a1]) - 1:
#                             if paths[a1][l - 1] == paths[a2][i + 1]:
#                                 if swap(a1, a2, paths[a1][l - 1], paths[a1][l]):
#                                     num_swaps += 1
#                                     pass
#                     if l < len(paths[a1]) - 1:
#                         if i > 0:
#                             if paths[a1][l + 1] == paths[a2][i - 1]:
#                                 if swap(a1, a2, paths[a1][l + 1], paths[a1][l]):
#                                     num_swaps += 1
#                                     pass
#                 except ValueError:
#                     pass
#     return num_swaps, agent_swaps, location_swaps

def get_collisions(paths, agents, dummy=dummy_loc):
    num_swaps = 0
    agent_swaps = [[],[]]
    location_swaps = [[],[]]
    total_corridor_len = 0
    num_intersections = 0
    agent_intersections = [[],[]]
    location_intersections = []
    def swap(a1, a2, l1, l2):
        if l1 != dummy and l2 != dummy:
            agent_swaps[0].append(agents[a1])
            agent_swaps[1].append(agents[a2])
            location_swaps[0].append(l1)
            location_swaps[1].append(l2)
            return True
        return False
    def cross(a1, a2, l1):
        if l1 != dummy:
            agent_intersections[0].append(agents[a1])
            agent_intersections[1].append(agents[a2])
            location_intersections.append(l1)
            return True
        return False
    for a1 in range(len(paths)):
        for a2 in range(a1 + 1, len(paths)):
            # print(a1, a2)
            in_corridor = False
            start_corridor = -1
            end_corridor = -1
            len_corridor = 0
            j = -1
            for i in range(len(paths[a1])):
                l1 = paths[a1][i]
                if l1 != dummy:
                    if not in_corridor:
                        j = get_index(paths, a2, l1)

                        if j > 0:  # is a shared location (l1 in path of a2)
                            in_corridor = True
                            start_corridor = l1
                            end_corridor = l1
                            len_corridor = 1
                        # else if intersection at a2 starting location
                        elif j == 0:
                            if cross(a1, a2, l1):
                                num_intersections += 1
                        # else location not in a2 path
                    else:   #currently in a corridor
                        l2 = paths[a2][j - len_corridor]
                        if j - len_corridor > 0:
                            if l2 == l1:
                                end_corridor = l1
                                len_corridor += 1
                            else:
                                if len_corridor > 1:
                                    if swap(a1, a2, start_corridor, end_corridor):
                                        num_swaps += 1
                                        total_corridor_len += len_corridor
                                else: #intersection (or following corridor)
                                    if cross(a1, a2, start_corridor):
                                        num_intersections += 1
                                    # could be following so check
                                    if j + 1 < len(paths[a2]) and l1 == paths[a2][j + 1]:
                                        if cross(a1, a2, l1):
                                            num_intersections += 1
                                in_corridor = False
                                start_corridor = -1
                                end_corridor = -1
                                len_corridor = 0
                                j = -1
                        elif j - len_corridor == 0:   # l2 = a2 start location
                            # reached start of a2 path
                            if l2 == l1:    # not well formed instance
                                end_corridor = l1
                                len_corridor += 1
                            if len_corridor > 1:
                                if swap(a1, a2, start_corridor, end_corridor):
                                    num_swaps += 1
                                    total_corridor_len += len_corridor
                                in_corridor = False
                                start_corridor = -1
                                end_corridor = -1
                                len_corridor = 0
                                j = -1
                            else:
                                if cross(a1, a2, start_corridor):
                                    num_intersections += 1
                                in_corridor = False
                                start_corridor = -1
                                end_corridor = -1
                                len_corridor = 0
                                j = -1
                            break
                else:
                    # reached end of a1's path
                    break
            # if we are still in a corridor at the end of a1's path
            if in_corridor:
                if len_corridor > 1:
                    if swap(a1, a2, start_corridor, end_corridor):
                        num_swaps += 1
                        total_corridor_len += len_corridor
                else:
                    if cross(a1, a2, start_corridor):
                        num_intersections += 1
    return num_swaps, agent_swaps, location_swaps, total_corridor_len, num_intersections, agent_intersections, location_intersections


def get_index(paths, agent, location):
    # print(location)
    for i in range(len(paths[agent])):
        if paths[agent][i] == location:
            return i
    return -1

def format_enums(enums):
    new_enums = []
    for e in enums:
        new_enums.append({"e": f"`{e}`"})
    return new_enums


def format_list_enums(l_enums):
    new_enums = []
    for lst in l_enums:
        new_enums.append(format_enums(lst))
    return new_enums


def main(map_path, agent_path, num_agents):
    # print("start")
    program_path = "./../../../../../Users/nixon/lazycbs-initial/lazy-cbs"
    p = Popen([program_path, "--map", map_path, "--agents", agent_path, "--upto", num_agents, "--time_limit", "60"], stdout=PIPE)
    # print("initial paths started")
    p.wait()
    # print("initial paths finished")
    result = p.stdout.readline()
    # result = "{\"Agent 0\": [[0, 0], [0, 1], [0, 2]], \"Agent 1\": [[1, 1], [0, 1], [0, 0]]}"
    # result = "{\"Agent 0\": [[0, 1], [1, 1], [1, 0]], \"Agent 1\": [[0, 0], [1, 0], [1, 1], [1, 2]]}"
    # result = "{\"A0\": [[0, 0], [1, 0], [1, 1], [1, 2]], \"A1\": [[0, 1], [1, 1], [1, 0]]}"
    # result = sys.argv[1]
    try:
        result_dict = json.loads(result)
    except Exception as e:
        print(result)
        print(map_path)
        print(agent_path)
        print(num_agents)
        return
    # print(result_dict)
    #
    locs = get_locations(result_dict)

    locs.append(dummy_loc)
    agents = get_agents(result_dict)
    paths, max_len, sources, targets, tot_len = get_paths(result_dict, dummy_loc)
    dists, time = get_dists(paths, targets, dummy_loc)
    num_swaps, agent_swaps, location_swaps, total_corridor, num_crossings, agent_cross, location_cross = get_collisions(paths, agents, dummy_loc)
    # print(paths)
    times = [[i for i in range(len(path))] for path in paths]

    # simulate(paths, times, dummy_loc)

    data = {
        "location": format_enums(locs),
        "dummy": {"e": f"`{dummy_loc}`"},
        "agents": format_enums(agents),
        "sources": format_enums(sources),
        "targets": format_enums(targets),
        "paths": format_list_enums(paths),
        "longestPath": max_len,
        "dist": dists,
        "numIntersections": num_crossings,
        "agentInt": format_list_enums(agent_cross),
        "locationInt": format_enums(location_cross),
        "numEdgeSwaps": num_swaps,
        "agentSwaps": format_list_enums(agent_swaps),
        "locationSwaps": format_list_enums(location_swaps)
            }
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)
    # print("lazy_cbs started")
    cbs_paths, cbs_stats, cbs_time = eval_lazy_cbs(map_path, agent_path, num_agents)
    # print("lazy_cbs finished")
    if not cbs_stats:
        cbs_cost = "N/A"
    else:
        # print(cbs_stats)
        cbs_cost = cbs_stats[0]
    # print("optimal schedule started")
    res = run_mzn.run_minizinc("./../optimal_schedule.mzn", "./data.json")
    # print("optimal schedule finished")
    res["lenShortest"] = tot_len
    res["shortestIndividual"] = max_len
    res["maxTime"] = time
    res["cbsCost"] = cbs_cost
    res["cbsTime"] = cbs_time
    res["totalCorridor"] = total_corridor
    # print("satisfactory schedule started")
    res_satisfy = run_mzn.run_minizinc("./../satisfactory_schedule.mzn", "./data.json")
    # print("satisfactory schedule finished")
    res["firstFound"] = {}
    res["firstFound"]["First Solution Cost"] = res_satisfy["statistics"]["objective"]
    res["firstFound"]["First Solution Time"] = res_satisfy["statistics"]["solveTime"]
    # print("prioritised planning started")
    res["prioritisedPlanning"] = prioritised_planning(data)
    # print("prioritised planning finished")
    if res["statistics"]["result"] != "None":
        simulate(paths, res["statistics"]["result"], dummy_loc)
    # simulate(paths, res["statistics"]["result"], dummy_loc)
    return res


if __name__ == '__main__':
    map_path = sys.argv[1]
    agent_path = sys.argv[2]
    num_agents = sys.argv[3]
    # map_path = "../maps/empty-8-8.map"
    # agent_path = "../agents/scen-even/empty-8-8-even-1.scen"
    # num_agents = "9"
    result = main(map_path, agent_path, num_agents)
    print(result)
    # print(result.statistics)

