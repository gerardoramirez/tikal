# Flutter Commands

Prefer the repo's existing toolchain. If `.fvm/` or `.fvmrc` exists, prefix
commands with `fvm` (e.g. `fvm flutter test`). If `melos.yaml` exists, use
Melos for the affected package.

```bash
flutter pub get
dart format .
flutter analyze
flutter test
flutter test test/path/to_test.dart
flutter test --coverage
flutter run
```

Code generation — run **only** if the repo already has `build_runner`
(or a similar generator) and you changed an annotated type. Skip this
when serialization is handwritten.

```bash
dart run build_runner build --delete-conflicting-outputs
```

Do not add new dependencies, linter rules, or code-gen packages unless the
user asks. After Dart/Flutter edits, run `flutter analyze` and the tests that
cover the change before calling the work done.

If browser or device UI verification is required, exercise the changed flow
in a running app (`flutter run` or the Dart MCP driver) — a static read of
the widget tree is not enough.
