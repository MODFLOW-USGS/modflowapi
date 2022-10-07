from .. import ModflowApi
from .simulation import Simulation
from enum import Enum


class Callbacks(Enum):
    stress_period = 0
    timestep = 1
    iteration = 2


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
    sim = Simulation(mf6)

    has_converged = False
    prev_time = 0
    current_time = mf6.get_current_time()
    end_time = mf6.get_end_time()
    kperold = [0 for _ in range(sim.subcomponent_count)]

    # todo: setup sim level callback?

    while current_time < end_time:
        dt = mf6.get_time_step()
        mf6.prepare_time_step(dt)

        if verbose:
            print(
                f"Solving: Stress Period {sim.kper + 1}; "
                f"Timestep {sim.kstp + 1}"
            )

        # question: can multiple models have the same solution id???
        #   and therefore we need to also iterate over subcomponents???
        for sol_id, maxiter in sim.solutions.items():
            for model in sim.models:
                if sol_id == model.solution_id:
                    break

            if sim.kper != kperold[sol_id - 1]:
                kperold[sol_id - 1] += 1
                callback(model, Callbacks.stress_period)
            elif current_time == 0:
                callback(model, Callbacks.stress_period)

            mf6.prepare_solve(sol_id)
            kiter = 0
            callback(model, Callbacks.timestep)

            while kiter < maxiter:
                callback(model, Callbacks.iteration)
                has_converged = mf6.solve(sol_id)
                kiter += 1
                if has_converged:
                    break

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
