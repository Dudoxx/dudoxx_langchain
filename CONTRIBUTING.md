# Contributing to Dudoxx Extraction

Thank you for your interest in contributing to the Dudoxx Extraction project! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Contributing to Dudoxx Extraction](#contributing-to-dudoxx-extraction)
  - [Table of Contents](#table-of-contents)
  - [Code of Conduct](#code-of-conduct)
  - [Getting Started](#getting-started)
  - [Development Environment](#development-environment)
  - [Branching Strategy](#branching-strategy)
  - [Commit Guidelines](#commit-guidelines)
  - [Pull Request Process](#pull-request-process)
  - [Testing Guidelines](#testing-guidelines)
  - [Documentation Guidelines](#documentation-guidelines)
  - [Code Style](#code-style)
  - [Issue Reporting](#issue-reporting)
  - [Feature Requests](#feature-requests)
  - [Community](#community)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

1. **Fork the repository**: Click the "Fork" button at the top right of the repository page.
2. **Clone your fork**: 
   ```bash
   git clone https://github.com/yourusername/dudoxx-extraction.git
   cd dudoxx-extraction
   ```
3. **Set up the upstream remote**:
   ```bash
   git remote add upstream https://github.com/originalowner/dudoxx-extraction.git
   ```
4. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Development Environment

We recommend using the following tools for development:

- **Python**: Version 3.9 or higher
- **IDE**: Visual Studio Code with Python extensions
- **Linters**: flake8, black, isort
- **Testing**: pytest

## Branching Strategy

We follow a simplified Git flow:

- **main**: The main branch contains the latest stable release.
- **develop**: The development branch contains the latest development changes.
- **feature/\***: Feature branches should be created from develop and merged back into develop.
- **bugfix/\***: Bugfix branches should be created from develop and merged back into develop.
- **release/\***: Release branches are created from develop when preparing a new release.

## Commit Guidelines

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code (white-space, formatting, etc.)
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools and libraries

Example:
```
feat(extraction-pipeline): add support for PDF files
```

## Pull Request Process

1. **Create a branch**: Create a branch from develop for your changes.
2. **Make changes**: Make your changes in the branch.
3. **Run tests**: Ensure that all tests pass.
4. **Update documentation**: Update the documentation to reflect your changes.
5. **Create a pull request**: Create a pull request from your branch to develop.
6. **Code review**: Wait for code review and address any feedback.
7. **Merge**: Once approved, your pull request will be merged.

## Testing Guidelines

- All new features should include tests.
- All bug fixes should include tests that reproduce the bug.
- Run the test suite before submitting a pull request:
  ```bash
  pytest
  ```
- Aim for high test coverage, especially for critical components.

## Documentation Guidelines

- Update the documentation to reflect your changes.
- Use clear and concise language.
- Include code examples where appropriate.
- Follow the existing documentation style.
- Update the README.md if necessary.

## Code Style

We follow the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code. Additionally:

- Use type hints where appropriate.
- Use docstrings for all functions, classes, and modules.
- Use meaningful variable and function names.
- Keep functions and methods small and focused.
- Use black for code formatting:
  ```bash
  black .
  ```
- Use isort for import sorting:
  ```bash
  isort .
  ```
- Use flake8 for linting:
  ```bash
  flake8
  ```

## Issue Reporting

When reporting issues, please include:

- A clear and descriptive title
- A detailed description of the issue
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots or code snippets if applicable
- Environment information (OS, Python version, etc.)

## Feature Requests

When requesting features, please include:

- A clear and descriptive title
- A detailed description of the feature
- Use cases for the feature
- Any relevant examples or mockups
- How the feature aligns with the project's goals

## Community

- **Discussions**: Use the GitHub Discussions tab for general questions and discussions.
- **Issues**: Use GitHub Issues for bug reports and feature requests.
- **Pull Requests**: Use GitHub Pull Requests for code contributions.

Thank you for contributing to the Dudoxx Extraction project!
