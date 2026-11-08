# Engineering samples

These examples demonstrate the core technical patterns behind Map8.

## Included examples

| Directory | Focus |
|---|---|
| `backend/` | Flask route/service separation and transactional SQL Server persistence |
| `frontend/` | Resilient asynchronous requests and editable-calendar state |
| `algorithms/` | Capacity-aware geographic allocation and route ordering |
| `automation/` | Controlled Selenium browser automation |
| `tests/` | Deterministic tests for algorithms and calendar state |

## Run the tests

The geospatial sample and its tests use only the Python standard library:

```bash
python -m unittest discover -s examples/tests -v
cd examples && npm test
```

Optional packages for the integration examples are listed in `requirements.txt`.

