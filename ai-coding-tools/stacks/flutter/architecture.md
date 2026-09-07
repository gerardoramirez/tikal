# Flutter Architecture

Prefer the layout this repo already uses. Typical Flutter apps in this
pipeline look like:

```
lib/
  main.dart                 # or flavor entrypoints
  app.dart                  # MaterialApp / theme / router
  features/<name>/          # screens, widgets, and feature state together
  shared/                   # theme, widgets, utilities used by 2+ features
test/
  features/<name>/
```

## Boundaries

- **UI** (`*Page`, `*View`, widgets) renders state and dispatches events.
- **State** (notifier, bloc, cubit, controller) owns mutations and I/O.
- **Data** (repository, API client, local store) is the only layer that
  talks to the network or disk.

Do not invent a new folder taxonomy for a small change. Put a new feature
in its own directory under the existing features/modules root.

## State and navigation

- One state-management style per app. Read `pubspec.yaml` and nearby
  features before choosing an approach.
- Navigation stays on the existing router (go_router, Navigator 2.0,
  auto_route, etc.). Do not mix in a second routing package.
- Inject dependencies the way neighboring features do (constructor, Riverpod
  providers, get_it). Do not introduce a new locator.

## Theming and platforms

- Use the existing `ThemeData` / text styles / color tokens. Do not hard-code
  a parallel palette.
- Android, iOS, and any enabled desktop/web targets in `pubspec.yaml` or
  platform folders stay in mind: safe areas, back gesture, and plugins that
  are mobile-only.

## When analyzing an unfamiliar Flutter repo

1. Read `pubspec.yaml` and `tikal.project.md`.
2. Skim `lib/main.dart` (or flavor mains) and the router.
3. Open one complete existing feature and copy its shape.
4. Then change code.
