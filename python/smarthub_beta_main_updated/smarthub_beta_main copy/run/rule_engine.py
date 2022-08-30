class RuleEngine:
    def __init__(self):
        self.rules = []

    def execute(self, rule_context):
        for rule in self.rules:
            if rule.should_execute(rule_context):
                rule.execute(rule_context)
        return rule_context

    def register_rule(self, rule):
        self.rules.append(rule)
        return self
