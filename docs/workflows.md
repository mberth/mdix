# mdix workflow patterns

Practical recipes for incremental vault cleanup using `mdix`.
These assume you are comfortable with the basics covered in the [README](../README.md).

## The safe cleanup loop

The recommended pattern for any cleanup pass:

```bash
mdix --root ~/notes schema inventory        # 1) see what's there
mdix --root ~/notes schema validate \
  --include "people/**"                     # 2) scope to one collection
mdix --root ~/notes schema migrate \
  --dry-run --include "people/**"           # 3) preview changes
mdix --root ~/notes schema migrate \
  --include "people/**"                     # 4) apply
mdix --root ~/notes schema validate \
  --include "people/**"                     # 5) confirm clean
```

Both `schema validate` and `schema migrate` report the effective schema source path
in output under `schema`.

## Scoped fm normalize passes

`fm normalize` handles status renaming, default-filling, derived fields, and null key cleanup.
Always dry-run first:

```bash
mdix --root ~/notes fm normalize --dry-run \
  --include "people/**" \
  --map-value status active identified \
  --set-default type person \
  --derive title nickname \
  --remove-null-keys
```

Apply when the preview looks right:

```bash
mdix --root ~/notes fm normalize \
  --include "people/**" \
  --map-value status active identified \
  --set-default type person \
  --derive title nickname \
  --remove-null-keys
```

## Incremental cleanup: mixed-content vault

For vaults with mixed entity types and legacy metadata, work in small scoped passes
and commit after each one:

```bash
# Pass 1: normalize one collection, commit
mdix --root ~/notes fm normalize --dry-run \
  --include "Organisations/**" \
  --map-value status is_identified identified \
  --set-default type organisation \
  --derive title name \
  --remove-null-keys

mdix --root ~/notes fm normalize \
  --include "Organisations/**" \
  --map-value status is_identified identified \
  --set-default type organisation \
  --derive title name \
  --remove-null-keys
# git add + commit

# Pass 2: separate pass for a different concern
mdix --root ~/notes fm normalize \
  --include "People/**" \
  --exclude "People/_TEMPLATE.md" \
  --remove-null-keys
# git add + commit
```

Why this works well:

- Each pass is scoped and reviewable.
- `--dry-run` and apply use the same command shape, reducing operator error.
- Git history stays meaningful: each commit captures one cleanup intention.
- You can re-run `schema validate` between passes to measure progress.

## CI gate

```bash
# Fail CI if any note has frontmatter errors
mdix q --fail-on-errors

# Fail CI if schema has violations
mdix schema validate
```

`schema validate` exits with code `2` on violations in strict mode.
`mdix q --fail-on-errors` emits an error summary to stderr and exits non-zero when
any item has parse errors.
