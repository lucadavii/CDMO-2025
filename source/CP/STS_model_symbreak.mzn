include "globals.mzn";


int: n;
int: weeks = n-1;
int: periods = n div 2;
array[1..periods,1..weeks,0..1] of var 1..n: x;

constraint forall(i in 1..periods, j in 1..weeks)( %the teams in each slot must be diff
    all_different([x[i,j,k]|k in 0..1])
); 

constraint forall(j in 1..weeks)( %each team plays once in a week
    all_different([x[i,j,k]| i in 1..periods, k in 0..1])
);

constraint forall(i in 1..periods, l in 0..n)( %every team plays at most twice in the same period over the tournament
    count([x[i,j,k] | j in 1..weeks, k in 0..1], l) <= 2
);

constraint forall(a in 1..n, b in a+1..n)( %every team plays with every other team exactly once
    count([ (x[i,j,0]=a /\ x[i,j,1]=b) \/ (x[i,j,0]=b /\ x[i,j,1]=a) | i in 1..periods, j in 1..weeks ], true) == 1
);

% constraint(
%     x[1,1,0]=2 /\ x[1,1,1]=4 /\
%     x[2,1,0]=5 /\ x[2,1,1]=6 /\
%     x[3,1,0]=1 /\ x[3,1,1]=3
% );

%implied constraints

constraint forall(l in 1..n)( %each team plays exactly n-1 matches
    count([x[i,j,k] | i in 1..periods, j in 1..weeks, k in 0..1], l) = weeks
);

%symmetry breaking
constraint forall(i in 1..periods, j in 1..weeks)( %the first team in each slot must be less than the second team, eliminates symmetries in the single slots
    x[i,j,0] < x[i,j,1]
);

% constraint lex_lesseq(
%     [x[i,j,0] | i in 1..periods, j in 1..weeks],
%     [x[i,j,1] | i in 1..periods, j in 1..weeks]
% );

% constraint forall(i in 1..periods-1)( %order on the periods based on the first team to eliminate permutations of periods symmetries
%     lex_lesseq(
%         [x[i,j,0] | j in 1..weeks],
%         [x[i+1,j,0] | j in 1..weeks]
%     )
% );

constraint lex_lesseq(
    [x[i,j,0] | i in periods..1, j in 1..weeks],
    [x[i,j,0] | i in 1..periods, j in 1..weeks]
);

% constraint forall(j in 1..weeks-1)( %eliminate permutations of weeks symmetries
%     lex_lesseq(
%         [x[i,j,0] | i in 1..periods],
%         [x[i,j+1,0] | i in 1..periods]
%     )
%);

constraint lex_lesseq(
    [x[i,j,0]| i in 1..periods, j in weeks..1],
    [x[i,j,0]| i in 1..periods, j in 1..weeks]
);



solve ::int_search(x, first_fail,indomain_random, complete) :: restart_luby(120) :: relax_and_reconstruct(array1d(x),80) satisfy; %a solution is found more easily for n=14 if restart is 120 (comparable to peak depth) and p is rather high
%output ["[\(show(x[p,w,0])),\(show(x[p,w,1]))] "++ if w=weeks then "\n" else "" endif |p in 1..periods, w in 1..weeks]; 
output[
    "{\n\"sol\":\n" ++
    "[" ++
  concat([
    "[" ++
    concat([
      "[" ++ show(x[p, w, 0]) ++ "," ++ show(x[p, w, 1]) ++ "]"
      ++ if w != weeks then "," else "" endif
      | w in 1..weeks
    ]) ++ "]" ++
    if p != periods then ",\n" else "" endif
    | p in 1..periods
  ]) ++
  "]\n" ++
  "}"
];