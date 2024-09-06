Here's an updated README with the description and image included:

```markdown
# TaC
**Thieves and Citizens**

![behaviour](https://github.com/viktorvesely/TaC/blob/main/tac.png?raw=True)

## Description

TaC is a strategic game simulation where two groups, Thieves and Citizens, interact within a defined environment. The objective is to study and observe the behavior patterns of these groups as they compete for resources and survival. The simulation showcases complex behaviors through different strategies and interactions between the two groups.

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

### Running the Project

1. Activate the virtual environment:
   ```bash
   poetry shell
   ```

2. Run the project:
   ```bash
   python <main-script>.py
   ```
   Replace `<main-script>.py` with the name of the main script or entry point for your project.

### Adding Dependencies

To add new dependencies to the project, use the following command:
```bash
poetry add <package-name>
```

### Updating Dependencies

If you need to update the dependencies:
```bash
poetry update
```

This README now includes the project description, the image, and the setup instructions for Poetry. You can adjust the `<repository-url>` and `<main-script>.py` as needed for your specific project.