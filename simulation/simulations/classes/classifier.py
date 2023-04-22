import numpy as np
from sklearn.linear_model import SGDOneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM

from classes.utils import LOG

OCCAlgo = OneClassSVM | SGDOneClassSVM | LocalOutlierFactor


class Classifier:
    def __init__(self, decision_threshold=-1.0):
        self.models: list[OCCAlgo | None] = [None for _ in range(12)]
        self.decision_threshold = decision_threshold

        # OCSVM params
        self.nu = 0.06

        # LOF params
        self.n_neighbors=20
        self.contamination=0.1

    def train(self, data: np.ndarray, month: int):
        model = OneClassSVM(nu=self.nu)
        model = model.fit(data)
        self.models[month-1] = model

        LOG('models', self.models)

    def classify(self, data: np.ndarray, month: int) -> np.ndarray:
        model = self.models[month-1]

        assert type(model) is OneClassSVM
        decisions = model.decision_function(data)
        classification_res = self.decide(decisions)

        return np.array(classification_res)

    def decide(self, decisions):
        classification_res = []
        for decision in decisions:
            if decision <= self.decision_threshold:
                classification_res.append(-1)
            else:
                classification_res.append(1)

        return classification_res

    def is_complete_models(self):
        total_models = 0
        for i in range(len(self.models)):
            if self.models[i] != None:
                total_models += 1

        return total_models == 12
