# Project Overview

Fill this in for the consuming repository. Agents load it after `tikal.yaml`.

- **Project Name:** <Project Name>
- **Description:** <Purpose and functionality>
- **Target Runtime/Language:** <e.g. Flutter 3.24 / Dart 3.5>

## Build System and Development Commands

### Basic Build/Install Process
```bash
# Install dependencies and generate code, for example:
flutter pub get
dart run build_runner build --delete-conflicting-outputs
```

### Common Development Tasks
- `Run Tests`: <e.g. flutter test>
- `Run App`: <e.g. flutter run>
- `Analyze`: <e.g. flutter analyze>
- `Format`: <e.g. dart format .>

### Testing Individual Components
- <e.g. flutter test test/widget_test.dart>

## Repository Structure

### Core Directories
- **lib/** - Application source
- **test/** - Unit and widget tests
- **integration_test/** - Device/integration tests (if present)

### Configuration Files
- **pubspec.yaml** - Dart/Flutter dependencies and assets
- **analysis_options.yaml** - Analyzer and linter rules

## Architecture Overview

### Key Components / Flow
- **State management:** <e.g. Riverpod, Bloc, ChangeNotifier — use what is already here>
- **Navigation:** <e.g. go_router>
- **Data / APIs:** <how the app talks to backends or local storage>

## Development Guidelines

- Match existing patterns in this repo. Do not introduce a second state-management library.
- All changes must pass `flutter analyze` and the test suite.
