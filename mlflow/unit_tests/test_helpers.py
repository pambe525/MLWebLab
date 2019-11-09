import os
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from pandas import DataFrame
from pandas.errors import EmptyDataError

from mlflow import constants
from mlflow.helpers import dataframe_has_headers
from mlflow.helpers import read_csv_datafile
from mlflow.helpers import set_data_file_response


class HelperStaticFunctionsTestCase(SimpleTestCase):
    mock_data = data = {"Col1": [1, 2, 3, 4], "col2": [5, 6, 7, 8], "Col3": [9, 10, 11, 12],
                        "Col4": [13, 14, 15, 16], "Col5": [17, 18, 19, 20]}
    mock_data_summary = [
        {"name": "Col1", "type": "int64", "min": 1, "max": 4, "mean": 2.5, "stdev": 1.29},
        {"name": "col2", "type": "int64", "min": 5, "max": 8, "mean": 6.5, "stdev": 1.29},
        {"name": "Col3", "type": "int64", "min": 9, "max": 12, "mean": 10.5, "stdev": 1.29},
        {"name": "Col4", "type": "int64", "min": 13, "max": 16, "mean": 14.5, "stdev": 1.29},
        {"name": "Col5", "type": "int64", "min": 17, "max": 20, "mean": 18.5, "stdev": 1.29}
    ]

    # ---------------------------------------------------------------------------------------------
    # Tests for dataframe_has_headers
    # ---------------------------------------------------------------------------------------------
    def test_dataframe_has_headers_with_proper_headers(self):
        data = {"Col1": [1, 2, 3, 4], "col2": [5, 6, 7, 8], "Col3": [9, 10, 11, 12],
                "Col4": [13, 14, 15, 16], "Col5": [17, 18, 19, 20]}
        self.assertTrue(dataframe_has_headers(DataFrame(data)))

    def test_dataframe_has_headers_with_mixed_headers(self):
        data = {"1.2": [1, 2, 3, 4], "col2": [5, 6, 7, 8], "2": [9, 10, 11, 12],
                "Col4": [13, 14, 15, 16], 3: [17, 18, 19, 20]}
        self.assertFalse(dataframe_has_headers(DataFrame(data)))

    def test_dataframe_has_headers_with_numeric_headers(self):
        data = {"1": [1, 2, 3, 4], "2.0": [5, 6, 7, 8], "3": [9, 10, 11, 12],
                "4": [13, 14, 15, 16], "5": [17, 18, 19, 20]}
        self.assertFalse(dataframe_has_headers(DataFrame(data)))

    # ---------------------------------------------------------------------------------------------
    # Tests for read_csv_data_file
    # ---------------------------------------------------------------------------------------------
    def test_read_csv_data_file_reads_returns_dataframe(self):
        data = {"col1": list(range(10)), "col2": list(range(10, 20)), "col3": list(range(20, 30)),
                "col4": list(range(30, 40)), "col5": list(range(40, 50))}
        filename = "test.csv"
        filepath = os.path.join(constants.DATA_FILE_PATH, filename)
        with patch("mlflow.helpers.read_csv") as mock_read_csv:
            mock_read_csv.return_value = DataFrame(data)
            dataframe = read_csv_datafile(filename)
            mock_read_csv.assert_called_once_with(filepath)
        self.assertEqual(dataframe.shape[0], 10)
        self.assertEqual(dataframe.shape[1], 5)

    def test_read_csv_data_file_with_read_exception(self):
        with patch("mlflow.helpers.read_csv") as mock_read_csv:
            mock_read_csv.side_effect = EmptyDataError("No data in file")
            try:
                read_csv_datafile("test.csv")
            except EmptyDataError as e:
                mock_read_csv.assert_called_once()
                self.assertEqual(str(e), "No data in file")

    def test_read_csv_data_file_with_one_column_in_data_file_error(self):
        data = {"col1": [1, 2, 3, 4]}
        with patch("mlflow.helpers.read_csv") as mock_read_csv:
            mock_read_csv.return_value = DataFrame(data)
            try:
                read_csv_datafile("test.csv")
            except Exception as e:
                mock_read_csv.assert_called_once()
                self.assertTrue("Data file has only one column" in str(e))

    def test_read_csv_data_file_with_numeric_headers_error(self):
        data = {"1.5": [1.1, 2.1, 3.1], "2.2": [1.2, 2.2, 3.2], "col3": [1.3, 2.3, 3.3]}
        with patch("mlflow.helpers.read_csv") as mock_read_csv:
            mock_read_csv.return_value = DataFrame(data)
            try:
                read_csv_datafile("test.csv")
            except Exception as e:
                mock_read_csv.assert_called_once()
                self.assertTrue("Data file has no headers" in str(e))

    def test_read_csv_data_file_with_less_than_10_records(self):
        data = {"col1": list(range(9)), "col2": list(range(10, 19)), "col3": list(range(20, 29)),
                "col4": list(range(30, 39)), "col5": list(range(40, 49))}
        with patch("mlflow.helpers.read_csv") as mock_read_csv:
            mock_read_csv.return_value = DataFrame(data)
            try:
                read_csv_datafile("test.csv")
            except Exception as e:
                mock_read_csv.assert_called_once()
                self.assertTrue("Data file has fewer than 10 records" in str(e))

    # ---------------------------------------------------------------------------------------------
    # Tests for set_data_file_info
    # ---------------------------------------------------------------------------------------------
    def test_set_data_file_response_returns_response(self):
        data_frame = DataFrame(self.mock_data)
        response = {}
        set_data_file_response(response, data_frame)
        self.assertEqual(response['data_file_rows'], data_frame.shape[0])
        self.assertEqual(response['data_file_cols'], data_frame.shape[1])
        self.assertEqual(response['target_feature'], data_frame.columns[-1])
        self.assertEqual(response['features_summary'], self.mock_data_summary)
        self.assertEqual(response['data_frame'], data_frame.to_json())

    # ----------------------------------------------------------------------------------------------
    # def _verify_validation_content(self, context, is_enabled):
    #     if not is_enabled:
    #         self.assertEqual(context['active_tab'], "data_summary")
    #     else:
    #         self.assertEqual(context['active_tab'], "train")
    #         self.assertEqual(context['training_method'], "Linear Regression")
    #         self.assertGreater(float(context['validation_score']), 0)
    #         self.assertGreater(float(context['training_score']), 0)
