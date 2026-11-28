"""dbt-score exceptions."""


class DuplicatedRuleException(Exception):
    """Two rules with the same name are defined."""

    def __init__(self, rule_name: str):
        """Instantiate exception."""
        super().__init__(
            f"Rule {rule_name} is defined twice. Rules must have unique names."
        )


class RuleNotFoundException(Exception):
    """Selected rules could not be found."""

    def __init__(self, rule_names: list[str]):
        """Instantiate exception."""
        super().__init__(f"Selected rule(s) not found: {', '.join(rule_names)}.")
