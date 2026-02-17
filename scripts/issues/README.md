# Issue scripts

Small, focused shell helpers for issue reporting using `mdix | jq`.

## Usage

Run from the repository root:

```bash
scripts/issues/status-counts.sh
scripts/issues/type-counts.sh
scripts/issues/epic-rollup.sh
scripts/issues/non-done.sh
```

Each script accepts an optional issue root path (default: `plan/issues`):

```bash
scripts/issues/status-counts.sh plan/issues
```

## Scripts

- `status-counts.sh` - Count issues by `status`
- `type-counts.sh` - Count issues by `type`
- `epic-rollup.sh` - Show epics with child counts and child status rollups
- `non-done.sh` - List issues where status is not `done`
