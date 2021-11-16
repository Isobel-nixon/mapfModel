include "collisionresolving.mzn";

array[agents] of 1..card(agents): priority;

%% vertex collisions with priorities (this already ensures vertex collisions with priorities? atm)
constraint forall(l in location where l != dummy, a, b in sharedLocations[l] where a != b)(
                      priority[a] > priority[b] -> fdep[a, l] < farr[b, l]
                  );

 %% vertex collisions with priorities              
% constraint forall(s in 1..numEdgeSwaps)(
%                 (fdep[agentSwaps[1, s], locationSwaps[1, s]] < farr[agentSwaps[2, s], locationSwaps[1, s]]
%                 \/ fdep[agentSwaps[2, s], locationSwaps[2, s]] < farr[agentSwaps[1, s], locationSwaps[2, s]])
%                 /\
%                 (fdep[agentSwaps[1, s], locationSwaps[2, s]] < farr[agentSwaps[2, s], locationSwaps[2, s]]
%                 \/ fdep[agentSwaps[2, s], locationSwaps[1, s]] < farr[agentSwaps[1, s], locationSwaps[1, s]])
%                 );


solve minimize sumofcosts;