# Flutter Review and Analysis

Use this when reviewing a Flutter app or analyzing a change. Report concrete
file/widget names, not generic advice.

## Analyzer first

- `flutter analyze` (or Dart MCP `analyze_files`) must be clean for files you
  touched. Do not leave info/warning debt you introduced.
- Honor `analysis_options.yaml`. Do not disable rules to make a change pass.

## Correctness

- Do not use a `BuildContext` across an async gap unless `mounted` (or the
  equivalent ref/context check) is verified after the await.
- Dispose `AnimationController`, `TextEditingController`, `FocusNode`,
  `ScrollController`, `StreamSubscription`, and similar tickers you create.
- `setState` / notify only after the widget is still mounted.
- List children that reorder or change identity need `Key`s.
- `const` constructors where the widget subtree is compile-time constant.

## Rebuilds and performance

- Keep `build` cheap. Extract stable subtrees. Do not do I/O or heavy work
  in `build`.
- Scope rebuilds: watch/select only the fields the widget needs. Do not
  rebuild a large page because a leaf value changed.
- Images, fonts, and assets must be declared in `pubspec.yaml`.

## Architecture fit

- Follow the state-management library already in `pubspec.yaml`. Do not add
  a second one (no Bloc in a Riverpod app, and the reverse).
- Keep widgets presentational when logic already lives in a notifier/bloc/
  controller. Do not dump new business rules into `build`.
- Platform channels, flavors, and dart-defines: match existing naming and
  entrypoints (`main_dev.dart`, `--flavor`, etc.).

## Tests

- Widget tests for UI behavior you change; unit tests for logic.
- Name tests `subject_under_test__in_situation__does_thing` unless this repo
  already uses a different convention — then match the repo.
- If golden tests exist, update them only when the visual change is
  intentional, and say so.

## Shipping hygiene

- No `print` in production paths. Use the project's logger.
- Do not commit `*.g.dart` / `*.freezed.dart` inconsistencies. If you change
  an annotated type, regenerate.
- Secrets stay out of source. Use `--dart-define`, flavor config, or the
  project's existing secret path.
