`agents/data` stores machine-readable runtime datasets used by agent report generators.

- Keep these files normalized and loader-friendly.
- Avoid placing schema or explanatory metadata here unless it is required at runtime.
- `tony.json` is the canonical Nightclub goods catalog consumed by Tony's report generator.