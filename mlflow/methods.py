from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_validate
from statistics import mean, stdev
from sklearn.utils import shuffle
import base64
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO


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


def plot_fit(y, y_predict, context):
    plt.figure(figsize=(5, 3), dpi=100)
    plt.scatter(y, y_predict, color="darkred", s=5)
    plt.plot([min(y), max(y)], [min(y_predict), max(y_predict)], color="lightgray")
    target = context['target_feature']
    plt.xlabel("Actual " + target, fontsize=9)
    plt.ylabel("Predicted " + target, fontsize=9)
    plt.xticks(fontsize=7)
    plt.yticks(fontsize=7)
    plt.title("Actual versus Predicted Target Feature")
    plt.tight_layout()
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    context['graphic'] = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    buf.close()
