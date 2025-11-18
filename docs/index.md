# Welcome to dbt-score

`dbt-score` is a linter for [dbt](https://www.getdbt.com/) metadata.

dbt allows data practitioners to organize their data into _models_ and
_sources_. Those models and sources have metadata associated with them:
documentation, tests, types, etc. dbt supports more types of entities, e.g.
snapshots, analysis, seeds and more.

`dbt-score` allows to lint and score this metadata, in order to enforce (or
encourage) good practices. The dbt entities that `dbt-score` is able to lint
(currently) are:

- Models
- Sources
- Snapshots
- Exposures
- Seeds
- Macros

## Example

```
> dbt-score lint --show all
🥇 M: customers (score: 10.0)
    OK   dbt_score.rules.generic.has_description
    OK   dbt_score.rules.generic.has_owner
    OK   dbt_score.rules.generic.sql_has_reasonable_number_of_lines
Score: 10.0 🥇
```

In this example, the model `customers` scores the maximum value of `10.0` as it
passes all the rules. It also is awarded a golden medal because of the perfect
score. By default a passing dbt entity with or without rule violations will not
be shown, unless we pass the `--show-all` flag.

## Philosophy

dbt entities are often used as metadata containers: either in YAML files or
through the use of `{{ config() }}` blocks, they are associated with a lot of
information. At scale, it becomes tedious to enforce good practices in large
data teams dealing with many dbt entities.

To that end, `dbt-score` has 2 main features:

- It runs rules on dbt entities, and displays any rule violations. These can be
  used in interactive environments or in CI.
- Using those run results, it scores items, to ascribe them a measure of their
  maturity. This score can help gamify metadata improvements/coverage, and be
  reflected in data catalogs.

`dbt-score` aims to:

- Provide a predefined set of good practices (the core rules).
- Allow teams to easily add their own rules.
- Allow rule sets to be packaged and distributed.
- Be configurable to adapt to different data stacks and practices.

## About

`dbt-score` is free software, released under the MIT license. It originated at
Picnic Technologies in Amsterdam, Netherlands. Source code is
[available on Github](https://github.com/PicnicSupermarket/dbt-score).

All contributions, in the form of bug reports, pull requests, feedback or
discussion are welcome. See the **contribution guide** for more information.
