# How it is built

## Contents

- [The shape](#the-shape)
- [Safe by default](#safe-by-default)
- [Kavita behaviour it relies on](#kavita-behaviour-it-relies-on)

## The shape

```
Kavita  <--  api.py  -->  cli.py  -->  core.py (rules and matching)
                             |
                             +-->  notify.py  -->  your webhook
```

`core.py` never touches the network, the disk or the clock.

## Safe by default

- `DRY_RUN` is true until set to false. `plan` and dry run write and alert nothing.
- The only writes are adding series to a named collection, and sharing a collection it has just created.
- An empty series list or a bad rules file changes nothing. One failing rule does not stop the others.
- A wildcard-only pattern is refused unless authors narrow it.
- Redirects are refused, so the key is never resent elsewhere.

## Kavita behaviour it relies on

Seen on a real Kavita 0.9.1:

- The account's API key works in the `x-api-key` header.
- `POST /api/Collection/update-for-series` only adds, and adding a series twice is harmless.
- With `collectionTagId` 0 it always creates a new collection, even if the name exists, so it is looked up first.
- A new collection is visible only to its owner until `POST /api/Collection/update` promotes it.
- A series filter with field 7 lists a collection's members.
- A library scan removes a collection that has no series.
