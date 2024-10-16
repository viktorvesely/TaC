from multiprocessing import Pool
from dataclasses import replace

from .state import Vars
from .main import experiment_simulation
from .analysis import load_experiments_by_name, THEFT_DF, plot_2d_grid, t_test_h1

from .utils import Utils

def boot_experiment(config: Vars):
    experiment_simulation(config)


def vary(source: Vars, name: str, values: list, variations: int) -> list[Vars]:

    out = []
    for value in values:
        for _ in range(variations):
            out.append(replace(source, **{name: value}))

    return out

def experiment(
        experiment_name: str,
        source: Vars | None = None,
        simulation_time_s: float = 150,
        sparsities: tuple[float, ...] = (1, 80),
        variations: int = 100
    ):

    import tqdm

    source = source if source is not None else Vars()

    source.experiment_name = experiment_name
    source.end_t = simulation_time_s * 1_000

    configs = vary(
        source,
        name="generation_empty_w",
        values=sparsities,
        variations=variations
    )

    with Pool(8) as p, tqdm.tqdm(total=len(configs), disable=False) as pbar:
        try:
            for _ in p.imap_unordered(boot_experiment, configs):
                pbar.update()
        except KeyboardInterrupt:
            return False
        
    return True

def test_for_different_motivation_weights(base_name: str):
    
    import pickle
    import numpy as np
    from itertools import product

    vision_weights = np.linspace(0, 1, num=5, endpoint=True)
    frustration_weights = np.linspace(0, 1, num=5, endpoint=True)
    n_all = vision_weights.size * frustration_weights.size

    source = Vars()
    grid = dict()

    path = Utils.experiments_path().parent / "tests" / f"{base_name}.pkl"
    folder = path.parent
    if not folder.is_dir():
        folder.mkdir(parents=True)

    for i, (vision_w, frustration_w) in enumerate(product(vision_weights, frustration_weights)):
        exp_name = f"{base_name}_{i}"
        modified = replace(source, frustration_weight=frustration_w, vision_weight=vision_w)
        keep_going = experiment(exp_name, source=modified, simulation_time_s=120)
        if not keep_going:
            break
        dfs = load_experiments_by_name(exp_name)
        theft_df = dfs[THEFT_DF]
        p_value = t_test_h1(theft_df)
        grid[(vision_w, frustration_w)] = p_value

        print(f" {(i + 1)} / {n_all}")

    with open(path, "wb") as f:
        pickle.dump(grid, f)

    plot_2d_grid(grid, xlabel="frustration", ylabel="vision")
        

if __name__ == "__main__":
    # test_for_different_motivation_weights("weights_120s_100v")

    experiment("test_new", variations=20)
    
    
