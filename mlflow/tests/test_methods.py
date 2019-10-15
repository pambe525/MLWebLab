from django.test import SimpleTestCase
from mlflow.methods import fit_linear_regression
from pandas import DataFrame


class MethodsTestCase(SimpleTestCase):

    def test_fit_linear_regression_perfect_line(self):
        # Y = 3*X1 + 2*X2 + 5
        data = {"X1": list(range(10)), "X2": list(reversed(range(10))), "Y": list(range(15, 25))}
        data_frame = DataFrame(data)
        fit_result = fit_linear_regression(data_frame, 0.8)
        self.assertEqual(fit_result['training_score'], 1.0)
        self.assertEqual(fit_result['validation_score'], 1.0)
