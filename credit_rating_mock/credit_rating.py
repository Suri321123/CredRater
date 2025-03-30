from abc import ABC, abstractmethod

# There must be a set of functions which needed to be implemented by every rule
class Rule(ABC):
    @abstractmethod
    def calculate_rule_ponits(self, value):
        pass


# here due to different type of attributes we can have, so for better scalability, separated the class for attribute types
# in future if some new type of attribute comes into picture then it will handled by defining new class against it
class NumericRiskRule(Rule):
    def __init__(self, thresholds, comparison=">"):
        self.thresholds = sorted(thresholds, reverse=True)
        self.comparison = comparison

    def calculate_rule_ponits(self, value):
        try:
            for threshold, points in self.thresholds:
                if self.comparison == ">=" and value >= threshold:
                    return points
                elif self.comparison == ">" and value > threshold:
                    return points
            return 0
        except Exception as e:
            print(f"Error in NumericRiskRule: {e}")
            return 0


class CategoryRiskRule(Rule):
    def __init__(self, scores):
        self.scores = scores

    def calculate_rule_ponits(self, value):
        try:
            return self.scores.get(value, 0)
        except Exception as e:
            print(f"Error in CategoryRiskRule: {e}")
            return 0


# this will map the each attribute to its correct class , threshold values and points
class RiskRuleObjectFactoryMaping:
    def __init__(self):
        try:
            self.rules = {
                "ltv": NumericRiskRule(thresholds=[[0.9, 2], [0.8, 1]]),
                "dti": NumericRiskRule(thresholds=[[0.5, 2], [0.4, 1]]),
                "credit_score": NumericRiskRule(thresholds=[[700, -1], [650, 0], [0, 1]], comparison=">="),
                "loan_type": CategoryRiskRule(scores={"fixed": -1, "adjustable": 1}),
                "property_type": CategoryRiskRule(scores={"condo": 1}),
            }
        except Exception as e:
            print(f"Error initializing RiskRuleObjectFactoryMaping: {e}")

    def get_rule(self, attribute_name):
        try:
            return self.rules.get(attribute_name, None)
        except Exception as e:
            print(f"Error in get_rule: {e}")
            return None


# class to return the score point of each rule attrribute
class RiskRuleScoreCalculator:
    # used dependency injection rather declaring the class objects directly to de-couple
    def __init__(self, rule_obj_mapper):
        self.rule_obj_mapper = rule_obj_mapper

    def get_rule_score(self, attribute_name, value):
        try:
            rule = self.rule_obj_mapper.get_rule(attribute_name)
            return rule.calculate_rule_ponits(value) if rule else 0
        except Exception as e:
            print(f"Error in get_rule_score: {e}")
            return 0


# this is a general class to hold the common attributes of mortgage
class Mortgage:
    def __init__(self, loan_amount, property_value, debt_amount, annual_income, credit_score, loan_type, property_type):
        self.loan_amount = loan_amount
        self.property_value = property_value
        self.debt_amount = debt_amount
        self.annual_income = annual_income
        self.credit_score = credit_score
        self.loan_type = loan_type
        self.property_type = property_type


# this is specific mortgage class for residential only,
# In case something else type of mortgage comes we can always have a separate class to scale
class ResidentialMortgage(Mortgage):
    # passing the risk_evaluator object as dependency injection rather declaring the class here itself to decouple
    def __init__(self, risk_evaluator, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.risk_evaluator = risk_evaluator

    def calculate_risk_score(self):
        try:
            risk_factors = {
                "ltv": self.loan_amount / self.property_value,
                "dti": self.debt_amount / self.annual_income,
                "credit_score": self.credit_score,
                "loan_type": self.loan_type,
                "property_type": self.property_type,
            }
            return sum(self.risk_evaluator.get_rule_score(attribute_name, value) for attribute_name, value in risk_factors.items())
        except Exception as e:
            print(f"Error in calculate_risk_score: {e}")
            return 0


# there can be more ratings added in future so, we can modify this single class and add them independently
class FinalCreditRating:
    def __init__(self, risk_score):
        self.risk_score = risk_score
    
    def get_final_rating(self):
        try:
            if self.risk_score <= 2:
                return "AAA"
            elif self.risk_score >= 3 and self.risk_score <= 5:
                return "BBB"
            elif self.risk_score > 5:
                return "C"
        except Exception as e:
            print(f"Error in get_final_rating: {e}")
            return "Unknown"


def main(risk_evaluator, sample_data):
    results = []
    try:
        for mortgage_data in sample_data["mortgages"]:
            mortgage = ResidentialMortgage(
                risk_evaluator,
                loan_amount=mortgage_data["loan_amount"],
                property_value=mortgage_data["property_value"],
                debt_amount=mortgage_data["debt_amount"],
                annual_income=mortgage_data["annual_income"],
                credit_score=mortgage_data["credit_score"],
                loan_type=mortgage_data["loan_type"],
                property_type=mortgage_data["property_type"]
            )

            final_rating = FinalCreditRating(mortgage.calculate_risk_score()).get_final_rating()
            results.append({
                "risk_score": mortgage.calculate_risk_score()
            })
    except Exception as e:
        print(f"Error in main function: {e}")

    return results


if __name__ == "__main__":
    try:
        # sample data which will be taken from APIs or some data source.
        mortgage_data = {
            "mortgages": [
                {"credit_score": 750, "loan_amount": 200000, "property_value": 250000,
                "annual_income": 60000, "debt_amount": 20000, "loan_type": "fixed",
                "property_type": "single_family"},
                {"credit_score": 680, "loan_amount": 150000, "property_value": 175000,
                "annual_income": 45000, "debt_amount": 10000, "loan_type": "adjustable",
                "property_type": "condo"}
            ]
        }

        # initialize all the risk rules, Rick rules can also be taken from API of some data source
        rule_obj_mapper = RiskRuleObjectFactoryMaping()

        risk_evaluator = RiskRuleScoreCalculator(rule_obj_mapper)
        
        final_ratings = main(risk_evaluator, mortgage_data)

        for idx, rating in enumerate(final_ratings, 1):
            final_rating = FinalCreditRating(rating['risk_score'])
            result = final_rating.get_final_rating()
            print(f"Mortgage {idx}: Final Credit Rating = {result}")
    except Exception as e:
        print(f"Unexpected error in execution: {e}")
