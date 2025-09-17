#!/usr/bin/env python3
import os, sys, re, csv, json
from datetime import date

# CSV headers (must match your CSV schema)
HEADERS = [
  "slug","name","acronym","owner_org","governance_body","homepage_url","spec_repo_url",
  "scope_domains","geographies","standard_types","stage","license","known_adopters",
  "overlaps_with","dependencies","interoperability_notes",
  "engagement_status","priority","internal_lead",
  "last_interaction_date","last_interaction_summary","next_milestone","next_milestone_date",
  "tracking_issue_url","last_updated_date","last_updated_by"
]

# Fields expected from the issue form
FORM_FIELDS = {
  "slug","name","acronym","owner_org","governance_body","homepage_url","spec_repo_url",
  "scope_domains","geographies","standard_types","stage","license","known_adopters",
  "overlaps_with","dependencies","interoperability_notes"
}

def parse_issue_from_event():
  event_path = os.environ.get("GITHUB_EVENT_PATH")
  if not event_path or not os.path.exists(event_path):
    print("ERROR: GITHUB_EVENT_PATH not found", file=sys.stderr); sys.exit(1)
  with open(event_path, "r", encoding="utf-8") as f:
    ev = json.load(f)
  issue = ev.get("issue") or {}
  body = issue.get("body") or ""
  issue_url = issue.get("html_url") or ""
  author = (issue.get("user") or {}).get("login") or "unknown"
  return body, issue_url, author

def strip_fences(text):
  t = text.strip()
  t = re.sub(r"^```[a-zA-Z0-9]*\n", "", t)
  t = re.sub(r"\n```$", "", t)
  t = re.sub(r"\s*\n\s*", " ", t).strip()
  return t

def parse_form_fields(md):
  # Matches "### fieldname\nvalue ... (until next ### or end)"
  pattern = re.compile(r"^###\s+([^\n]+)\n+([\s\S]*?)(?=\n###\s+|$)", re.M)
  fields = {}
  for m in pattern.finditer(md):
    label = m.group(1).strip().lower()
    value = strip_fences(m.group(2))
    if label in FORM_FIELDS and value:
      fields[label] = value
  return fields

def load_rows(csv_path):
  if not os.path.exists(csv_path):
    return []
  with open(csv_path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    return [dict(r) for r in reader]

def write_rows(csv_path, rows):
  rows_sorted = sorted(rows, key=lambda r: (r.get("slug") or "").lower())
  with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=HEADERS)
    writer.writeheader()
    for r in rows_sorted:
      writer.writerow({h: r.get(h, "") for h in HEADERS})

def main(csv_path):
  body, issue_url, author = parse_issue_from_event()
  fields = parse_form_fields(body)

  if "slug" not in fields or not fields["slug"].strip():
    print("ERROR: 'slug' is required in the issue form", file=sys.stderr); 
    slug = ""
  else:
    slug = fields["slug"].strip()

  today = date.today().strftime("%Y-%m-%d")

  defaults = {
    "engagement_status": "not-contacted",
    "priority": "medium",
    "internal_lead": "",
    "last_interaction_date": "",
    "last_interaction_summary": "",
    "next_milestone": "",
    "next_milestone_date": "",
    "tracking_issue_url": issue_url,
    "last_updated_date": today,
    "last_updated_by": author
  }

  rows = load_rows(csv_path)
  found = False

  for r in rows:
    if (r.get("slug") or "").strip().lower() == slug.lower():
      for k, v in fields.items():
        r[k] = v
      r["tracking_issue_url"] = issue_url or r.get("tracking_issue_url", "")
      r["last_updated_date"] = today
      r["last_updated_by"] = author
      found = True
      break

  if not found:
    new_row = {h: "" for h in HEADERS}
    new_row.update(defaults)
    for k, v in fields.items():
      new_row[k] = v
    rows.append(new_row)

  write_rows(csv_path, rows)
  print(f"Ingested issue into {csv_path} (slug={slug}, {'updated' if found else 'added'})")

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("Usage: ingest_issue.py data/initiatives.csv", file=sys.stderr); sys.exit(2)
  main(sys.argv[1])
