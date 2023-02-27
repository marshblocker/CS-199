from sklearn.svm import OneClassSVM
from sklearn.model_selection import KFold, cross_validate
import pandas as pd
import numpy as np
import os

K = 10
NU = 0.06

metro_manila = ['NAIA','Port Area','Sangley Point', 'Science Garden']

def get_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    df.sort_values(by=['YEAR', 'MONTH', 'DAY'])
    df = df[['YEAR', 'MONTH', 'DAY', 'TMAX', 'TMIN', 'TMEAN', 'RH']]

    tmax_mean = df[df['TMAX'] != -999]['TMAX'].mean()
    tmin_mean = df[df['TMIN'] != -999]['TMIN'].mean()
    tmean_mean = df[df['TMEAN'] != -999]['TMEAN'].mean()
    rh_mean = df[df['RH'] != -999]['RH'].mean()

    df.loc[df['TMAX'] == -999, 'TMAX'] = tmax_mean
    df.loc[df['TMIN'] == -999, 'TMIN'] = tmin_mean
    df.loc[df['TMEAN'] == -999, 'TMEAN'] = tmean_mean
    df.loc[df['RH'] == -999, 'RH'] = rh_mean

    return df

def test(X, y, clf) -> float:
    tp = 0
    tn = 0
    fp = 0
    fn = 0

    prediction = clf.predict(X)
    for i in range(len(prediction)):
        # true positive
        if prediction[i] == 1 and y[i] == 1:
            tp += 1
        # true negative
        elif prediction[i] == -1 and y[i] == -1:
            tn += 1
        # false positive
        elif prediction[i] == 1 and y[i] == -1:
            fp += 1
        # false negative
        elif prediction[i] == -1 and y[i] == 1:
            fn += 1

    f_score = tp / (tp + 0.5*(fp + fn))
    # print(tp, tn, fp, fn)
    return f_score

def main():
    directory = 'PAGASA/'
    stations = {}
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            df = get_data(directory + filename)
            df = {
                year: df_year.reset_index()
                for year, df_year in df.groupby('YEAR')
            }
            stations[filename.rstrip('.csv')] = df

    year = 2016
    month = 1

    for i in range(1, 12):
        month = i

        X_train = [stations[station_name][year] for station_name in metro_manila]
        X_train = [df[df['MONTH'] == month] for df in X_train]
        X_train = [df[['TMAX', 'TMIN', 'TMEAN', 'RH']].to_numpy() for df in X_train]
        X_train = np.concatenate((X_train))
        
        y_train = np.full((len(X_train), 1), 1)

        model = OneClassSVM(nu=NU)
        kf = KFold(n_splits=K, shuffle=True)

        cv_res = cross_validate(
            estimator=model,
            X=X_train,
            y=y_train,
            cv=kf,
            scoring='f1',
            n_jobs=-1,
            verbose=0,
            return_train_score=False,
            return_estimator=True
        )

        estimators = cv_res['estimator']

        X_test_clean = stations['NAIA'][year+1]
        X_test_clean = X_test_clean[X_test_clean['MONTH'] == month]
        X_test_clean = X_test_clean[['TMAX', 'TMIN', 'TMEAN', 'RH']].to_numpy()

        y_test_clean = np.full((len(X_test_clean), 1), 1)

        X_test_mal = stations['Baguio'][year+1]
        X_test_mal = X_test_mal[X_test_mal['MONTH'] == month]
        X_test_mal = X_test_mal[['TMAX', 'TMIN', 'TMEAN', 'RH']].to_numpy()

        y_test_mal = np.full((len(X_test_mal), 1), -1)

        X_test = np.concatenate((X_test_clean, X_test_mal))
        y_test = np.concatenate((y_test_clean, y_test_mal))

        ave_f_score = round(sum(map(
            lambda clf: test(X_test, y_test, clf),
            estimators
        )) / len(estimators), 3)

        print('Average F-score:', ave_f_score)


if __name__ == '__main__':
    main()