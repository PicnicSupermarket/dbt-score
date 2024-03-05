"""Entry point of the dbt_score.

This enables module to be run directly.
"""

from dbt_score.cli import cli

if __name__ == "__main__":
    cli()
