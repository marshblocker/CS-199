from sklearn.svm import OneClassSVM
from sklearn.model_selection import KFold, cross_validate

import numpy as np

class Classifier:
    def __init__(self):
        self.models: list[OneClassSVM | None] = [None for _ in range(12)]
        self.nu = 0.06
        self.K = 10 # number of folds in K-cross validation

    def train(self, data: np.ndarray, month: int):
        X_train = data
        y_train = np.ones(X_train.shape[0])

        model = OneClassSVM(nu=self.nu)
        kf = KFold(n_splits=self.K, shuffle=True)

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
        print(cv_res['test_score'])

        test_scores = list(cv_res['test_score'])
        max_score_indx = test_scores.index(max(test_scores))
        models = list(cv_res['estimator'])
        best_model = models[max_score_indx]
        self.models[month-1] = best_model

    def classify(self, data: np.ndarray, month: int) -> np.ndarray:
        model = self.models[month-1]

        assert type(model) is OneClassSVM

        return model.predict(data)
