from subprocess import Popen, PIPE

from minizinc import Model, Solver, Instance, Status
from minizinc.CLI import CLIInstance

from parse_times import parse_times


def run_minizinc(model, data):
    collisions = Model(model)
    collisions.add_file(data)
    s = Solver.lookup("com.google.or-tools")
    instance = Instance(s, collisions)
    # print("started flatten")
    cli_instance = CLIInstance(s, collisions)
    fzn_name = model.rstrip(".mzn") + ".fzn"
    with cli_instance.flat() as t:
        # print(t)
        if "flatIntVars" in t[2]:
            intvars = t[2]["flatIntVars"]
            intcon = t[2]["flatIntConstraints"]
        else:
            intvars = 0
            intcon = 0
        if "flatBoolVars" in t[2]:
            boolvars = t[2]["flatBoolVars"]
            boolcon = t[2]["flatBoolConstraints"]
        else:
            boolvars = 0
            boolcon = 0
        with open(t[0].name) as temp:
            # print(temp.read())
            with open(fzn_name, "w") as f:
                f.write(temp.read())
    # use geas solver
    # /mnt/w/Users/nixon/geas/fzn/fzn_geas -s -f --obj-probe 50 --global-diff true satisfactory_schedule.fzn --time_out
    # p = Popen(["/mnt/w/Users/nixon/or-tools_flatzinc_VisualStudio2019-64bit_v9.1.9490/bin/fzn-or-tools.exe",
    #            fzn_name, "--statistics", "--time_limit", "60"], stdout=PIPE)
    p = Popen(["/mnt/w/Users/nixon/geas/fzn/fzn_geas", "-s", "-f", "--obj-probe", "50", "--global-diff", "true", "--time-out", "60",
               fzn_name], stdout=PIPE, stderr=PIPE)
    p.wait()
    # print("finish scheduling")
    result = p.stdout.readlines()
    result = [l.decode("utf-8") for l in result]
    stats = p.stderr.readlines()
    stats = stats[0].decode("utf-8").strip("\n").split(",")
    # print(result)
    # print(stats)
    res = {}
    res["intVars"] = intvars
    res["intCon"] = intcon
    res["boolVars"] = boolvars
    res["boolCon"] = boolcon
    statistics = {}
    res['statistics'] = statistics
    offset = 0
    # print(result)
    if not result:
        res['status'] = Status.ERROR
        offset = -4
        statistics['result'] = "None"
        statistics['objective'] = "0"
        statistics['solveTime'] = "0"
        statistics['conflicts'] = "0"
        statistics['restarts'] = "0"
        statistics['learnt clauses'] = "0"
        return res
    elif result[0] == "=====UNSATISFIABLE=====\n":
        res['status'] = Status.UNSATISFIABLE
        offset = -4
        statistics['result'] = "None"
        statistics['objective'] = "0"
    elif result[0] == "=====UNKNOWN=====\n":  # timed out before a solution could be found
        res['status'] = Status.UNKNOWN
        statistics['objective'] = stats[0]
        statistics['result'] = "None"
        offset = -4
    elif result[-1] == "%% INCOMPLETE\n":  # timed out before an optimal solution could be found
        if result[0][0] == "a":  # first thing is arrivals
            statistics['result'] = split_agent_times(result[0][10:-2])
            statistics['objective'] = result[1][13:-2]
        else:
            statistics['objective'] = result[0][13:-2]
            statistics['result'] = split_agent_times(result[1][10:-2])
        res['status'] = Status.SATISFIED
        offset = -1
    else:
        res['status'] = Status.OPTIMAL_SOLUTION
        if result[0][0] == "a": # first thing is arrivals
            statistics['result'] = split_agent_times(result[0][10:-2])
            statistics['objective'] = result[1][13:-2]
        else:
            statistics['objective'] = result[0][13:-2]
            statistics['result'] = split_agent_times(result[1][10:-2])
    statistics['solveTime'] = stats[-1]
    statistics['conflicts'] = stats[3]
    statistics['restarts'] = stats[2]
    statistics['learnt clauses'] = stats[4]

    return res


def split_agent_times(result):
    # print(result)
    num_steps, times = parse_times(result)
    agent_times = list(chunks(times, num_steps))
    return agent_times


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]