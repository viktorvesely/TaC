# TaC
**Thieves and Citizens**

![Behavior](https://github.com/viktorvesely/TaC/blob/main/tac_flow_chart_v1.2.png?raw=True)

## Description

TaC is a strategic game simulation where two groups, Thieves and Citizens, interact within an environment.

## Prerequisites

### Common Requirements
- **Python**: Ensure Python is installed on your system. Download it [here](https://www.python.org/downloads/).

If you prefer to use a different dependency manager, you can find the required packages for this project in the `pyproject.toml` file and install them using pip or your preferred package manager.

### Poetry Setup
This project uses [Poetry](https://python-poetry.org/) for dependency management. 

#### Linux-Based Systems
To install Poetry on Linux, run the following command:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

#### Windows
For Windows users, you can install Poetry by following the instructions on the official [Poetry installation page](https://python-poetry.org/docs/#installation).

## Setting Up the Project

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Install the project dependencies with Poetry:**
   ```bash
   poetry install
   ```
   This command will automatically create a virtual environment and install all dependencies listed in the `pyproject.toml` file.

3. **Compile the Cython files:**
   ```bash
   # Navigate to the Cython files and compile them
   cd simulation/world/c_vision
   python compile_vision build_ext --inplace
   
   cd ../c_collision
   python compile_collisions build_ext --inplace
   ```

## Running the Project

1. **Activate the virtual environment:**
   ```bash
   poetry shell
   ```

2. **Run the project:**
   ```bash
   python -m simulation.main
   ```
```
