# Pyomo Sudoku solver by auke.greijdanus@gmail.com
# Solver: https://www.scipopt.org/download.php?fname=scipampl-7.0.0.win.x86_64.intel.opt.spx2.exe.zip

from pyomo.environ import *

sudoku = [
[0,0,0,0,0,0,4,0,3],
[5,0,0,7,0,4,0,0,1],
[0,0,4,5,0,0,0,7,0],
[0,0,1,0,7,0,0,9,8],
[0,0,0,4,0,6,0,0,0],
[3,8,0,0,9,0,7,0,0],
[0,1,0,0,0,8,5,0,0],
[9,0,0,1,0,7,0,0,6],
[8,0,5,0,0,0,0,0,0]
]

m = ConcreteModel()

m.i = RangeSet(9)
m.j = RangeSet(9)
m.z = RangeSet(9)
m.b = Set()
oneToNine = {1:1,2:2,3:3,4:4,5:5,6:6,7:7,8:8,9:9}

m.x = Var(m.i, m.j, within=PositiveIntegers, bounds=(1,9))
m.bin = Var(m.i, m.j, m.z, within=Binary)
m.t = Param(m.b, m.i, m.j, default=0, mutable=True)
m.objc = Var()

for rowNo,row in enumerate(sudoku):
    for colNo,number in enumerate(row):
        blockNo = ceil((rowNo+1)/3)**2 * ceil((colNo+1)/3)
        if blockNo not in m.b:
            m.b.add(blockNo)
        m.t[blockNo,rowNo+1,colNo+1] = 1
        if number > 0:
            m.x[rowNo+1,colNo+1].fixed = True
            m.x[rowNo+1,colNo+1].value = number

def constr_sud(m, i, j):
    return sum((m.bin[i,j,z] * oneToNine[z]) for z in m.z) == m.x[i,j]
m.constr_sud = Constraint(m.i, m.j, rule=constr_sud)

def constr_row(m, j, z):
    return sum(m.bin[i,j,z] for i in m.i) == 1
m.constr_row = Constraint(m.j , m.z, rule=constr_row)

def constr_col(m, i, z):
    return sum(m.bin[i,j,z] for j in m.j) == 1
m.constr_col = Constraint(m.i , m.z, rule=constr_col)

def constr_blk(m, b, z):
    return sum(sum((m.t[b,i,j] * m.bin[i,j,z]) for i in m.i) for j in m.j) == 1
m.constr_blk = Constraint(m.b, m.z, rule=constr_blk)

m.constr_obj = Constraint(rule=m.objc == 1)

m.obj = Objective(expr = m.objc, sense=maximize)
solver = SolverFactory("scip", executable='C:/Python/Pyomo/Solvers/scip/scipampl-7.0.0.win.x86_64.intel.opt.spx2.exe')
solver.solve(m, tee=True)

for i in m.i:
    for j in m.j:
        if j == 9:
            print(f"{round(m.x[i,j].value)}\n", end='')
            continue
        print(f"{round(m.x[i,j].value)} ", end='' )
