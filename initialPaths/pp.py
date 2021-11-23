import json
import sys
from subprocess import Popen, PIPE

from minizinc import Model, Solver, Instance
from minizinc.CLI import CLIInstance
from numpy import random

from run_mzn import run_minizinc


def prioritised_planning(data):
    no_agents = len(data["agents"])
    data["priority"] = random_pp(no_agents)
    # print(data["priority"])
    with open('prioritised_planning_shortest.json', 'w') as outfile:
        json.dump(data, outfile)
    data["priority"] = shortest_pp(data, no_agents)
    # print(data["priority"])
    with open('prioritised_planning_random.json', 'w') as outfile:
        json.dump(data, outfile)
    data_shortest = run_minizinc("./../prioritised_planning.mzn", "prioritised_planning_shortest.json")
    data_random = run_minizinc("./../prioritised_planning.mzn", "prioritised_planning_random.json")
    result = {}
    result["Prioritised Planning Shortest Cost"] = data_shortest["statistics"]["objective"]
    result["Prioritised Planning Shortest Time"] = data_shortest["statistics"]["solveTime"]
    result["Prioritised Planning Random Cost"] = data_random["statistics"]["objective"]
    result["Prioritised Planning Random Time"] = data_random["statistics"]["solveTime"]
    return result


def random_pp(no_agents):
    rng = random.default_rng()
    return rng.permutation(no_agents).tolist()


def shortest_pp(data, no_agents):
    agents = [i for i in range(no_agents)]
    agents_by_path_length = sorted(agents, key=lambda x: get_path_length(data["paths"][x], data["dummy"]))
    priorities = [0] * no_agents
    for i in range(no_agents):
        agent = agents_by_path_length[i]
        priorities[agent] = i
    return priorities


def get_path_length(path, dummy):
    length = 0
    for location in path:
        if location == dummy:
            return length
        else:
            length += 1
    return length


if __name__ == '__main__':
    data_file = sys.argv[1]