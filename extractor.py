import numpy as np
from scipy import interpolate
from scipy.optimize import fminbound

template = """
seed 56689
app_style diffusion nonlinear hop
dimension 3
lattice sc/26n 1
region myregion block 0 50 0 50 0 50
create_box myregion
create_sites box
set site value 1
set site value 2 if z < 4.0
set site value 3 if z < 2.0
set site value 3 if z > 49.0

barrier hop {}

temperature .0257
solve_style linear

dump 1 text 10.0 dump.spparks
run 100.0
"""

def main():
    col = 2
    dat = 'neb.dat'
    out = 'in.spparks'
    ind = []
    var = []
    with open(dat, 'r') as f:
        for line in f:
            ind.append(float(line.split()[0]))
            var.append(-1 * float(line.split()[col]))
    #print(ind)
    #print(var)
    func = interpolate.interp1d(ind, var, kind='nearest')
    max_value = -1 * fminbound(func, float(ind[0]), float(ind[-1]))
    print("Barrier Value is: " + str(max_value))
    res = template.format(max_value)
    with open(out, 'w') as f:
        f.write(res)
    print("Generating Complete, You May Run ./spk_serial < in.spparks To Check.")

if __name__ == '__main__':
    main()
