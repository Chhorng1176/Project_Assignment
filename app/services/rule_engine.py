# app/services/rule_engine.py

from app.models.rule import Rule


def diagnose(symptoms_input: list):
    """
    Rule-based diagnosis engine

    :param symptoms_input: list of symptoms from user
           Example: ['yellow leaves', 'brown spots']
    :return: dict {
        rule: Rule,
        matched_symptoms: list[str]
    } or None
    """

    if not symptoms_input:
        return None

    # ---------------------------------
    # Normalize input symptoms
    # ---------------------------------
    symptoms_input = [
        s.strip().lower()
        for s in symptoms_input
        if s.strip()
    ]

    matched_results = []

    # ---------------------------------
    # Iterate through all rules
    # ---------------------------------
    for rule in Rule.query.all():

        if not rule.symptoms:
            continue

        # Rule symptoms (comma-separated)
        rule_symptoms = [
            s.strip().lower()
            for s in rule.symptoms.split(",")
            if s.strip()
        ]

        # Find matched symptoms
        matched = [
            s for s in rule_symptoms
            if s in symptoms_input
        ]

        # If at least one symptom matches → consider rule
        if matched:
            matched_results.append({
                "rule": rule,
                "matched_symptoms": matched
            })

    # ---------------------------------
    # No rule matched
    # ---------------------------------
    if not matched_results:
        return None

    # ---------------------------------
    # Sort by confidence (highest first)
    # ---------------------------------
    matched_results.sort(
        key=lambda r: r["rule"].confidence or 0,
        reverse=True
    )

    # Return best rule + explanation
    return matched_results[0]
