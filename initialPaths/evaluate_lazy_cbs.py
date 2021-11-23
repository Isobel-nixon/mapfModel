import io
from subprocess import run, TimeoutExpired, PIPE, STDOUT
import sys
import json


def get_paths():
    pass


def eval_lazy_cbs(map_path, agent_path, num_agents, time_limit=30):
    program_path = "./../../../../../Users/nixon/lazycbs/lazy-cbs"
    cmd = [program_path, "--map", map_path, "--agents", agent_path, "--upto", num_agents]
    # print("lazy-cbs started")
    try:
        p = run(cmd, capture_output=True, text=True, timeout=time_limit)
        res = p.stdout.split('\n')
        result = res[0]
        stats = res[1]
        solve_time = p.stderr.split(", ")[-1].strip("] ")
    except TimeoutExpired as timeErr:
        result = stats = timeErr.stdout
        solve_time = time_limit
    # res = p.split(b'\n')
    # result = res[0]
    # stats = res[1]
    # #
    try:
        result = json.loads(result)
        stats = json.loads(stats)
    except Exception as e:
        pass
    return result, stats, solve_time


if __name__ == '__main__':
    map_path = sys.argv[1]
    agent_path = sys.argv[2]
    num_agents = sys.argv[3]
    # map_path = "../maps/empty-8-8.map"
    # agent_path = "../agents/scen-even/empty-8-8-even-1.scen"
    # num_agents = "9"
    result = eval_lazy_cbs(map_path, agent_path, num_agents)
    print(result)