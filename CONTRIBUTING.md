# Contributing

Keep financial calculations deterministic and testable. Add or update a unit
test for every behavior change, preserve raw transaction descriptions, and use
`Decimal` through the money helpers rather than binary floating-point arithmetic.

Before pushing, run:

```text
python -m unittest discover -s tests
```

Changes that affect database structure should include a migration or an
idempotent SQL script and document any operational order of execution.
