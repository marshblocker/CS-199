import numpy as np
from sklearn.kernel_approximation import Nystroem
from sklearn.linear_model import SGDOneClassSVM
from sklearn.neighbors import LocalOutlierFactor
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.svm import OneClassSVM

from classes.utils import LOG

OCCAlgo = OneClassSVM | SGDOneClassSVM | LocalOutlierFactor | Pipeline


class Classifier:
    def __init__(self, occ_algo: str = 'ocsvm', decision_threshold: float = 0.0):
        self.models: list[OCCAlgo | None] = [None for _ in range(12)]
        self.occ_algo = occ_algo
        self.decision_threshold = decision_threshold

        # OCSVM params
        self.nu = 0.06

        # SGD-OCSVM params
        self.gamma = 2.0
        self.random_state = 42

        # LOF params
        self.n_neighbors = 20
        self.contamination = 0.1

    def train(self, data: np.ndarray, month: int):
        match self.occ_algo:
            case 'ocsvm':
                model = OneClassSVM(nu=self.nu)
                model = model.fit(data)
            case 'sgd-ocsvm':
                transform = Nystroem(
                    gamma=self.gamma, random_state=self.random_state, n_components=len(data))
                model = SGDOneClassSVM(
                    nu=self.nu, shuffle=True, fit_intercept=True, random_state=self.random_state, tol=1e-4)
                model = make_pipeline(transform, model).fit(data)
            case 'lof':
                model = LocalOutlierFactor(
                    novelty=True, n_neighbors=self.n_neighbors, contamination=self.contamination)
                model = model.fit(data)
            case _:
                raise Exception('Invalid occ algo')

        self.models[month-1] = model
        LOG('models', self.models)

    def classify(self, data: np.ndarray, month: int) -> np.ndarray:
        model = self.models[month-1]

        assert model != None
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
