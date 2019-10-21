from statistics import mean, stdev

from pandas import read_json
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_validate
from sklearn.utils import shuffle


# TRAINING METHODS AND ALGORITHMS
def fit_linear_regression(json_data, training_ratio):
    dataframe = shuffle(read_json(json_data))
    X = dataframe[dataframe.columns[:-1]].values
    y = dataframe[dataframe.columns[-1]].values
    k_folds = int(1.0 / (1.0 - training_ratio))
    estimator = LinearRegression()
    cv_results = cross_validate(estimator, X, y, cv=k_folds, return_train_score=True)
    y_predict = estimator.fit(X, y).predict(X)
    fit_result = {"train_score": mean(cv_results['train_score']), "test_score": mean(cv_results['test_score']),
                  'train_scores_stdev': stdev(cv_results['train_score']),
                  'test_scores_stdev': stdev(cv_results['test_score']),
                  'y': y.tolist(), 'y_predict': y_predict.tolist()}
    return fit_result
