# TaC
**Thieves and Citizens**

## Description

TaC is an Agent Based Model simulation where two groups, Thieves and Citizens, interact within an environment.

## Prerequisites

### Common Requirements
- **Python**: Ensure Python is installed on your system. Download it [here](https://www.python.org/downloads/).

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

1. **Activate the virtual environment:**
   (if using a virtual environment manager, activate it here)

2. **Run the project:**
   ```bash
   python -m simulation.main
   ```
