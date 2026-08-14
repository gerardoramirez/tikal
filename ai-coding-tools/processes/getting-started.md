# General Info about this Repo

This file provides guidance to Claude Code (claude.ai/code) and other AI coding assistants when working with code in this repository.

## Project Overview

Provide a brief overview of the project here:
- **Project Name:** <Project Name>
- **Description:** <Description of the project's purpose and functionality>
- **Target Runtime/Language:** <e.g., Python 3.12+, Node.js 20+, Rust, Go, etc.>

## Build System and Development Commands

### Basic Build/Install Process
```bash
# Provide the commands to install dependencies and build the project, for example:
npm install
npm run build
# or
pip install -r requirements.txt
# or
cargo build
```

### Common Development Tasks
- `Run Tests`: <Command to run the test suite, e.g., npm test, pytest, cargo test>
- `Run App/Server`: <Command to start the application locally, e.g., npm run dev, python main.py>
- `Clean Build`: <Command to clean build artifacts, e.g., npm run clean, cargo clean>

### Testing Individual Components
- <Explain how to run specific tests or single test files, e.g., pytest tests/test_module.py or npm test -- -t "some test">

## Repository Structure

### Core Directories
- **src/** - Core application source code
- **tests/** - Unit and integration tests
- **scripts/** - Utility and automation scripts

### Configuration Files
- **<config_file_1>** - <e.g., package.json, Cargo.toml, pyproject.toml>
- **<config_file_2>** - <e.g., tsconfig.json, vite.config.ts, .gitignore>

## Code Quality and Linting

### Primary Linting & Formatting Tools
- **<Linter/Formatter Name>** - <e.g., Prettier, ESLint, Ruff, ClangFormat>
- Configuration in `<config_file>` (e.g., `.prettierrc`, `eslint.config.js`, `.ruff.toml`)

### Linting/Formatting Commands
```bash
# Provide commands to lint and format the codebase:
npm run lint
npm run format
# or
ruff check .
ruff format .
```

## Architecture Overview

### Key Components / Flow
- **Data Flow/Pipeline**: <Describe the core pipeline, request life cycle, or data flow>
- **Database/Storage**: <Describe database system, ORM, or data layer if applicable>
- **API/Interfaces**: <Describe REST, GraphQL, gRPC, or CLI interfaces>

## Development Guidelines

### Testing Requirements
- All changes must pass the test suite.
- Write tests for any new functionality or bug fixes.
- Place tests in the standard tests directory.

### Code Style & Conventions
- Preferred coding conventions: <e.g., Airbnb style guide, PEP 8, idiomatic Go>
- Line length limit: <e.g., 80, 100, 120 characters>
- Give each new function, class, and module clear docstrings/comments.

### Interacting with Me (User Persona/Instructions)
- <Optional: Define instructions for how the AI should communicate with you, e.g., "I am navigating this codebase as a senior developer. Be direct and avoid excessive polite filler. Prefer showing code over explanation.">
