from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_validate
from statistics import mean, stdev
from sklearn.utils import shuffle


# TRAINING METHODS AND ALGORITHMS
def fit_linear_regression(dataframe, training_ratio):
    dataframe = shuffle(dataframe)
    X = dataframe[dataframe.columns[:-1]].values
    y = dataframe[dataframe.columns[-1]].values
    k_folds = int(1.0 / (1.0 - training_ratio))
    estimator = LinearRegression()
    cv_results = cross_validate(estimator, X, y, cv=k_folds, return_train_score=True)
    linreg = estimator.fit(X, y)
    y_predict = linreg.predict(X)
    fit_result = {"training_score": mean(cv_results['train_score']),
                  "validation_score": mean(cv_results['test_score']),
                  'train_scores_stdev': stdev(cv_results['train_score']),
                  'test_scores_stdev': stdev(cv_results['test_score']),
                  'y': y, 'y_predict': y_predict}
    return fit_result


def plot_fit():
    pass
