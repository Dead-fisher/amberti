from amberti.logger import getLogger
from amberti.amber import tleap
import os

logger = getLogger()

def create_simulation_box(
                          lib1, lib2, 
                          frcmod1, frcmod2, 
                          lpdb1, lpdb2, ppdb, llpdb,
                          ligand_forcefield,
                          protein_forcefield,
                          water='tip3p',
                          size=15.0, resize=0.75
    ):
    if water == "tip3p":
        waterbox = "TIP3PBOX"
        ionparm = "ionsjc_tip3p"
    else:
        logger.error("Water box style can only support tip3p. Not implemented.")
        RuntimeError("Not implemented.")

    scripts = [
        f"source leaprc.{ligand_forcefield}",
        f"source leaprc.water.{water}",
        f"source leaprc.protein.{protein_forcefield}",
        f"loadAmberParams frcmod.{ionparm}",
        f"loadoff {lib1}",
        f"loadoff {lib2}",
        f"loadamberparams {frcmod1}",
        f"loadamberparams {frcmod2}",

        # load the coordinates and create the complex
        f"mol1 = loadpdb {lpdb1}",
        f"mol2 = loadpdb {lpdb2}",
        f"protein = loadpdb {ppdb}",
        f"ligands = loadpdb {llpdb}"
        "complex1 = combine {mol1 protein}",
        "complex2 = combine {mol2 protein}",
        "complex3 = combine {ligands protein}"

        # create ligands in solution for vdw+bonded transformation
        f"solvatebox complex1 {waterbox} {str(size)} {str(resize)}",
        "addions complex1 Na+ 0",
        "savepdb complex1 complex_1.pdb",
        "saveamberparm complex1 complex_1.parm7 complex_1.rst7",

        # create ligands in solution for vdw+bonded transformation
        f"solvatebox complex2 {waterbox} {str(size)} {str(resize)}",
        "addions complex2 Na+ 0",
        "savepdb complex2 complex_2.pdb",
        "saveamberparm complex2 complex_2.parm7 complex_2.rst7",
        
        # create ligands in solution for vdw+bonded transformation
        f"solvatebox ligands TIP3PBOX {size}",
        "addions ligands Na+ 0",
        "savepdb ligands ligands_vdw_bonded.pdb",
        "saveamberparm ligands ligands_vdw_bonded.parm7 ligands_vdw_bonded.rst7",

        # create complex in solution for vdw+bonded transformation
        f"solvatebox complex TIP3PBOX {size} ",
        "addions complex Na+ 0",
        "savepdb complex complex_vdw_bonded.pdb",
        "saveamberparm complex complex_vdw_bonded.parm7 complex_vdw_bonded.rst7"

        "quit"
        ]
    fname = "tleap.buildtop.in"
    tleap("\n".join(scripts), fname=fname)



def make_charge_transform(
            lib1, lib2, 
            frcmod1, frcmod2, 
            lsolv, lmol1, lmol2,
            csolv, cmol1, cmol2,
            ligand_forcefield,
            protein_forcefield,
            water='tip3p',
    ):
    if water == "tip3p":
        ionparm = "ionsjc_tip3p"
    else:
        logger.error("Water box style can only support tip3p. Not implemented.")
        RuntimeError("Not implemented.")

    scripts = [
        f"source leaprc.{ligand_forcefield}",
        f"source leaprc.water.{water}",
        f"source leaprc.protein.{protein_forcefield}",
        f"loadAmberParams frcmod.{ionparm}",
        f"loadoff {lib1}",
        f"loadoff {lib2}",
        f"loadamberparams {frcmod1}",
        f"loadamberparams {frcmod2}",

        # load the coordinates and create the complex
        f"lsolv = loadpdb {lsolv}",
        f"lmol1 = loadpdb {lmol1}",
        f"lmol2 = loadpdb {lmol2}",

        f"csolv = loadpdb {csolv}",
        f"cmol1 = loadpdb {cmol1}",
        f"cmol2 = loadpdb {cmol2}",

        # decharge transformation
        'decharge = combine {lmol1 lmol1 lsolv}',
        'setbox decharge vdw',
        'savepdb decharge ligands_decharge.pdb',
        'saveamberparm decharge ligands_decharge.parm7 ligands_decharge.rst7',

        'decharge = combine {cmol1 cmol1 csolv}',
        'setbox decharge vdw',
        'savepdb decharge complex_decharge.pdb',
        'saveamberparm decharge complex_decharge.parm7 complex_decharge.rst7',

        # recharge transformation
        'recharge = combine {lmol2 lmol2 lsolv}',
        'setbox recharge vdw',
        'savepdb recharge ligands_recharge.pdb',
        'saveamberparm recharge ligands_recharge.parm7 ligands_recharge.rst7',

        'recharge = combine {cmol2 cmol2 csolv}',
        'setbox recharge vdw',
        'savepdb recharge complex_recharge.pdb',
        'saveamberparm recharge complex_recharge.parm7 complex_recharge.rst7',

        "quit"
        ]
    
    fname = "tleap.charge.in"
    logger.info("Create the decharging and recharging topology.")
    tleap("\n".join(scripts), fname=fname)



    