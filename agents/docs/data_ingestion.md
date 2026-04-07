# Data Ingestion & Validation Workflow

This reference describes the workflow for preparing weekly GTA Online data using the repository's canonical schema v2.

## Purpose

- Define the shared workflow for `Pavel` and `Vincent`
- Document the expected input shape, normalization rules, and validation checkpoints
- Ensure analysis agents receive clean, consistent weekly payloads

## Roles

### Pavel: Weekly Data Curator

- Ingests raw weekly activity notes, web-scraped content, or semi-structured JSON
- Normalizes data into the canonical `schema_v2` payload shape
- Preserves intent and weekly goals while standardizing field names and values
- Reports missing fields and recommends explicit corrections

### Vincent: Schema Validation Specialist

- Validates the candidate `schema_v2` payload produced by Pavel
- Detects missing required sections, invalid types, and malformed structure
- Provides exact corrections for each issue
- Ensures the payload is ready for downstream analysis agents

## Workflow

1. **Source data collection**
   - Raw data is collected from websites, notes, or manual entry
   - Source should be tagged using `data_quality.source`

2. **Pavel normalization**
   - Convert raw content to canonical `schema_v2` format
   - Use `agents/weekly_input_template.md` and `data/schema_v2_example.json` as references
   - Output a candidate payload and a missing field checklist

3. **Vincent validation**
   - Validate the candidate payload against the canonical schema
   - Flag errors and warnings that prevent reliable analysis
   - If issues remain, return the payload to Pavel for correction

4. **Analysis consumption**
   - Once Vincent approves the payload, analysis agents (Michael, Franklin, Trevor, Agent 14, Tony, Lamar, Ron, Lester) can consume it
   - Any subsequent data ingestion should follow the same cycle

## Canonical References

- `agents/weekly_input_template.md`
- `data/schema_v2_example.json`
- `agents/docs/data_ingestion.md`

## Recommended Fields

At minimum, a clean schema v2 payload should include:

- `schema_version`
- `schema_mode`
- `week`
- `player_context`
- `planning_context`
- `weekly_content`
- `business_state`
- `crew_context`
- `analysis_hints`
- `data_quality`

## Data Quality Notes

- Use `source` values like `manual`, `rockstar_newswire`, or `mixed`
- Clearly annotate uncertain or inferred fields in `data_quality`
- Keep raw source notes separate from normalized payload data
