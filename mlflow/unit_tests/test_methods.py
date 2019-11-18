from django.test import SimpleTestCase
from pandas import DataFrame

from mlflow.methods import fit_linear_regression, correlation_matrix


class MethodsTestCase(SimpleTestCase):

    def test_fit_linear_regression_perfect_plane(self):
        # Y = 3*X1 + 2*X2 + 5
        data = {"X1": list(range(10)), "X2": list(reversed(range(10))), "Y": list(range(15, 25))}
        data_frame = DataFrame(data)
        fit_result = fit_linear_regression(data_frame, 5)
        self.assertEqual(fit_result['mean_train_score'], 1.0)
        self.assertEqual(fit_result['mean_test_score'], 1.0)
        self.assertEqual(fit_result['train_scores_stdev'], 0)
        self.assertEqual(fit_result['test_scores_stdev'], 0)
        y = [round(x, 2) for x in fit_result['y']]
        y_predict = [round(x, 2) for x in fit_result['y_predict']]
        self.assertEqual(y, y_predict)

    def test_fit_linear_regression_arbitrary_data(self):
        # Y = 5*X1 + 3*X2 - 4
        data = {"X1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0], "X2": [3.0, 2.0, 5.0, 1.0, 4.0, 6.0],
                "Y": [12.0, 15.0, 26.0, 16.0, 31.0, 40.0]}
        data_frame = DataFrame(data)
        fit_result = fit_linear_regression(data_frame, 3)
        self.assertNotEqual(round(fit_result['mean_train_score'], 2), 0.0)
        self.assertNotEqual(round(fit_result['mean_test_score'], 2), 0.0)
        self.assertGreaterEqual(round(fit_result['train_scores_stdev'], 2), 0.0)
        self.assertGreaterEqual(round(fit_result['test_scores_stdev'], 2), 0.0)
        self.assertEqual(len(fit_result['train_scores']), 3)
        self.assertTrue(all(fit_result['train_scores']))
        self.assertEqual(len(fit_result['test_scores']), 3)
        self.assertTrue(all(fit_result['test_scores']))
        y = [round(x, 2) for x in fit_result['y']]
        y_predict = [round(x, 2) for x in fit_result['y_predict']]
        self.assertNotEqual(y, y_predict)

    def test_correlation_matrix(self):
        data = {"X1": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0],
                "X2": [4.0, 3.5, 3.0, 2.5, 2.0, 1.5, 1.0, 0.5],
                "X3": [4.0, 5.5, 4.5, 5.0, 5.0, 4.5, 5.5, 4.0]}
        data_frame = DataFrame(data)
        corr_matrix = correlation_matrix(data_frame)
        expected_matrix = [[1.0, -1.0, 0.0], [-1.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        self.assertListEqual(corr_matrix[0], expected_matrix[0])
        self.assertListEqual(corr_matrix[1], expected_matrix[1])
        self.assertListEqual(corr_matrix[2], expected_matrix[2])