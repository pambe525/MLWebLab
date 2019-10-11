from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split


# TRAINING METHODS AND ALGORITHMS

def fit_linear_regression(dataframe, training_ratio):
    test_ratio = 1.0 - training_ratio
    X = dataframe[dataframe.columns[:-1]].values
    y = dataframe[dataframe.columns[-1]].values
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_ratio)
    fit = LinearRegression().fit(X_train, y_train)
    fit_result = {"training_score": fit.score(X_train, y_train), "validation_score": fit.score(X_test, y_test)}
    return fit_result
