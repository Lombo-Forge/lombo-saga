---
name: adapt
description: Change LomboSaga's rules, thresholds, settings or alerts without breaking it. Use when the user wants different behaviour, a new setting, a new Kavita call or a different alert target.
---

# Adapt LomboSaga

1. **Change a rule:** for new series edit `rules.json`; for new behaviour edit `core.py`. Write the test first with plain data, watch it
   fail, then change the code. Keep `core.py` free of network, disk and clock; pass what it needs in.
2. **Add a setting:** read and validate it in `config.py` (the error must name the variable), add a
   commented line to `.env.example`, and add a test in `tests/test_app.py` for a bad value.
3. **Add a Kavita call:** add a method to `api.py`, the path to the fake in `tests/conftest.py`,
   and a test. Confirm the call against a throwaway Kavita before relying on it.
4. **Change alerts:** `notify.py` posts JSON to a webhook. For a service that needs a different body,
   put a small bridge in front of it, or add a second function and keep `send()` as is.
5. **Run:** `pytest -q` and `sh scripts/leak-check.sh`. Both must pass.
6. **Stay safe:** a change must leave `DRY_RUN` defaulting to true and `plan` read-only.
