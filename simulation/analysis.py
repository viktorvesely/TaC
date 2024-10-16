import numpy as np
import pandas as pd
from pathlib import Path
import re
import json
from scipy.stats import ttest_ind, mannwhitneyu

from matplotlib import pyplot as plt
from matplotlib.colors import TwoSlopeNorm

THEFT_DF = "TheftEvent.parquet"
regex = r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})_(\d{5})"

def plot_2d_grid(grid, xlabel: str, ylabel: str, vmax: float=None, vmin=None, cmap: str = "coolwarm"):

    rows = sorted(set(key[0] for key in grid.keys()))

    case_1d = False
    try:
        columns = sorted(set(key[1] for key in grid.keys()))
    except IndexError:
        case_1d = True
        columns = [None]


    matrix = np.zeros((len(rows), len(columns)))

    # Populate the matrix with values from the dictionary
    for i, row in enumerate(rows):
        for j, col in enumerate(columns):
            metric = grid[(row, col)] if not case_1d else grid[(row,)]
            matrix[i, j] = metric

    # Plotting the matrix using subplots
    cmap = plt.get_cmap(cmap)
    print(np.max(matrix))
    norm = TwoSlopeNorm(vmin=(vmin or 0.0), vcenter=0.05, vmax=(vmax or np.max(matrix)))

    fig, ax = plt.subplots()
    cax = ax.matshow(matrix, cmap=cmap, norm=norm)
    fig.colorbar(cax)

    # Set axis labels
    ax.set_xticks(np.arange(len(columns)))
    ax.set_xticklabels(columns)
    ax.set_yticks(np.arange(len(rows)))
    ax.set_yticklabels(rows)

    ax.set_xlabel(xlabel, fontsize=12)
    ax.xaxis.set_label_position('top') 
    ax.set_ylabel(ylabel, fontsize=12)

    plt.show()

    return fig

def load_experiments_by_name(
        name: str,
        dataframes: tuple[str, ...] = (THEFT_DF, ),
        attach_config_vars: tuple[str, ...] = ("generation_empty_w", "n_thieves", "end_t")
    ) -> dict[str, pd.DataFrame]:

    folder = Path(__file__).parent / "data" / "experiments"
    dfs = {dfname: [] for dfname in dataframes}

    for ent in (folder / name).iterdir():

        if not ent.is_dir():
            continue

        res = re.match(regex, ent.name)
        
        if res is None:
            continue

        dstr, randstr = res.group(1), res.group(2)

        if not (ent / "config.json").is_file():
            continue

        with open(ent / "config.json", "r", encoding="utf-8") as f:
            config = json.load(f)
        
        skip_log = not all([(ent / dfname).is_file() for dfname in dataframes])
    
        if skip_log:
            continue

        for dfname in dataframes:
            df = pd.read_parquet(ent / dfname) 
            df["rand"]= ent.name
            
            for av in attach_config_vars:
                df[av] = config[av]
            
            dfs[dfname].append(df)
    
    dfs = {dfname: pd.concat(inners, ignore_index=True) for dfname, inners in dfs.items()}

    return dfs


def take_any(s: pd.Series):

    if (unique := s.unique()).size != 1:
        raise ValueError(f"Heterogenous or empty {s.name}")
        
    return unique[0]

def succ_normalized_thefts(theft_df: pd.DataFrame) -> pd.DataFrame:
    
    n_thieves = take_any(theft_df["n_thieves"])
    end_t = take_any(theft_df["end_t"])

    conditions = theft_df.groupby(["rand", "generation_empty_w"])["caught"].value_counts()
    conditions = conditions.reset_index()
    conditions = conditions[~conditions["caught"]]
    conditions["count"] = conditions["count"] / (n_thieves * end_t)

    return conditions


def t_test_h1(theft_df: pd.DataFrame) -> float:

    experiments_condition = succ_normalized_thefts(theft_df)
    
    densities = np.sort(experiments_condition["generation_empty_w"].unique())
    assert densities.size == 2
    value_high_sparsity = densities[-1]
    value_low_sparsity = densities[0]
    
    sample_high_sparsity = experiments_condition.loc[experiments_condition["generation_empty_w"] == value_high_sparsity, "count"]
    sample_low_sparsity = experiments_condition.loc[experiments_condition["generation_empty_w"] == value_low_sparsity, "count"]
    results = ttest_ind(sample_low_sparsity, sample_high_sparsity, equal_var=False, alternative="greater")

    return results.pvalue

def mannwhitneyu_test_h1(theft_df: pd.DataFrame) -> float:

    experiments_condition = succ_normalized_thefts(theft_df)
    
    densities = np.sort(experiments_condition["generation_empty_w"].unique())
    assert densities.size == 2
    value_high_sparsity = densities[-1]
    value_low_sparsity = densities[0]
    
    sample_high_sparsity = experiments_condition.loc[experiments_condition["generation_empty_w"] == value_high_sparsity, "count"]
    sample_low_sparsity = experiments_condition.loc[experiments_condition["generation_empty_w"] == value_low_sparsity, "count"]
    results = mannwhitneyu(sample_low_sparsity, sample_high_sparsity, alternative="greater")

    return results.pvalue