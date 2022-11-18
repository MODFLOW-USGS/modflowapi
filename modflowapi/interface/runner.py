from .. import ModflowApi
from .simulation import Simulation
from enum import Enum
import pathlib
import platform
import shutil


class Callbacks(Enum):
    initialize = 0
    stress_period = 1
    timestep_start = 2
    timestep_end = 3
    iteration_start = 4
    iteration_end = 5


def run_model(dll, sim_path, callback, verbose=False, _develop=False):
    """
    Method to run a Modflow simulation using the MODFLOW-API
    with a callback function

    Parameters
    ----------
    dll : str
        path to the Modflow6 shared object
    sim_path : str
        path to the Modflow6 simulation
    callback : method
        user defined method that intercepts the simulation
        progress and allows for input variable adjustments on the fly
    verbose : bool
        flag for verbose output from the simulation runner
    _develop : bool
        flag that dumps a list of all mf6 api variable addresses to text
        file named "var_list.txt". This is primarily used for interface
        development purposes and bug fixes within the modflowapi python
        package.
    """
    ext = pathlib.Path(dll).suffix
    if not ext:
        if platform.system().lower() == "windows":
            dll += ".dll"
        elif platform.system().lower() == "linux":
            dll = "./" + dll + ".so"
        else:
            dll += ".dylib"

    # sl = shutil.which(dll)
    # if sl is None:
    #     raise Exception(
    #         f"The program {dll} does not exist or is not executable"
    #     )
    # else:
    #     sl = pathlib.Path(dll).absolute()

    mf6 = ModflowApi(
        dll,
        working_directory=sim_path,
    )

    if verbose:
        version = mf6.get_version()
        print(f"MODFLOW-6 API Version {version}")
        print("Initializing MODFLOW-6 simulation")

    mf6.initialize()
    sim = Simulation.load(mf6)

    if _develop:
        with open("var_list.txt", "w") as foo:
            for name in mf6.get_input_var_names():
                foo.write(f"{name}\n")

    callback(sim, Callbacks.initialize)

    has_converged = False
    current_time = mf6.get_current_time()
    end_time = mf6.get_end_time()
    kperold = [0 for _ in range(sim.subcomponent_count)]

    while current_time < end_time:
        dt = mf6.get_time_step()
        mf6.prepare_time_step(dt)

        if verbose:
            print(
                f"Solving: Stress Period {sim.kper + 1}; "
                f"Timestep {sim.kstp + 1}"
            )

        for sol_id, maxiter in sorted(sim.solutions.items()):
            models = {}
            solution = {sol_id: maxiter}
            for model in sim.models:
                if sol_id == model.solution_id:
                    models[model.name.lower()] = model

            sim_grp = Simulation(mf6, models, solution)
            mf6.prepare_solve(sol_id)
            if sim.kper != kperold[sol_id - 1]:
                callback(sim_grp, Callbacks.stress_period)
                kperold[sol_id - 1] += 1
            elif current_time == 0:
                callback(sim_grp, Callbacks.stress_period)

            kiter = 0
            callback(sim_grp, Callbacks.timestep_start)

            while kiter < maxiter:
                sim_grp.iteration = kiter
                callback(sim_grp, Callbacks.iteration_start)
                has_converged = mf6.solve(sol_id)
                callback(sim_grp, Callbacks.iteration_end)
                kiter += 1
                if has_converged and sim_grp.allow_convergence:
                    break

            callback(sim_grp, Callbacks.timestep_end)
            mf6.finalize_solve(sol_id)

        mf6.finalize_time_step()
        current_time = mf6.get_current_time()

        if not has_converged:
            print(f"MODEL: {model.name} DID NOT CONVERGE")

    try:
        mf6.finalize()
    except Exception:
        raise RuntimeError("MF6 simulation failed, check listing file")

    print("SUCCESSFUL TERMINATION OF THE SIMULATION")
