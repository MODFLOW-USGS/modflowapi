import pytest
import os
from modflowapi.interface.pakbase import (
    ArrayPackage,
    ListPackage,
    AdvancedPackage,
)
from modflowapi import Callbacks, run_model
import shutil
import numpy as np

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

            model = sim.test_model
            if len(model.package_names) != 17:
                raise AssertionError("Invalid number of packages")

            if len(model.package_types) != 16:
                raise AssertionError("Invalid number of package types")

            if model.shape != (1, 10, 10):
                raise AssertionError("Model shape is incorrect")

            if model.size != 100:
                raise AssertionError("Model size is incorrect")

            if (model.kper, model.kstp) != (-1, -1):
                raise AssertionError(
                    "Model has advanced prior to initialization callback"
                )

            dis = model.dis
            if not isinstance(dis, ArrayPackage):
                raise TypeError("DIS package has incorrect base class type")

            wel = model.wel
            if not isinstance(wel, ListPackage):
                raise TypeError("WEL package has incorrect base class type")

            gnc = model.gnc
            if not isinstance(gnc, AdvancedPackage):
                raise TypeError("GNC package has incorrect base class type")

            rch = model.rch
            if len(rch) != 2:
                raise AssertionError(
                    "Model object not returning multiple packages"
                )

            idomain = dis.idomain.values
            if not isinstance(idomain, np.ndarray):
                raise TypeError("Expecting a numpy array for idomain")

        elif step == Callbacks.stress_period:
            if sim.kstp != 0:
                raise AssertionError(
                    "Solution advanced prior to stress_period callback"
                )

        elif step == Callbacks.timestep_start:
            if sim.iteration != -1:
                raise AssertionError(
                    "Solution advanced prior to timestep_start callback"
                )

            factor = ((1 + sim.kstp) / sim.nstp) * 0.5
            spd = sim.test_model.wel.stress_period_data.values
            sim.test_model.wel.stress_period_data["flux"] *= factor

            spd2 = sim.test_model.wel.stress_period_data.values
            if not np.allclose((spd["flux"] * factor), spd2["flux"]):
                raise AssertionError("Pointer not being set properly")

    name = "test_model"
    sim_pth = os.path.join(data_pth, name)
    test_pth = os.path.join(tmp_pth, name)
    shutil.copytree(sim_pth, test_pth, dirs_exist_ok=True)

    run_model(so, test_pth, callback)


@pytest.mark.order(2)
def test_disv_model():
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

            model = sim.gwf_1
            if len(model.package_names) != 12:
                raise AssertionError("Invalid number of packages")

            if len(model.package_types) != 11:
                raise AssertionError("Invalid number of package types")

            if model.shape != (4, 200):
                raise AssertionError("Model shape is incorrect")

            if model.size != 800:
                raise AssertionError("Model size is incorrect")

            if (model.kper, model.kstp) != (-1, -1):
                raise AssertionError(
                    "Model has advanced prior to initialization callback"
                )

            dis = model.dis
            if not isinstance(dis, ArrayPackage):
                raise TypeError("DIS package has incorrect base class type")

            chd = model.chd_left
            if not isinstance(chd, ListPackage):
                raise TypeError("CHD package has incorrect base class type")

            hfb = model.hfb
            if not isinstance(hfb, AdvancedPackage):
                raise TypeError("HFB package has incorrect base class type")

            chd = model.chd
            if len(chd) != 2:
                raise AssertionError(
                    "Model object not returning multiple packages"
                )

            top = dis.top.values
            if not isinstance(top, np.ndarray):
                raise TypeError("Expecting a numpy array for top")

        elif step == Callbacks.stress_period:
            if sim.kstp != 0:
                raise AssertionError(
                    "Solution advanced prior to stress_period callback"
                )

        elif step == Callbacks.timestep_start:
            if sim.iteration != -1:
                raise AssertionError(
                    "Solution advanced prior to timestep_start callback"
                )

            factor = 0.75
            spd = sim.gwf_1.chd_left.stress_period_data.values
            sim.gwf_1.chd_left.stress_period_data["head"] *= factor

            spd2 = sim.gwf_1.chd_left.stress_period_data.values
            if not np.allclose((spd["head"] * factor), spd2["head"]):
                raise AssertionError("Pointer not being set properly")

    name = "disv_model"
    sim_pth = os.path.join(data_pth, name)
    test_pth = os.path.join(tmp_pth, name)
    shutil.copytree(sim_pth, test_pth, dirs_exist_ok=True)

    run_model(so, test_pth, callback)


@pytest.mark.order(3)
def test_disu_model():
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

            model = sim.gwf_1
            if len(model.package_names) != 12:
                raise AssertionError("Invalid number of packages")

            if len(model.package_types) != 12:
                raise AssertionError("Invalid number of package types")

            if model.shape != (121,):
                raise AssertionError("Model shape is incorrect")

            if model.size != 121:
                raise AssertionError("Model size is incorrect")

            if (model.kper, model.kstp) != (-1, -1):
                raise AssertionError(
                    "Model has advanced prior to initialization callback"
                )

            dis = model.dis
            if not isinstance(dis, ArrayPackage):
                raise TypeError("DIS package has incorrect base class type")

            rch = model.rch
            if not isinstance(rch, ListPackage):
                raise TypeError("RCH package has incorrect base class type")

            mvr = model.mvr
            if not isinstance(mvr, AdvancedPackage):
                raise TypeError("MVR package has incorrect base class type")

            top = dis.top.values
            if not isinstance(top, np.ndarray):
                raise TypeError("Expecting a numpy array for top")

        elif step == Callbacks.stress_period:
            if sim.kstp != 0:
                raise AssertionError(
                    "Solution advanced prior to stress_period callback"
                )

        elif step == Callbacks.timestep_start:
            if sim.iteration != -1:
                raise AssertionError(
                    "Solution advanced prior to timestep_start callback"
                )

            factor = 1.75
            spd = sim.gwf_1.rch.stress_period_data.values
            sim.gwf_1.rch.stress_period_data["recharge"] += factor

            spd2 = sim.gwf_1.rch.stress_period_data.values
            if not np.allclose((spd["recharge"] + factor), spd2["recharge"]):
                raise AssertionError("Pointer not being set properly")

    name = "disu_model"
    sim_pth = os.path.join(data_pth, name)
    test_pth = os.path.join(tmp_pth, name)
    shutil.copytree(sim_pth, test_pth, dirs_exist_ok=True)

    run_model(so, test_pth, callback)


@pytest.mark.order(4)
def test_two_models():
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
            if len(sim.models) != 2:
                raise AssertionError("Invalid number of models")

    name = "two_models"
    sim_pth = os.path.join(data_pth, name)
    test_pth = os.path.join(tmp_pth, name)
    shutil.copytree(sim_pth, test_pth, dirs_exist_ok=True)

    run_model(so, test_pth, callback)
