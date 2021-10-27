
enum location;
location: dummy;
enum agents;

array[agents] of location: sources;
array[agents] of location: targets;

int: longestPath;
array[agents, 1..longestPath] of location: paths;
array[agents, 1..longestPath] of int: dist; % distances between previous location and current location
int: numEdgeSwaps;
array[1..2, 1..numEdgeSwaps] of agents: agentSwaps;
array[1..2, 1..numEdgeSwaps] of location: locationSwaps;
int: time = sum(dist);

array[agents, 1..longestPath] of var 0..time: arrival;  % time which agent arrives at loc of ith location
array[agents, 1..longestPath] of var 0..time: departure; % last time in which agent is at that location
array[agents] of var 0..time: planlen;

array[agents, location] of var -1..time: farr;
array[agents, location] of var -1..time: fdep;

array[location] of set of agents: sharedLocations = [{a | i in 1..longestPath, a in agents where paths[a, i] = l} | l in location];

% arrival calculation constraints

constraint forall(a in agents, l in 1..longestPath)(
              arrival[a, l] = farr[a, paths[a, l]]
);

constraint forall(a in agents)(
           arrival[a, 1] = 0);
                    
constraint forall(a in agents, i in 2..longestPath)(
           arrival[a, i] = departure[a, i - 1] + dist[a, i - 1]  % 
);

% departure calculation constraints

constraint forall(a in agents, i in 1..longestPath -1 where paths[a, i] != dummy )(
           departure[a, i] >= arrival[a, i]
);
                  

constraint forall(a in agents, l in 1..longestPath)(
              departure[a, l] = fdep[a, paths[a, l]]
);             

constraint forall(a in agents, i in 1..longestPath where paths[a, i] = dummy \/ paths[a, i] = targets[a])(
            departure[a, i] = time
);

% check for vertex collisions
% constraint forall(l in location where l != dummy, a, b in sharedLocations[l] where a < b)(
%                   forall(i, j in 1..longestPath where paths[a, i] = l /\ paths[b, j] = l)(
%                       departure[a, i] <= arrival[b, j] \/ departure[b, j] <= arrival[a, i]    
%                       )
%                   );

constraint forall(l in location where l != dummy, a, b in sharedLocations[l] where a < b)(
                      fdep[a, l] < farr[b, l] \/ fdep[b, l] < farr[a, l]    
                  );
                  
constraint forall(l in location where l!= dummy, a, b in sharedLocations[l] where a != b /\ targets[a] = l)(
                      farr[b, l] < farr[a, l]
);

% check for edge collisions

% fix this
% constraint forall(l, m in location where l != dummy /\ m != dummy, 
%                   a, b in (sharedLocations[l] intersect sharedLocations[m]))
%                   (
%                   forall(i, j in 2..longestPath where paths[a, i] = l /\ paths[a, i - 1] = m /\ paths[b, j] = m /\ paths[b, j -1] = l)
%                    (
%                           departure[a, i] <= arrival[b, j-1] \/ departure[b, j] <= arrival[a, i - 1]    
%                    ));

constraint forall(s in 1..numEdgeSwaps)(
                (fdep[agentSwaps[1, s], locationSwaps[1, s]] < farr[agentSwaps[2, s], locationSwaps[1, s]]
                \/ fdep[agentSwaps[2, s], locationSwaps[2, s]] < farr[agentSwaps[1, s], locationSwaps[2, s]])
                );

% calculate sum of costs

constraint planlen = [arrival[a, l] | a in agents, l in 1..longestPath where paths[a, l] = targets[a]];

var 0..time*card(agents): sumofcosts;

constraint sumofcosts = sum(planlen);

solve minimize sumofcosts;


output [if i == 1 then "Agent \(agents[a]): " else "" endif++ "\(arrival[a, i]): \(paths[a,i])" ++ if paths[a, i] = targets[a] then "\n" else ", " endif| a in agents, i in 1..longestPath where paths[a, i] != dummy] ++ ["\nCost of plan = ", show(sumofcosts)];