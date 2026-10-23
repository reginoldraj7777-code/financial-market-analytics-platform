# API guide

Start with `uvicorn src.api:app --host 127.0.0.1 --port 8000`. Open `/docs` for the schema.

| Route | Purpose |
|---|---|
| GET /health | Process health and API version |
| GET /metrics | Read the selected benchmark manifest |
| GET /alerts?limit=20 | Up to 100 ranked synthetic candidates without labels |
| POST /score | Score up to 10,000 finite values against a supplied positive-scale baseline |
| POST /reviews | Append a human decision for an existing queue observation |
| GET /reviews?limit=20 | Read the latest review events, preserving earlier decisions |

Example score body:

```json
{"values":[99,100,101,120],"center":100,"scale":2,"threshold":2.5}
```

Scores are `[0.5,0,0.5,10]`; only the last value is flagged. Compute the baseline on a preceding window; never fit on the observations under investigation.

Fetch `/alerts` to obtain a real `observation_id`, then send a review body with that ID, `decision` (`confirmed`, `dismissed`, `needs_context`), `reviewer`, and optional `note`. Each submission creates a new event; corrections never overwrite history. Unknown observations return 404, missing benchmark artifacts return 503, invalid request bodies return 422.

`EVIDENCE_DIR` defaults to `evidence/full`; `REVIEW_DB` defaults to `data/reviews.db`. Database records are local and ignored by Git. Back up or mount this directory for persistence. This demo has no authentication or rate limiting and should remain on a trusted local interface until those controls are added.
