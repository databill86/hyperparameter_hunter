##################################################
# Import Own Assets
##################################################
from hyperparameter_hunter import Environment, CVExperiment, Real, Integer, Categorical
from hyperparameter_hunter import BayesianOptimization
from hyperparameter_hunter.utils.learning_utils import get_breast_cancer_data
from hyperparameter_hunter.utils.test_utils import has_experiment_result_file

##################################################
# Import Miscellaneous Assets
##################################################
import pytest

try:
    lightgbm = pytest.importorskip("lightgbm")
except Exception:
    raise

##################################################
# Import Learning Assets
##################################################
from lightgbm import LGBMClassifier
from sklearn.metrics import f1_score

##################################################
# Global Settings
##################################################
assets_dir = "hyperparameter_hunter/__TEST__HyperparameterHunterAssets__"
# assets_dir = "hyperparameter_hunter/HyperparameterHunterAssets"


##################################################
# Environment Fixtures
##################################################
@pytest.fixture(scope="function", autouse=False)
def env_0():
    return Environment(
        train_dataset=get_breast_cancer_data(target="diagnosis"),
        root_results_path=assets_dir,
        target_column="diagnosis",
        metrics_map=dict(
            roc_auc="roc_auc_score",
            f1=f1_score,
            f1_micro=lambda y_true, y_pred: f1_score(y_true, y_pred, average="micro"),
            f1_macro=lambda y_true, y_pred: f1_score(y_true, y_pred, average="macro"),
        ),
        cross_validation_type="KFold",
        cross_validation_params=dict(n_splits=2, shuffle=True, random_state=42),
        verbose=1,
    )


##################################################
# Experiment Fixtures
##################################################
@pytest.fixture(scope="function", autouse=False)
def exp_lgb_0():
    return CVExperiment(
        model_initializer=LGBMClassifier,
        model_init_params=dict(
            boosting_type="gbdt",
            num_leaves=5,
            max_depth=5,
            min_child_samples=1,
            subsample=0.5,
            verbose=-1,
        ),
    )


##################################################
# Optimization Protocol Fixtures
##################################################
@pytest.fixture(scope="function", autouse=False, params=[None, "f1_micro", "f1", "f1_macro"])
def opt_lgb_0(request):
    optimizer = BayesianOptimization(target_metric=request.param, iterations=2, random_state=32)
    optimizer.set_experiment_guidelines(
        model_initializer=LGBMClassifier,
        model_init_params=dict(
            boosting_type=Categorical(["gbdt", "dart"]),
            num_leaves=Integer(2, 8),
            max_depth=5,
            min_child_samples=1,
            subsample=Real(0.4, 0.7),
            verbose=-1,
        ),
    )
    optimizer.go()
    yield optimizer

    assert optimizer.target_metric == ("oof", (request.param or "roc_auc"))
    # lb = pd.read_csv(
    #     # Path(assets_dir) / "HyperparameterHunterAssets" / "Leaderboards" / "GlobalLeaderboard.csv",
    #     Path(assets_dir) / "Leaderboards" / "GlobalLeaderboard.csv",
    # )
    # assert lb.columns[0] == f"oof_{request.param}"


def test_lgb_0(env_0, exp_lgb_0, opt_lgb_0):
    assert len(opt_lgb_0.similar_experiments) > 0

    for similar_experiment in opt_lgb_0.similar_experiments:
        assert has_experiment_result_file(
            assets_dir, similar_experiment[2], ["Descriptions", "Heartbeats", "PredictionsOOF"]
        )
