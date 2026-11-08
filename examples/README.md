# Public engineering samples

These examples demonstrate the technical patterns behind Map8 without copying production source code. All routes, table names, selectors, credentials, payloads, thresholds and records are synthetic.

## Included examples

| Directory | Focus |
|---|---|
| `backend/` | Flask route/service separation and transactional SQL Server persistence |
| `frontend/` | Resilient asynchronous requests and editable-calendar state |
| `algorithms/` | Capacity-aware geographic allocation and route ordering |
| `automation/` | Controlled Selenium browser automation |
| `tests/` | Deterministic tests for the public algorithm sample |

## Run the tests

The geospatial sample and its tests use only the Python standard library:

```bash
python -m unittest discover -s examples/tests -v
cd examples && npm test
```

The integration-oriented examples are intentionally not connected to a real database or ERP. Their optional packages are listed in `requirements.txt`.

## Publication boundary

- No production module was copied into this directory.
- No real hostname, IP address, database/table name, provider token or CSS selector is present.
- No customer, employee, order or route record is present.
- Security controls shown here are illustrative; private deployment controls remain private.

