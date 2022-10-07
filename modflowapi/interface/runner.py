from .. import ModflowApi
from .simulation import Simulation
from .model import Model


def run_model(dll, sim_path, callback=None):
    mf6 = ModflowApi(
        dll,
        working_directory=sim_path,
    )

    mf6.initialize()
    sim = Simulation(mf6)

    has_converged = False
    prev_time = 0
    current_time = mf6.get_current_time()
    end_time = mf6.get_end_time()
    kperold = [0 for _ in range(sim.subcomponent_count)]

    # todo: setup callback

    while current_time < end_time:
        delt = current_time - prev_time
        dt = mf6.get_time_step()
        mf6.prepare_time_step(dt)

        for sol_id, maxiter in sim.solutions.items():
            if sim.kper != kperold[sol_id - 1]:
                kperold[sol_id - 1] += 1
                # todo: stress period callback

            mf6.prepare_solve(sol_id)
            kiter = 0
            # todo: callback: timestep callback

            while kiter < maxiter:
                # todo: iteration callback

                has_converged = mf6.solve(sol_id)
                kiter += 1
                if has_converged:
                    break

            mf6.finalize_solve(sol_id)

        mf6.finalize_time_step()
        prev_time = current_time
        current_time = mf6.get_current_time()

        if not has_converged:
            print("MODEL DID NOT CONVERGE")

    try:
        mf6.finalize()
    except:
        raise RuntimeError("MF6 simulation failed, check listing file")

    print("SUCCESSFUL TERMINATION OF PROGRAM")


