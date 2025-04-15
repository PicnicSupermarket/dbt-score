# Seed Support

dbt-score now supports linting and scoring for dbt seeds. Seeds are CSV files that dbt loads into your data warehouse, and they can benefit from the same metadata quality checks as models, sources, and snapshots.

## Seed Rules

The following rules are included for seeds:

- **seed_has_description**: A seed should have a description to explain its purpose and contents.
- **seed_columns_have_description**: All columns in a seed should have descriptions.
- **seed_has_tests**: Seeds should have appropriate tests to ensure data quality.
- **seed_has_owner**: Seeds should have a defined owner for accountability.

## Example

```shell
> dbt-score lint --select my_seed
🥉 Seed: my_seed (score: 6.6)
    WARN (medium) dbt_score.rules.generic.seed_has_description: Seed lacks a description.
    WARN (medium) dbt_score.rules.generic.seed_has_owner: Seed lacks an owner.
```