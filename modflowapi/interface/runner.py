from .. import ModflowApi
from .simulation import Simulation
from enum import Enum


class Callbacks(Enum):
    initialize = 0
    stress_period = 1
    timestep_start = 2
    timestep_end = 3
    iteration_start = 4
    iteration_end = 5


def run_model(dll, sim_path, callback, verbose=False):

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

    with open("var_list.txt", "w") as foo:
        for name in mf6.get_input_var_names():
            foo.write(f"{name}\n")

    for model in sim.models:
        callback(model, Callbacks.initialize)

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

        for sol_id, maxiter in sim.solutions.items():
            models = []
            for model in sim.models:
                if sol_id == model.solution_id:
                    models.append(model)

            # can we prepare and finalize the solutions for all
            mf6.prepare_solve(sol_id)
            # check on the simulation group solving and think about how to
            # solve, as a group of models or single models in serial...
            for ix, model in enumerate(models):
                if sim.kper != kperold[sol_id - 1]:
                    callback(model, Callbacks.stress_period)
                    if ix + 1 == len(models):
                        kperold[sol_id - 1] += 1
                elif current_time == 0:
                    callback(model, Callbacks.stress_period)

                kiter = 0
                callback(model, Callbacks.timestep_start)

                while kiter < maxiter:
                    model.iteration = kiter
                    callback(model, Callbacks.iteration_start)
                    has_converged = mf6.solve(sol_id)
                    callback(model, Callbacks.iteration_end)
                    kiter += 1
                    if has_converged:
                        break

                callback(model, Callbacks.timestep_end)

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
