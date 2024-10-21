# TaC
**Thieves and Citizens**

## Description

TaC is an Agent Based Model simulation where two groups, Thieves and Citizens, interact within an environment.

## Prerequisites

### Common Requirements
- **Python**: Ensure Python 3.12 or higher is installed on your system. Download it [here](https://www.python.org/downloads/).

- **Dependencies**: You can find the required dependecies for this project in the `requirements.txt` file and install them using pip or your preferred package manager.

## Setting Up the Project

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Install the project dependencies:**
   
3. **Compile the Cython files:**
   ```bash
   # Navigate to the Cython files and compile them
   cd simulation/world/c_vision
   python compile_vision build_ext --inplace
   
   cd simulation/world/c_collision
   python compile_collisions build_ext --inplace
   ```

## Running the Project

1. **Run the realtime simulation**
   Navigate to a folder where you can see the `simulation` folder and then run
   ```bash
   python -m simulation.main
   ```

1. **Run the experiment**
   Go to `experiments.py` change the name of the 
   experiment.

   Navigate to a folder where you can see the `simulation` folder and then run
   ```bash
   python -m simulation.experiments
   ```