import modflowapi
from modflowapi import Callbacks


def my_function(ml, step):
    if step == Callbacks.stress_period:
        rch_data = ml.rch[0].stress_period_data

        rch_data["recharge"] -= 10
        rch_data = ml.rch_0.stress_period_data.values
        # ml.rch_0.stress_period_data.values = rch_data

        rhs = ml.rch[0].rhs
        hcof = ml.rch_0.hcof
        # do stuff
        ml.rch_0.stress_period_data.values = rch_data
        chk = ml.rch_0.stress_period_data.values

    if step == Callbacks.timestep_start:
        ml.wel.stress_period_data["flux"] -= ml.kstp * 1.5
        chk = ml.wel.stress_period_data.values

        rhs = ml.wel.rhs
        hcof = ml.wel.hcof

    if step == Callbacks.iteration:
        chd = ml.chd
        spd = chd.stress_period_data.values
        spd["head"] -= 0.1
        chd.stress_period_data.values = spd
        chk = chd.stress_period_data.values


def my_other_function(ml, step):
    # make sure that DISV is working
    if step == Callbacks.timestep_start:
        k11 = ml.npf.k11
        k11[0:10] *= 30
        ml.npf.k11 = k11

        x = ml.chd_left.stress_period_data.values
        print('break')


def yet_another_function(ml, step):
    # make sure that DISU is working
    if step == Callbacks.timestep_start:
        k11 = ml.npf.k11
        print('break')


def two_model_function(ml, step):
    # check multi-model simulations
    if step == Callbacks.timestep_start:
        print(f"{ml.name}")


if __name__ == "__main__":
    import os
    dll = os.path.join("..", "trunk", "bin", "libmf6.dll")

    sim_pth = os.path.join(".", "examples", "test_model")
    modflowapi.run_model(dll, sim_pth, my_function, verbose=True)

    sim_pth = os.path.join(".", "examples", "disv_model")
    modflowapi.run_model(dll, sim_pth, my_other_function, verbose=True)

    sim_pth = os.path.join(".", "examples", "disu_model")
    modflowapi.run_model(dll, sim_pth, yet_another_function, verbose=True)

    sim_pth = os.path.join(".", "examples", "two_models")
    modflowapi.run_model(dll, sim_pth, two_model_function, verbose=True)