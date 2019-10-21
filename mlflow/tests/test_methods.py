from django.test import SimpleTestCase
from pandas import DataFrame

from mlflow.methods import fit_linear_regression


class MethodsTestCase(SimpleTestCase):

    def test_fit_linear_regression_perfect_plane(self):
        # Y = 3*X1 + 2*X2 + 5
        data = {"X1": list(range(10)), "X2": list(reversed(range(10))), "Y": list(range(15, 25))}
        json_data = DataFrame(data).to_json()
        fit_result = fit_linear_regression(json_data, 0.8)
        self.assertEqual(fit_result['train_score'], 1.0)
        self.assertEqual(fit_result['test_score'], 1.0)
        self.assertEqual(fit_result['train_scores_stdev'], 0)
        self.assertEqual(fit_result['test_scores_stdev'], 0)
        y = [round(x, 2) for x in fit_result['y']]
        y_predict = [round(x, 2) for x in fit_result['y_predict']]
        self.assertEqual(y, y_predict)

    def test_fit_linear_regression_arbitrary_data(self):
        # Y = 5*X1 + 3*X2 - 4
        data = {"X1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0], "X2": [3.0, 2.0, 5.0, 1.0, 4.0, 6.0],
                "Y": [12.0, 15.0, 26.0, 16.0, 31.0, 40.0]}
        json_data = DataFrame(data).to_json()
        fit_result = fit_linear_regression(json_data, 0.7)
        self.assertGreater(round(fit_result['train_score'], 2), 0.9)
        self.assertGreater(round(fit_result['test_score'], 2), 0.1)
        self.assertGreaterEqual(round(fit_result['train_scores_stdev'], 2), 0.0)
        self.assertGreaterEqual(round(fit_result['test_scores_stdev'], 2), 0.0)
        y = [round(x, 2) for x in fit_result['y']]
        y_predict = [round(x, 2) for x in fit_result['y_predict']]
        self.assertNotEqual(y, y_predict)
