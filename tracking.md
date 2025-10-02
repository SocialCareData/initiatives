# Extending this list to support tracking engagement and alignment

Initially, this is a simple list to record initiatives with potentially overlapping scopes to support strategic alignment and interoperability.

By using issue templates and automation in GitHub, this could be extended to manage and monitor engagements and interactions.

Suggested fields:
- slug: Unique kebab-case ID for the initiative (used as the key), e.g., city-open-schema.
- name: Full official name of the initiative.
- acronym: Short code or abbreviation (optional).
- owner_org: Organisation that owns or stewards the initiative.
- governance_body: Committee/WG overseeing it (optional).
- homepage_url: Public landing page for the initiative (URL).
- spec_repo_url: Repository for specs/code (URL), if applicable.
- scope_domains: Topical domains/tags; semicolon-separated (e.g., health;terminology).
- geographies: Jurisdictions/regions covered; semicolon-separated (e.g., global;UK).
- standard_types: Type(s) of standard; semicolon-separated (data-model;schema;api;vocabulary).
- stage: Lifecycle status (enum: planning|draft|active|deprecated).
- license: License covering the spec/data model (e.g., CC BY 4.0, Apache-2.0).
- known_adopters: Public adopters/implementers; semicolon-separated (optional).
- overlaps_with: Slugs of related/overlapping initiatives; semicolon-separated (optional).
- dependencies: Slugs of prerequisite standards; semicolon-separated (optional).
- interoperability_notes: Brief notes on mappings/alignments (public-safe).

Additions for tracking:
- engagement_status: Current relationship (enum: not-contacted|outreach-sent|in-conversation|collaborating|paused|no-response|not-pursuing).
- priority: Importance for your team (enum: high|medium|low).
- internal_lead: GitHub handle/team responsible (no personal contact details).
- last_interaction_date: Date of last meaningful interaction (YYYY-MM-DD).
- last_interaction_summary: One-line public-safe summary of the last interaction.
- next_milestone: Next planned step or decision (short).
- next_milestone_date: Target date for the next milestone (YYYY-MM-DD).
- tracking_issue_url: Link to the GitHub issue tracking this initiative (URL).
- last_updated_date: When this row was last edited (YYYY-MM-DD).
- last_updated_by: GitHub handle of the editor who made the last change.
