import os
import os.path

from pandas import read_csv

from mlflow import constants


# Finds if a pandas data frame has headers
def dataframe_has_headers(data_frame):
    for header in data_frame.columns:
        try:
            float(header)
            return False
        except ValueError:
            continue
    return True


# Reads csv data file and returns a pandas DataFrame object (also checks for date file errors)
def read_csv_datafile(file_name):
    file_path = os.path.join(constants.DATA_FILE_PATH, file_name)
    dataFrame = read_csv(file_path)
    if int(dataFrame.shape[1]) < 2:
        raise Exception("Data file has only one column. Add at least one more column.")
    if not dataframe_has_headers(dataFrame):
        raise Exception("Data file has no headers. Add non-numeric column headers.")
    if int(dataFrame.shape[0]) < 10:
        raise Exception("Data file has fewer than 10 records (must have at least 10 records)")
    return dataFrame


# Sets default context dict parameters for home page content container
def set_data_file_response(response, data_frame):
    response['data_file_rows'] = int(data_frame.shape[0])
    response['data_file_cols'] = int(data_frame.shape[1])
    response['target_feature'] = data_frame.columns[-1]
    summary = []
    for column_name in data_frame.columns:
        column_stats = {
            'name': column_name,
            'type': str(data_frame.dtypes[column_name]),
            'min': round(min(data_frame[column_name]), 2),
            'max': round(max(data_frame[column_name]), 2),
            'mean': round(data_frame[column_name].mean(), 2),
            'stdev': round(data_frame[column_name].std(), 2)
        }
        summary.append(column_stats)
    response['column_summary'] = summary
    response['data_frame'] = data_frame.to_json()
