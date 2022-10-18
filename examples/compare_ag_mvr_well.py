import flopy
import os


sws = os.path.abspath(os.path.dirname(__file__))


def build_mf6(name, headtol=None, fluxtol=None):
    sim_ws = os.path.join(sws, name)
    sim = flopy.mf6.MFSimulation(name, sim_ws=sim_ws)

    perlen = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    period_data = [(i, i, 1.0) for i in perlen]
    tdis = flopy.mf6.ModflowTdis(
        sim,
        nper=12,
        perioddata=tuple(period_data),
        time_units="days"
    )

    ims = flopy.mf6.ModflowIms(
        sim,
        print_option="ALL",
        complexity="COMPLEX",
        no_ptcrecord=["ALL"],
        rcloserecord=[1e-10, "L2NORM_RCLOSE"],
        scaling_method="L2NORM",
        linear_acceleration="BICGSTAB",
        under_relaxation="DBD",
        under_relaxation_gamma=0.0,
        under_relaxation_theta=0.97,
        under_relaxation_kappa=0.0001
    )

    gwf = flopy.mf6.ModflowGwf(
        sim,
        modelname=name,
        save_flows=True,
        print_input=True,
        print_flows=True,
        newtonoptions="NEWTON UNDER_RELAXATION",
    )

    # define delc and delr to equal approximately 1 acre
    dis = flopy.mf6.ModflowGwfdis(
        gwf,
        nrow=10,
        ncol=10,
        delr=63.6,
        delc=63.6,
        top=100,
        length_units='meters'
    )

    ic = flopy.mf6.ModflowGwfic(gwf, strt=95)
    npf = flopy.mf6.ModflowGwfnpf(gwf, save_specific_discharge=True, icelltype=1)
    sto = flopy.mf6.ModflowGwfsto(gwf, iconvert=1)

    stress_period_data = {}
    for i in range(12):
        if i == 2:
            stress_period_data[i] = [[(0, 5, 4), -100.],
                                     [(0, 1, 2), -50.],]
        else:
            stress_period_data[i] = [[(0, 5, 4), -100.],
                                     [(0, 1, 2), -50.],]

    wel = flopy.mf6.ModflowGwfwel(
        gwf,
        stress_period_data=stress_period_data,
    )

    stress_period_data = {}
    for i in range(12):
        stress_period_data[i] = [[(0, 1, 2), 94, 10],
                                 [(0, 1, 3), 95, 10]]

    drn = flopy.mf6.ModflowGwfdrn(
        gwf,
        maxbound=2,
        stress_period_data=stress_period_data
    )

    stress_period_data = {}
    for i in range(12):
        stress_period_data[i] = [[(0, 9, 2), 0.25],
                                 [(0, 9, 3), 0.25]]
    rch = flopy.mf6.ModflowGwfrch(
        gwf,
        maxbound=2,
        stress_period_data=stress_period_data
    )

    rcha = flopy.mf6.ModflowGwfrcha(
        gwf,
    )

    stress_period_data = {}
    for i in range(12):
        stress_period_data[i] = [[(0, 0, 1), 100],
                                 [(0, 0, 2), 99]]
    chd = flopy.mf6.ModflowGwfchd(
        gwf,
        stress_period_data=stress_period_data
    )

    stress_period_data = {}
    for i in range(12):
        stress_period_data[i] = [[(0, 9, 1), 80, 1e-03],
                                 [(0, 9, 2), 81, 1e-03]]

    ghb = flopy.mf6.ModflowGwfghb(
        gwf,
        stress_period_data=stress_period_data
    )

    stress_period_data = {}
    for i in range(12):
        stress_period_data[i] = [[(0, 4, 3), 100, 2e-02, 10, 0.2, 0.1],
                                 [(0, 4, 4), 100, 2e-02, 10, 0.2, 0.1]]

    evt = flopy.mf6.ModflowGwfevt(
        gwf,
        maxbound=2,
        stress_period_data=stress_period_data
    )

    budget_file = f"{name}.cbc"
    head_file = f"{name}.hds"
    saverecord = {i: [("HEAD", "ALL"), ("BUDGET", "ALL")] for i in range(10)}
    printrecord = {i: [("HEAD", "ALL"), ("BUDGET", "ALL")] for i in range(10)}
    oc = flopy.mf6.ModflowGwfoc(gwf,
                                budget_filerecord=budget_file,
                                head_filerecord=head_file,
                                saverecord=saverecord,
                                printrecord=printrecord)

    sim.write_simulation()
    return sim, gwf


def mf6_dev_no_final_check(model_ws, fname):
    contents = []
    with open(os.path.join(model_ws, fname)) as foo:
        for line in foo:
            if "options" in line.lower():
                contents.append(line)
                contents.append("  DEV_NO_FINAL_CHECK\n")
            else:
                contents.append(line)

    with open(os.path.join(model_ws, fname), "w") as foo:
        for line in contents:
            foo.write(line)


if __name__ == "__main__":
    # set dll path
    load_existing = False
    run_model = True
    name = "dis_model"
    mf6_ws = os.path.join(sws, ".")

    sim, gwf = build_mf6(name)

