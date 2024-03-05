"""dbt-score exceptions."""


class DuplicatedRuleException(Exception):
    """Two rules with the same name are defined."""

    def __init__(self, rule_name: str):
        """Instantiate exception."""
        super().__init__(
            f"Rule {rule_name} is defined twice. Rules must have unique names."
        )
