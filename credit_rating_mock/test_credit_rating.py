import pytest
from credit_rating import (
    NumericRiskRule,
    CategoryRiskRule,
    RiskRuleObjectFactoryMaping,
    RiskRuleScoreCalculator,
    ResidentialMortgage,
)


@pytest.fixture
def rule_manager():
    return RiskRuleObjectFactoryMaping()


@pytest.fixture
def get_rule_score(rule_manager):
    return RiskRuleScoreCalculator(rule_manager)


def test_ltv_rule(get_rule_score):
    assert get_rule_score.get_rule_score("ltv", 1.0) == 2
    assert get_rule_score.get_rule_score("ltv", 0.85) == 1
    assert get_rule_score.get_rule_score("ltv", 0.75) == 0


def test_dti_rule(get_rule_score):
    assert get_rule_score.get_rule_score("dti", 0.6) == 2
    assert get_rule_score.get_rule_score("dti", 0.45) == 1
    assert get_rule_score.get_rule_score("dti", 0.35) == 0


def test_credit_score_rule(get_rule_score):
    assert get_rule_score.get_rule_score("credit_score", 720) == -1
    assert get_rule_score.get_rule_score("credit_score", 680) == 0
    assert get_rule_score.get_rule_score("credit_score", 640) == 1


def test_loan_type_rule(get_rule_score):
    assert get_rule_score.get_rule_score("loan_type", "fixed") == -1
    assert get_rule_score.get_rule_score("loan_type", "adjustable") == 1
    assert get_rule_score.get_rule_score("loan_type", "unknown") == 0


def test_property_type_rule(get_rule_score):
    assert get_rule_score.get_rule_score("property_type", "condo") == 1
    assert get_rule_score.get_rule_score("property_type", "house") == 0


def test_risk_rule_manager(rule_manager):
    assert isinstance(rule_manager.get_rule("ltv"), NumericRiskRule)
    assert isinstance(rule_manager.get_rule("dti"), NumericRiskRule)
    assert isinstance(rule_manager.get_rule("credit_score"), NumericRiskRule)
    assert isinstance(rule_manager.get_rule("loan_type"), CategoryRiskRule)
    assert isinstance(rule_manager.get_rule("property_type"), CategoryRiskRule)
    assert rule_manager.get_rule("unknown") is None


def test_residential_mortgage_one_sample(get_rule_score):
    mortgage = ResidentialMortgage(
        get_rule_score,
        loan_amount=200000,    # LTV = 200k / 250k = 0.8 → Score = 0
        property_value=250000,
        debt_amount=50000,     # DTI = 50k / 100k = 0.5 → Score = 1
        annual_income=100000,
        credit_score=720,      # Credit Score = 720 → Score = -1
        loan_type="fixed",     # Loan Type = "fixed" → Score = -1
        property_type="condo"  # Property Type = "condo" → Score = 1
    )

    risk_score = mortgage.calculate_risk_score()
    expected_score = 0 + 1 - 1 - 1 + 1
    assert risk_score == expected_score

def test_residential_mortgage_second_sample(get_rule_score):
    mortgage = ResidentialMortgage(
        get_rule_score,
        loan_amount=200000,    # LTV = 200k / 250k = 0.8 → Score = 0
        property_value=250000,
        debt_amount=20000,     # DTI = 20k / 60k = 0.33 → Score = 0 
        annual_income=60000,
        credit_score=750,      # Credit Score = 720 → Score = -1
        loan_type="fixed",     # Loan Type = "fixed" → Score = -1
        property_type="single_family"  # Property Type = "condo" → Score = 0
    )

    risk_score = mortgage.calculate_risk_score()
    expected_score = 0 + 0 - 1 - 1 + 0
    assert risk_score == expected_score


def test_numeric_risk_rule_invalid_comparison():
    rule = NumericRiskRule(thresholds=[[0.9, 2]], comparison="invalid")
    assert rule.calculate_rule_ponits(0.95) == 0

def test_category_risk_rule_invalid_input():
    rule = CategoryRiskRule(scores={"fixed": -1, "adjustable": 1})
    assert rule.calculate_rule_ponits(123) == 0

def test_risk_rule_object_factory_missing_rule():
    factory = RiskRuleObjectFactoryMaping()
    assert factory.get_rule("non_existent_attribute") is None

def test_risk_rule_score_calculator_missing_rule():
    factory = RiskRuleObjectFactoryMaping()
    calculator = RiskRuleScoreCalculator(factory)
    assert calculator.get_rule_score("non_existent_attribute", 1) == 0
