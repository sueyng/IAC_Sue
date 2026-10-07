#!/usr/bin/env python3
"""Pre-deployment check for the Glacier prefix settings in a v10.1 S3 parameter file.

CloudFormation already rejects a single prefix list that is badly formatted or
repeats a prefix. It cannot compare lists across settings, so run this before
deploying:

    python3 check-glacier-prefixes.py env/parameters-s3bucket.yaml

Errors (exit code 1):
  - prefix list format: up to 5 comma-separated prefixes, no spaces or empty items
  - the same prefix twice in one setting
  - the same prefix in two settings
  - a setting 2 or 3 prefix list while EnableGlacierTransition is not "true"

Warnings (exit code 0):
  - one prefix contains another (e.g. logs/ and logs/app/), so both rules apply
  - setting 1 is empty (whole bucket) while setting 2 or 3 is used
  - a prefix without a trailing slash
  - transition days not lower than the matching expiration days
"""
import re
import sys

SETTINGS = {
    1: ("GlacierTransitionPrefix", "GlacierTransitionDays", "GlacierNoncurrentTransitionDays"),
    2: ("Glacier2TransitionPrefix", "Glacier2TransitionDays", "Glacier2NoncurrentTransitionDays"),
    3: ("Glacier3TransitionPrefix", "Glacier3TransitionDays", "Glacier3NoncurrentTransitionDays"),
}
LIST_FORMAT = re.compile(r"(?:[^,\s]+(?:,[^,\s]+){0,4})?")
LINE = re.compile(r'^\s*([A-Za-z0-9]+)\s*:\s*"([^"]*)"')


def read_params(path):
    params = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if "PARAMETERS_END" in line:
                break
            m = LINE.match(line)
            if m:
                params[m.group(1)] = m.group(2)
    return params


def as_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def main(path):
    p = read_params(path)
    errors, warnings = [], []
    enabled = p.get("EnableGlacierTransition", "false") == "true"

    prefixes = {}  # setting -> list of prefixes
    invalid = set()
    for n, (key, _, _) in SETTINGS.items():
        raw = p.get(key, "")
        if not LIST_FORMAT.fullmatch(raw):
            errors.append(f'{key}: "{raw}" must be up to 5 comma-separated prefixes with no spaces or empty items')
            invalid.add(n)
            continue
        items = raw.split(",") if raw else []
        seen = set()
        for item in items:
            if item in seen:
                errors.append(f'{key}: "{item}" is listed twice')
            seen.add(item)
            if not item.endswith("/"):
                warnings.append(f'{key}: "{item}" has no trailing slash, so it also matches keys like "{item}-old/..."')
        prefixes[n] = sorted(seen)

    for n in (2, 3):
        if prefixes.get(n) and not enabled:
            errors.append(f'{SETTINGS[n][0]} is set but EnableGlacierTransition is not "true"')

    owners = {}
    for n, items in prefixes.items():
        for item in items:
            owners.setdefault(item, []).append(n)
    for item, ns in sorted(owners.items()):
        if len(ns) > 1:
            errors.append(f'"{item}" is in more than one setting ({", ".join(f"setting {n}" for n in ns)})')

    for a in sorted(owners):
        for b in sorted(owners):
            if a != b and b.startswith(a):
                sa = ", ".join(str(n) for n in owners[a])
                sb = ", ".join(str(n) for n in owners[b])
                warnings.append(f'"{b}" (setting {sb}) is inside "{a}" (setting {sa}); both rules apply to "{b}"')

    if enabled and not prefixes.get(1) and (prefixes.get(2) or prefixes.get(3)):
        warnings.append("setting 1 is empty (whole bucket) while setting 2 or 3 is used; "
                        "their prefixes also get setting 1's rule")

    if enabled:
        current_exp = as_int(p.get("S3CurrentVersionExpirationDays")) or (
            as_int(p.get("LifecycleExpirationDays")) if p.get("EnableLifecycle") == "true" else None)
        noncurrent_exp = as_int(p.get("S3NoncurrentVersionExpirationDays")) or (
            as_int(p.get("NoncurrentVersionExpirationDays")) if p.get("EnableNoncurrentVersionExpiration") == "true" else None)
        for n, (key, days_key, nc_key) in SETTINGS.items():
            if n > 1 and not prefixes.get(n):
                continue
            days, nc_days = as_int(p.get(days_key)), as_int(p.get(nc_key))
            if current_exp and days and days >= current_exp:
                warnings.append(f"{days_key} ({days}) is not lower than expiration ({current_exp}); "
                                "objects are deleted before they move")
            if noncurrent_exp and nc_days and nc_days >= noncurrent_exp:
                warnings.append(f"{nc_key} ({nc_days}) is not lower than old-version expiration ({noncurrent_exp}); "
                                "old versions are deleted before they move")

    for n in SETTINGS:
        items = prefixes.get(n)
        if n in invalid:
            label = "(invalid, see errors)"
        else:
            label = ", ".join(items) if items else ("(whole bucket)" if n == 1 else "(not used)")
        print(f"Setting {n}: {label}")
    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    print("Result: " + ("FAILED" if errors else "OK"))
    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
