import numpy as np
from scipy import interpolate
from scipy.optimize import fminbound

template = """
seed 56689
app_style diffusion nonlinear hop
dimension {dimension}
lattice {lattice} {lattice_params}
region {region_name} {region_style} {region_bound}
create_box {region_name}
create_sites {create_sites}

{values}

barrier hop {barrier}

temperature {temperature}
solve_style {solve_style} {solve_params}

dump 1 text 10.0 dump.spparks
run 100.0
"""

lattice_style = {
        1: ['line/2n'],
        2: ['sq/4n', 'sq/8n', 'tri'],
        3: ['sc/6n', 'sc/26n', 'bcc', 'fcc', 'diamond', 'fcc/octa/tetra']
        }

def make_template(barrier):
    dimension = int(input("Please input dimension size: (select from 1, 2, 3)") or "3")
    lattice = input("Please input lattice style: (select from " + " ".join(lattice_style[dimension]) + ")") or lattice_style[dimension][-1]
    lattice_params = ""
    if lattice.startswith('random'):
        n_random = int(input("Please input the number of random sites: (select from INTEGER)") or "1")
        cut_off = float(input("Please input the distance within which sites are connected (distance units): (select from FLOAT)") or "1.0")
        lattice_params += str(n_random) + " " + str(cut_off)
    elif lattice != "none":
        scale = float(input("Please input the lattice constant (distance units): (select from FLOAT)") or "1.0")
        lattice_params += str(scale)
    region_name = input("Please input the name of the region:") or "default"
    region_style = input("Please input the style of the region: (select from block, cylinder, sphere, union, intersect)") or "block"
    region_bound = ""
    if region_style == "block":
        for i in range(dimension):
            region_bound += str(int(input("Please input the lower bound of dimension " + str(i+1) + ":") or "0")) + " "
            region_bound += str(int(input("Please input the upper bound of dimension " + str(i+1) + ":") or "50")) + " "
    else:
        raise RuntimeError("Region style " + region_style + " is not supported yet!")
    create_sites = input("Please input the type of the site: (select from box, region)") or "box"
    if create_sites != "box":
        raise RuntimeError("Site type " + create_sites + " is not supported yet!")

    print("Generating Values Per Site...")
    values = ""
    while True:
        label = input("Please input the label of the value: (press ENTER to skip, select from site or iN or dN or x or y or z or xyz)")
        if label == '':
            if values == "":
                values = "set site value 1.0"
            print("Finished Generating Values Per Site!")
            break
        style = input("Please input the style of the value: (select from value or range or displace)") or "value"
        print("""
        ------------ HELP ------------
        value arg = nvalue
            nvalue = value to set sites to
        range args = lo hi
            lo,hi = range of values to set sites to
        unique args = none
        displace arg = delta
             delta = max distance to displace the site
        ------------ OVER ------------
                """)

        style_arg = input("Please input the arg of the style: (as shown in the HELP)")
        print("""
        ------------ NOTE ------------
        zero or more keyword/value pairs may be appended
        ------------ HELP ------------
        fraction value = frac
            frac = number > 0 and <= 1.0
        region args = region-ID
            region-ID = ID of region that sites must be part of
        loop arg = all or local
            all = loop over all sites
            local = loop over only sites I own
        if args = label2 op nvalue2
            label2 = id or site or iN or dN or x or y or z
            op = "<" or "<=" or ">" or "<=" or "=" or "!="
            nvalue2 = value to compare site value to
        ------------ OVER ------------
                """)
        keyword = ""
        print("Begin Getting keyword/value pairs...")
        while True:
            keyword += input("Please input the keyword/value pairs: (press ENTER to skip)") + " "
            if keyword == '':
                print("Finished Logging keyword/value pairs!")
                break
        values += "set" + label + " " + style + " " + style_arg + " " + keyword + "\n"
    temperature = float(input("Please input temperature:") or "0.00")
    solve_style = input("Please input solve style: (select from linear, tree, none, group)") or "linear"
    solve_params = ""
    if solve_style == 'group':
        solve_params += str(float(input("Please input the lower bound of the group: (use FLOAT)") or "0.00")) + " "
        solve_params += str(float(input("Please input the upper bound of the group: (use FLOAT)") or "1.00")) + " "
        ngroup = input("Please input the number of groups to use: (press ENTER to skip, use INTEGER)") or ""
        if ngroup != "":
            solve_params += "ngroup " + ngroup
    return template.format(
            dimension=dimension,
            lattice=lattice,
            lattice_params=lattice_params,
            region_name=region_name,
            region_style=region_style,
            region_bound=region_bound,
            create_sites=create_sites,
            values=values,
            barrier=barrier,
            temperature=temperature,
            solve_style=solve_style,
            solve_params=solve_params,
            )


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
    res = make_template(max_value)
    with open(out, 'w') as f:
        f.write(res)
    print("Generating Complete, You May Run ./spk_serial < in.spparks To Check.")

if __name__ == '__main__':
    main()
