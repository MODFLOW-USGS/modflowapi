import pytest
import os
from modflowapi import Callbacks, run_model
import shutil
import platform

so = "libmf6"
data_pth = os.path.join("..", "examples")
tmp_pth = os.path.join(".", "temp")


@pytest.mark.order(1)
def test_dis_model():
    def callback(sim, step):
        """
        Callback function

        Parameters
        ----------
        sim : modflowapi.Simulation object
        step : Enum
            step is the simulation step defined by Callbacks
        """
        if step == Callbacks.initialize:
            if len(sim.models) != 1:
                raise AssertionError("Invalid number of models")

            if len(sim.models.package_names) != 15:
                raise AssertionError("Invalid number of packages")



        elif step == Callbacks.stress_period:
            model = sim.models[0]
            x = model.package_names
            print('break')

    name = "test_model"
    sim_pth = os.path.join(data_pth, name)
    test_pth = os.path.join(tmp_pth, name)
    shutil.copytree(sim_pth, test_pth, dirs_exist_ok=True)

    run_model(so, test_pth, callback)


