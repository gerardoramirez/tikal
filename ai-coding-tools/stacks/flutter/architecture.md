# Flutter Architecture

Prefer the layout this repo already uses. Do not flatten or re-layer a
feature to match a diagram here.

Two layouts you will see. Copy the one already in `lib/features/` (or
the repo's modules root):

```
# Flat — screens and state together
lib/features/<name>/

# Layered — keep the existing layer names and import rules
lib/features/<name>/
  domain/          # entities, interfaces; often pure Dart
  data/            # repositories, local store, remote clients
  presentation/    # widgets and screen-local state
```

If a feature already keeps Flutter and Firebase out of `domain/`, do not
import them there.

## Boundaries

- **UI** (`*Page`, `*View`, widgets) renders state and dispatches events.
- **State** (ValueNotifier, ChangeNotifier, `setState`, cubit, bloc,
  Riverpod notifier, or a singleton module already in the app) owns
  mutations. I/O stays out of `build`.
- **Data** (repository, API client, local store) is the only layer that
  talks to the network or disk.

Do not invent a new folder taxonomy for a small change. Put a new feature
in its own directory under the existing features/modules root.

## State and navigation

- One state-management style per app. Read `tikal.project.md`, a nearby
  feature, and `pubspec.yaml`. Many apps have **no** state package in
  pubspec — they use `ValueNotifier`, `ChangeNotifier`, `setState`, or a
  singleton DataModule. Match that. Do not add Bloc, Riverpod, or Provider
  because this doc mentioned them.
- Navigation stays on the existing router (go_router, Navigator 2.0,
  auto_route, etc.). Do not mix in a second routing package.
- Inject dependencies the way neighboring features do (constructor,
  inherited singleton, get_it, Riverpod). Do not introduce a new locator.

## Persistence

If `tikal.project.md` (or the feature) is offline-first: write local
storage first, return control to the UI, then sync remotely without
blocking the user action. Do not await the network on the save path
unless this repo already does that on purpose. Honor any existing sync
coordinator or lifecycle hook — do not invent a second queue.

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
