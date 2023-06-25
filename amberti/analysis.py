import alchemlyb
from alchemlyb.estimators import TI
from alchemlyb.preprocessing import decorrelate_dhdl
from alchemlyb.parsing.amber import extract_dHdl
from alchemlyb.convergence import fwdrev_cumavg_Rc
from alchemlyb.visualisation import plot_convergence
from alchemlyb.convergence import forward_backward_convergence
import os
from pathlib import Path
import json

base_dir = Path(os.getcwd())
result = {}
for cl in ["ligands", "complex"]:
    wkdir = base_dir.joinpath(cl)
    for job in ["decharge", "recharge", "vdw_bonded"]:
        jobdir = wkdir.joinpath(job)
        lmd_lists = jobdir.glob("[0-9]*.*[0-9]")
        data_list = []
        for lmd in lmd_lists:
            data = extract_dHdl(lmd.joinpath("ti001.out"), T=300)
            decorrelated_dhdl = decorrelate_dhdl(data, remove_burnin=True)
            data_list.append(decorrelated_dhdl)
        dHdl = alchemlyb.concat(data_list)
        ti = TI()
        ti.fit(dHdl)
        fe = ti.delta_f_
        result[f"{cl}-{job}"] = fe.loc[0.00, 1.00]
        # R_c, running_average = fwdrev_cumavg_Rc(data_list, tol=2)

        df = forward_backward_convergence(data_list, 'ti')
        ax = plot_convergence(df)
        ax.figure.savefig(f'pics/dF_t_{cl}_{job}.png')

with open('result.json', "w") as fp:
    json.dump(result, fp, indent=4)

print("delta G = {}".format(
    result["complex-vdw_bonded"] + result["complex-recharge"] + result["complex-decharge"] - \
    (result["ligands-vdw_bonded"] + result["ligands-recharge"] + result["ligands-decharge"])
))