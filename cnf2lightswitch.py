#!/usr/bin/python3
#
# CNF to lights/switchs translator
# 
# Translates any Dimacs formatted file
# into a beamer/tikz source tex file.
# 
# author Daniel Le Berre
# 
# License: GNU GPL 3.0
import sys
import fileinput



def dimacs2index(d):
    """
       Translate a Dimacs literal into a positive index

       Parameters:
       -----------
       d : int
          a Dimacs literal, i.e. a signed integer

       Returns:
       --------
       int
          a positive integer which can be used as index in an array

       >>> dimacs2index(1)
       2
       >>> dimacs2index(-1)
       3
       >>> dimacs2index(0)
       0
    """
    if (d==0):
        return 0
    
    if (d>0):
        return d*2
    
    return (-d*2)+1

def latex_header():
    """
       Print latex, beamer and tikz header
    """
    print("\documentclass{beamer}")
    print("\\usepackage{pgf, tikz}")
    print("\\usetikzlibrary{positioning, fit}")
    print("\\begin{document}")
    print("\\begin{frame}")
    print("\\begin{tikzpicture}[scale=0.5]")

def latex_footer():
    """
       Print latex, beamer and tikz footer
    """
    print("\end{tikzpicture}")
    print("\end{frame}")
    print("\end{document}")

def declare_variables(n):
    """
       Generate unactivated switches 
       
       Paramaters:
       -----------
       n: int
          the total number of variables

       Returns:
       --------
       [[]]
          an empty mapping associating each literal to the clauses it appears in
    """
    lit_to_clauses = [[] for i in range(2*n+2)]
    print("\\node (v1) at (0, 0) {{\\uncover<1>{\pgfimage[width = 1cm]{figures/switch}}}};")
    print("\\node[below = 0 of v1] () {v1};")
    for i in range(2,n+1):
        print("\\node[right = of v%d]  (v%d) {{\\uncover<1>{\pgfimage[width = 1cm]{figures/switch}}}};" % (i-1,i))
        print("\\node[below = 0 of v%d] () {v%d};" % (i,i))
    return lit_to_clauses

def declare_clauses(m):
    """
       Generate lights off
       
       Parameters:
       -----------
       m: int
          the total number of clauses
    """
    print("\\node[above = 2cm of v1] (c1) {{\\uncover<1>{\pgfimage[width = 1cm]{figures/lightoff.png}}}};")
    for i in range(2,m+1):
        print("\\node[right = of c%d] (c%d) {{\\uncover<1>{\pgfimage[width = 1cm]{figures/lightoff.png}}}};" % (i-1,i))


def handle_clause(clause,i,lit_to_clauses):
    """
       Connect the switches to the lights

    """
    for s in clause.split():
        l = int(s)
        if (l !=0):
            lit_to_clauses[dimacs2index(l)].append(i)
            if (l>0):
                print("\\draw (c%d.south) edge[bend left] (v%d.east);" % (i,l))
            else:
                assert l<0
                print("\\draw (c%d.south) edge[bend right] (v%d.west);" % (i,-l))
            
def handle_solution_line(line,i):
    """
        Translate a solution line into corresponding switch position and light status.

    """
    satisfied_clauses = set()
    for s in line.split()[1:]:
        l = int(s)
        if (l !=0):
            satisfied_clauses.update(lit_to_clauses[dimacs2index(l)])
            if (l>0): 
                print("\\node () at (v%d) {\\only<%d>{\pgfimage[width = 1cm]{figures/switchon}}} ;" % (l,i))
            else: 
                assert l<0
                print("\\node () at (v%d) {\\only<%d>{\pgfimage[width = 1cm]{figures/switchoff}}} ;" % (-l,i))
    for c in satisfied_clauses:
        print("\\node () at (c%d) {\\only<%d>{\pgfimage[width = 1cm]{figures/lighton}}} ;" % (c,i))
    for c in set(range(1,m+1)).difference(satisfied_clauses):
        print("\\node () at (c%d) {\\only<%d>{\pgfimage[width = 1cm]{figures/lightoff}}} ;" % (c,i))

def wait_for_solution(m,lit_to_clauses):
    """
        Reads an assignment from a SAT solver on stdin and position the switches accordingly.

        The method also takes care of switching on the lights corresponding to satisfied clauses.
        If there are several v lines, display all the available solutions.
    """
    i = 2
    for line in sys.stdin:
        if (line.startswith("v ")): 
            handle_solution_line(line,i)
            i += 1

if (len(sys.argv)!=2):
    print("Usage: ./cnf2lightswitch.py file.cnf </dev/null")
    print("       solver file.cnf | ./cnf2lightswitch.py file.cnf ")
    sys.exit(1)
    

dimacs = open(sys.argv[1],"r")

line = dimacs.readline()
while line.startswith("c "):
    line = dimacs.readline()

assert line.startswith("p cnf")
header = line.split()
n = int(header[2])
m = int(header[3])

latex_header()
lit_to_clauses = declare_variables(n)
declare_clauses(m)

i=1
for line in dimacs:
    handle_clause(line,i,lit_to_clauses)
    i += 1
dimacs.close

wait_for_solution(m,lit_to_clauses)

latex_footer()
