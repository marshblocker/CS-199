import numpy as np
from sklearn.linear_model import SGDOneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM

from classes.utils import LOG

OCCAlgo = OneClassSVM | SGDOneClassSVM | LocalOutlierFactor


class Classifier:
        self.models: list[OCCAlgo | None] = [None for _ in range(12)]
        self.nu = 0.06
        self.K = 10  # number of folds in K-cross validation

    def train(self, data: np.ndarray, month: int):
        X_train = data
        y_train = np.ones(X_train.shape[0])

        K = self.K
        if len(X_train) < self.K:
            K = len(X_train)

        model = OneClassSVM(nu=self.nu)
        kf = KFold(n_splits=K, shuffle=True)

        LOG('models', self.models)

    def classify(self, data: np.ndarray, month: int) -> np.ndarray:
        model = self.models[month-1]

        assert type(model) is OneClassSVM

        return model.predict(data)
    
    def is_complete_models(self):
        total_models = 0
        for i in range(len(self.models)):
            if self.models[i] != None:
                total_models += 1
        
        return total_models == 12
