# Pydantic-generated JSON contracts

These JSON Schema files are generated from the Pydantic v2 models in `app/schemas.py` by:

```bash
cd backend
uv run python scripts/export_contracts.py
```

Do not hand-edit generated schemas. Regenerate and review them whenever Pydantic contracts change. The JSON Schemas encode field types, bounds, allowlisted values, and `extra=forbid`; Pydantic also enforces cross-field invariants (fact status/evidence consistency, response-state consistency, and source-offset/citation checks) that are not fully expressible in the generated schemas. The server must validate with the Pydantic models and `validate_evidence_links()`, not rely on JSON Schema alone. The contract currently accepts English (`en`) only; other locales must not be enabled until translation/UI/refusal content has fluent review. API routes/model processing are not implemented by this phase.
