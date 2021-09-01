
enum location;
location: dummy;
enum agents;

array[agents] of location: sources;
array[agents] of location: targets;

int: longestPath;
array[agents, 1..longestPath] of location: paths;
array[agents, 1..longestPath] of int: dist; % distances between previous location and current location
int: time = sum(dist);

array[agents, 1..longestPath] of var 0..time: arrival;  % time which agent arrives at loc of ith location
array[agents, 1..longestPath] of var 0..time: departure;
array[agents] of var 0..time: planlen;

array[location] of set of agents: sharedLocations = [{a | i in 1..longestPath, a in agents where paths[a, i] = l} | l in location];

% arrival calculation constraints
constraint forall(a in agents)(
           arrival[a, 1] = 0);
                    
constraint forall(a in agents, i in 2..longestPath)(
           arrival[a, i] >= arrival[a, i - 1] + dist[a, i]  
);

% departure calculation constraints

constraint forall(a in agents, i in 1..longestPath -1 where paths[a, i] != dummy)(
           departure[a, i] >= arrival[a, i] + dist[a, i + 1]
);
                  
constraint forall(a in agents, i in 1..longestPath -1 where paths[a, i] != dummy)(
           paths[a, i] != targets[a] /\ paths[a, i] != dummy-> departure[a, i] = arrival[a, i + 1]
);                

% set departure time for target/dummy to maxTime since we never actually depart from goal/dummy
constraint forall(a in agents, i in 1..longestPath)(
           paths[a, i] = targets[a] \/ paths[a, i] = dummy ->
           departure[a, i] = time
);


% check for vertex collisions
constraint forall(l in location where l != dummy, a, b in sharedLocations[l] where a < b)(
                  forall(i, j in 1..longestPath where paths[a, i] = l /\ paths[b, j] = l)(
                      departure[a, i] <= arrival[b, j] \/ departure[b, j] <= arrival[a, i]    
                      )
                  );

% check for edge collisions

constraint forall(l, m in location where l != dummy /\ m != dummy, 
                  a, b in (sharedLocations[l] intersect sharedLocations[m]))
                  (
                  forall(i, j in 2..longestPath where paths[a, i] = l /\ paths[a, i - 1] = m /\ paths[b, j] = m /\ paths[b, j -1] = l)
                   (
                          departure[a, i] <= arrival[b, j-1] \/ departure[b, j] <= arrival[a, i - 1]    
                   ));

% calculate sum of costs

constraint planlen = [arrival[a, longestPath] | a in agents];

var 0..time: sumofcosts;

constraint sumofcosts = sum(planlen);

solve minimize sumofcosts;
