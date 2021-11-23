import matplotlib.pyplot as plt

def read_file():
    with open("costs.csv", "r") as file:
        data = file.readlines()
    for i in range(len(data)):
        data[i] = data[i].split(', ')
    return data


def get_costs_percent(data):
    costs = get_costs(data)
    agents = costs.pop()
    og = costs[0]
    percentages = [[] for _ in costs]
    for i in range(len(agents)):
        for c in range(len(costs)):
            percent = costs[c][i]/og[i]
            percentages[c].append(percent)
    return percentages


def get_costs(data):
    og = []
    cbs = []
    sched = []
    sched_first = []
    pp_shortest = []
    pp_random = []
    agents = []
    for line in data[:-1]:
        og.append(int(line[13]))
        cbs.append(int(line[16]))
        sched.append(int(line[7]))
        sched_first.append(int(line[19]))
        pp_random.append(int(line[23]))
        pp_shortest.append(int(line[21]))
        agents.append(int(line[2]))
    return [og, cbs, sched, sched_first, pp_shortest, pp_random, agents]


def get_times(data):
    og = []
    cbs = []
    sched_opt = []
    sched_first = []
    pp_shortest = []
    pp_random = []
    agents = []
    for line in data[:-1]:
        og.append(0.01) # time taken to get shortest paths (initial lazy cbs)
        cbs.append(float(line[17])/1000)
        sched_opt.append(float(line[8]))
        sched_first.append(float(line[20]))
        pp_random.append(float(line[24]))
        pp_shortest.append(float(line[23]))
        agents.append(int(line[2]))
    return [og, cbs, sched_opt, sched_first, pp_shortest, pp_random, agents]


def get_times_percent(data):
    costs = get_times(data)
    og = costs[0]
    agents = costs.pop()
    percentages = [[] for _ in costs]
    for i in range(len(agents)):
        for c in range(len(costs)):
            percentages[c].append(costs[c][i]/og[i])
    return percentages


def get_corridor(data):
    cor_len = []
    for line in data:
        cor_len.append(int(line[14]))
    return cor_len


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    file = read_file()
    labels = ["original", "lazy-cbs", "scheduling-opt", "scheduling-first", "scheduling-pp-shortest", "scheduling-pp-random"]
    res = get_costs(file)
    agents = res.pop()
    for i in range(0, 4):
        plt.plot(agents, res[i], label=labels[i])
    plt.legend()
    plt.ylabel("Cost")
    plt.xlabel("Number of Agents")
    plt.savefig("CostByMethod.png")
    plt.close()

    res = get_costs_percent(file)
    for i in range(0, 4):
        plt.plot(agents, res[i], label=labels[i])
    plt.legend()
    plt.ylabel("Cost")
    plt.xlabel("Number of Agents")
    plt.savefig("CostByMethodPercentage.png")
    plt.close()

    res = get_times(file)
    res.pop()
    for i in range(0, 4):
        plt.plot(agents, res[i], label=labels[i])
    plt.legend()
    plt.ylabel("Time")
    plt.xlabel("Number of Agents")
    plt.savefig("TimeByMethod.png")
    plt.close()

    res = get_times_percent(file)
    for i in range(0, 4):
        plt.plot(agents, res[i], label=labels[i])
    plt.legend()
    plt.ylabel("Time (%)")
    plt.xlabel("Number of Agents")
    plt.savefig("TimeByMethodPercentage.png")
    plt.close()

    agents.append(agents[-1] + 1)
    corridor_lengths = get_corridor(file)
    plt.plot(agents, corridor_lengths)
    plt.ylabel("Corridor Length")
    plt.xlabel("Number of Agents")
    plt.savefig("Corridor_Lengths.png")
    plt.close()

