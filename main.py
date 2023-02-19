from sklearn.svm import OneClassSVM
from sklearn.model_selection import KFold, cross_validate
import pandas as pd
import numpy as np

K = 10
NU = 0.01
FLOAT_RANGE = 10

def get_data(path: str) -> np.ndarray:
    df = pd.read_csv(path)
    
    # Remove observations with trace rainfall values (< 0.1 mm)
    df = df[df.RAINFALL != -1]

    # Remove observations with missing values
    df = df[~df.isin([-999]).any(axis=1)]

    df.sort_values(by=['YEAR', 'MONTH', 'DAY'])
    df = df[['RAINFALL', 'TMAX', 'TMIN', 'TMEAN', 'RH', 'WIND_SPEED']]
    df = df.to_numpy()

    return df

def test(X, y, clf) -> float:
    tp = 0
    tn = 0
    fp = 0
    fn = 0

    prediction = clf.predict(X)
    for i in range(len(prediction)):
        # true positive
        if prediction[i] == -1 and y[i] == -1:
            tp += 1
        # true negative
        elif prediction[i] == 1 and y[i] == 1:
            tn += 1
        # false positive
        elif prediction[i] == -1 and y[i] == 1:
            fp += 1
        # false negative
        elif prediction[i] == 1 and y[i] == -1:
            fn += 1

    f_score = tp / (tp + 0.5*(fp + fn))

    return f_score

def main():
    df = get_data('PAGASA/Science Garden.csv')
    X_train, X_test = df[:len(df)-3000], df[len(df)-3000:]

    row = X_train.shape[0]
    y_train = np.full((row, 1), 1)

    row = X_test.shape[0]
    y_test = np.full((row, 1), 1)

    model = OneClassSVM(nu=NU)
    kf = KFold(n_splits=K, shuffle=True)

    cv_res = cross_validate(
        estimator=model,
        X=X_train,
        y=y_train,
        cv=kf,
        scoring='f1',
        n_jobs=-1,
        verbose=1,
        return_train_score=False,
        return_estimator=True
    )

    print('test_score:')
    print(cv_res['test_score'])

    estimators = cv_res['estimator']

    print('F-scores:')
    for clf in estimators:
        f_score = test(X_test, y_test, clf)
        print(f_score)


if __name__ == '__main__':
    main()
