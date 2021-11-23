import os

from main import main
from os import listdir
from minizinc import Status

benchmark_loc = "../benchmarks"


def setup_files():
    with open("scheduling_stats.csv", "w") as file:
        file.write("map, scene, num_agents, intVars, intCon, boolVars, boolCon, objective, solveTime, conflicts, restarts, learnt clauses, status, lenShortest, shortestIndividual, maxTime, cbsCost, cbsTime, totalCorridor, First Solution Cost, First Solution Time, Prioritised Planning Shortest Cost, Prioritised Planning Shortest Time, Prioritised Planning Random Cost, Prioritised Planning Random Time\n")
    with open("max_stats.csv", "w") as file:
        file.write("map, scene, num_agents\n")


def write_path_stats(stats):
    with open("scheduling_stats.csv", "a") as file:
        for stat in stats:
            file.write(f"{stat[0]}, {stat[1]}, {stat[2]}")
            write_dict(file, stat[3])
            file.write('\n')


def write_dict(file, d):
    for key in d.keys():
        if key != "result":
            if isinstance(d[key], dict):
                write_dict(file, d[key])
            else:
                file.write(f", {d[key]}")



def write_max_stats(benchmarks):
    with open("max_stats.csv", "a") as file:
        for benchmark_max in benchmarks:
            file.write(f"{benchmark_max[0]}, {benchmark_max[1]}, {benchmark_max[2]}\n")


def run_scene(map_path, scene_path, map_name, scene_name):
    print(scene_name)
    last_solved = True
    n = 1
    path_stats = []
    with open(scene_path) as scene:
        max_agents = len(scene.readlines())
    while last_solved and n < max_agents:
        n += 1
        print(n)
        result = main(map_path, scene_path, f"{n}")
        last_solved = result["status"] == Status.OPTIMAL_SOLUTION
        path_stats.append([map_name, scene_name, n, result])
    return [map_name, scene_name, n-1], path_stats


if __name__ == "__main__":
    setup_files()
    benchmarks = os.listdir(benchmark_loc)
    for benchmark in benchmarks:
        max_agent_stats = []
        map = benchmark_loc + "/" + benchmark + "/" + benchmark + ".map"
        even_scenes = os.listdir(benchmark_loc + "/" + benchmark + "/scen-even")
        for scene in even_scenes:
            calculation_stats = []
            scene_loc = benchmark_loc + "/" + benchmark + "/scen-even/" + scene
            max_agents, stats = run_scene(map, scene_loc, benchmark, scene)
            max_agent_stats.append(max_agents)
            calculation_stats += stats
            write_path_stats(calculation_stats)
        # random_scenes = os.listdir(benchmark_loc + "/" + benchmark + "/scen-random")
        # for scene in random_scenes:
        #     scene_loc = benchmark_loc + "/" + benchmark + "/scen-random/" + scene
        #     max_agents, stats = run_scene(map, scene_loc, benchmark, scene)
        #     max_agent_stats.append(max_agents)
        #     calculation_stats += stats
        write_max_stats(max_agent_stats)


