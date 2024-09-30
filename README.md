# TaC
**Thieves and Citizens**

![behaviour](https://github.com/viktorvesely/TaC/blob/main/tac_flow_chart_v1.2.png?raw=True)

## Description

TaC is a strategic game simulation where two groups, Thieves and Citizens, interact within a  environment.

## Poetry Setup Instructions

This project uses [Poetry](https://python-poetry.org/) for dependency management and packaging. Below are the steps to set up the project using Poetry.

### Prerequisites

- **Python**: Make sure Python is installed. You can download it [here](https://www.python.org/downloads/).
- **Poetry**: Install Poetry by running the following command:
  ```bash
  curl -sSL https://install.python-poetry.org | python3 -
  ```

### Setting Up the Project

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. Install the project dependencies with Poetry:
   ```bash
   poetry install
   ```

   This will automatically create a virtual environment and install all dependencies listed in the `pyproject.toml` file.

3. Compile the cython files

    ```bash
   Go to simulation/world/c_vision
      run python compile_vision build_ext --inplace
   Go to simulation/world/c_collision
      run python compile_collisions build_ext --inplace

   ```
### Running the Project

1. Activate the virtual environment:
   ```bash
   poetry shell
   ```

2. Run the project:
   ```bash
   python -m simulation.main
   ```
