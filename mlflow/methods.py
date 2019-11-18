from statistics import mean, stdev

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_validate
from sklearn.utils import shuffle


# TRAINING METHODS AND ALGORITHMS
def fit_linear_regression(data_frame, n_splits):
    dataframe = shuffle(data_frame)
    X = dataframe[dataframe.columns[:-1]].values
    y = dataframe[dataframe.columns[-1]].values
    estimator = LinearRegression()
    cv_results = cross_validate(estimator, X, y, cv=n_splits, return_train_score=True)
    y_predict = estimator.fit(X, y).predict(X)
    fit_result = {
        'train_scores': cv_results['train_score'].tolist(), 'test_scores': cv_results['test_score'].tolist(),
        'mean_train_score': mean(cv_results['train_score']), 'mean_test_score': mean(cv_results['test_score']),
        'train_scores_stdev': stdev(cv_results['train_score']), 'test_scores_stdev': stdev(cv_results['test_score']),
        'y': y.tolist(), 'y_predict': y_predict.tolist()
    }
    return fit_result


def correlation_matrix(data_frame):
    corr = data_frame.corr()
    return corr[corr.columns].values.tolist()
