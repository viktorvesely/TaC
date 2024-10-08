from multiprocessing import Pool
from dataclasses import replace

from .state import Vars
from .main import experiment_simulation

def boot_experiment(config: Vars):
    experiment_simulation(config, desired_t_s=150)


def vary(source: Vars, name: str, values: list, variations: int) -> list[Vars]:

    out = []
    for value in values:
        for _ in range(variations):
            out.append(replace(source, **{name: value}))

    return out

if __name__ == "__main__":

    import tqdm
    import numpy as np


    source = Vars(experiment_name="r_increased_look_cooldown")
    configs = vary(
        source,
        name="generation_empty_w",
        values=np.linspace(1, 80, num=2, endpoint=True),
        variations=60
    )


    with Pool(8) as p, tqdm.tqdm(total=len(configs), disable=False) as pbar:
        try:
            for _ in p.imap_unordered(boot_experiment, configs):
                pbar.update()
        except KeyboardInterrupt:
            ...
