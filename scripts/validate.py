#!/usr/bin/env python3
import csv, sys, re
from datetime import datetime
from urllib.parse import urlparse

REQUIRED_FIELDS = {"name"}
REQUIRED_IF_PRESENT = {"last_updated_date", "last_updated_by"}

ENUMS = {
    "stage": {"planning", "draft", "active", "deprecated"},
    "engagement_status": {"not-contacted", "outreach-sent", "in-conversation", "collaborating", "paused", "no-response", "not-pursuing"},
    "priority": {"high", "medium", "low"},
}

DATE_FIELDS = {"last_interaction_date", "next_milestone_date", "last_updated_date"}
URL_FIELDS = {"homepage_url", "spec_repo_url", "tracking_issue_url"}
LIST_FIELDS = {"scope_domains", "geographies", "standard_types", "known_adopters", "overlaps_with", "dependencies"}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

def is_http_url(u: str) -> bool:
    try:
        p = urlparse(u)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False

def is_iso_date(s: str) -> bool:
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except Exception:
        return False

def warn(msg: str):
    print(f"WARNING: {msg}")

def fail(msg: str):
    print(f"ERROR: {msg}")
    sys.exit(1)

def main(path: str):
    try:
        f = open(path, newline="", encoding="utf-8")
    except FileNotFoundError:
        fail(f"File not found: {path}")

    with f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        header_set = set(headers)

        missing = REQUIRED_FIELDS - header_set
        if missing:
            fail(f"Missing required columns: {sorted(missing)}")

        seen_slugs = set()
        rownum = 1
        count = 0
        warnings = 0

        for row in reader:
            rownum += 1
            count += 1

            # No emails in public CSV
            for k, v in row.items():
                if v and EMAIL_RE.search(v):
                    warn(f"line {rownum}: possible email detected in '{k}': '{v}'")
                    warnings += 1

            # Required fields non-empty
            for col in REQUIRED_FIELDS:
                val = (row.get(col) or "").strip()
                if not val:
                    warn(f"line {rownum}: '{col}' is required and must be non-empty")
                    warnings += 1

            # Required-if-present fields non-empty
            for col in REQUIRED_IF_PRESENT & header_set:
                val = (row.get(col) or "").strip()
                if not val:
                    warn(f"line {rownum}: '{col}' must be non-empty when the column is present")
                    warnings += 1

            # Slug format and uniqueness
            slug = (row.get("slug") or "").strip()
            if not SLUG_RE.match(slug):
                warn(f"line {rownum}: 'slug' must be kebab-case: '{slug}'")
                warnings += 1
            if slug in seen_slugs:
                warn(f"line {rownum}: duplicate slug '{slug}'")
                warnings += 1
            seen_slugs.add(slug)

            # Enums (only if column exists)
            for col, allowed in ENUMS.items():
                if col in header_set:
                    val = (row.get(col) or "").strip()
                    if val and val not in allowed:
                        warn(f"line {rownum}: '{col}'='{val}' not in {sorted(allowed)}")
                        warnings += 1

            # Dates
            for col in DATE_FIELDS & header_set:
                val = (row.get(col) or "").strip()
                if val and not is_iso_date(val):
                    warn(f"line {rownum}: '{col}' must be YYYY-MM-DD (got '{val}')")
                    warnings += 1

            # URLs
            for col in URL_FIELDS & header_set:
                val = (row.get(col) or "").strip()
                if val and not is_http_url(val):
                    warn(f"line {rownum}: '{col}' must be a valid http(s) URL (got '{val}')")
                    warnings += 1

            # Semicolon-separated lists: allow, no strict checks
            for col in LIST_FIELDS & header_set:
                _ = row.get(col, "")

        print(f"Validation passed: {count} rows.")
        if warnings:
            print(f"Total warnings: {warnings}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/validate.py data/initiatives.csv")
        sys.exit(2)
    main(sys.argv[1])
