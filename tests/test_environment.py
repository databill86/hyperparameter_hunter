##################################################
# Import Own Assets
##################################################
from hyperparameter_hunter.environment import (
    Environment,
    define_holdout_set,
    validate_file_blacklist,
)

##################################################
# Import Miscellaneous Assets
##################################################
import numpy as np
import pandas as pd
import pytest

##################################################
# Import Learning Assets
##################################################
from sklearn.datasets import load_breast_cancer
from sklearn.metrics import accuracy_score


##################################################
# Dummy Objects for Testing
##################################################
def get_breast_cancer_data():
    data = load_breast_cancer()
    df = pd.DataFrame(data=data.data, columns=data.feature_names)
    df["diagnosis"] = data.target
    return df


def get_holdout_set(train, target_column):
    # Hello, I am a test comment
    return train, train.copy()


def args_ids_for(scenarios):
    return dict(argvalues=scenarios, ids=[f"{_}" for _ in range(len(scenarios))])


train_dataset = get_breast_cancer_data()
cv_params = dict(n_splits=5, shuffle=True, random_state=32)
repeated_cv_params = dict(n_splits=5, n_repeats=2, random_state=32)

default_env_params = dict(
    train_dataset=train_dataset,
    environment_params_path=None,
    results_path="hyperparameter_hunter/__TEST__HyperparameterHunterAssets__",
    holdout_dataset=get_holdout_set,
    test_dataset=train_dataset.copy(),
    target_column="diagnosis",
    do_predict_proba=False,
    prediction_formatter=None,
    metrics_params=dict(
        metrics_map=dict(roc="roc_auc_score", f1="f1_score", acc="accuracy_score"),
        in_fold="all",
        oof="all",
        holdout="all",
    ),
    random_seeds=None,
    runs=3,
    cross_validation_type="StratifiedKFold",
    verbose=True,
    file_blacklist=None,
    reporting_params=dict(add_frame=False),
    cross_validation_params=repeated_cv_params,
)

##################################################
# Environment Initialization Scenarios
##################################################
scenarios_cv_params = [
    [repeated_cv_params, "LQuf_lTfr1xa9-JdjXpEVm9_b7oFZrLjzKNWESXeHlU="],
    [cv_params, "2YQ5gqPa98rQqClDOR82ubsp9qXiKlz4VqsONOcze3Q="],
]
scenarios_metrics_map = [
    [
        dict(roc="roc_auc_score", acc="accuracy_score"),
        "nqICREczftTR3kphbkIXDEZup5utQmhqeyndjZ5lfqQ=",
    ],
    [
        dict(
            roc="roc_auc_score",
            f1="f1_score",
            acc=lambda _t, _p: accuracy_score(_t, np.clip(np.round(_p), 0, 1)),
        ),
        "thDRj-vOjsLpplfaZl5qY8U6jRVeIoNbQHwXtWPhUTk=",
    ],
]
scenarios_cross_experiment_params = [
    [10, "StratifiedKFold", repeated_cv_params, "fFiOUZCDoqJ6NisIZ9_ZjGd4pVbCO-aXYzMvYzq1OAk="],
    [3, "KFold", cv_params, "Kgqa7eSV52fPYVYeF6aIySKz6-QBRRShWklcoyePgBg="],
]


@pytest.mark.parametrize(["_cv_params", "expected"], **args_ids_for(scenarios_cv_params))
def test_environment_init_cv_params(_cv_params, expected):
    env = Environment(**dict(default_env_params, **dict(cross_validation_params=_cv_params)))
    assert env == expected


@pytest.mark.parametrize(["metrics", "expected"], **args_ids_for(scenarios_metrics_map))
def test_environment_init_metrics(metrics, expected):
    env = Environment(
        **dict(
            default_env_params,
            **dict(
                metrics_params=dict(metrics_map=metrics, in_fold="all", oof="all", holdout="all")
            ),
        )
    )
    assert env == expected


@pytest.mark.parametrize(
    ["runs", "cv_type", "_cv_params", "expected"], **args_ids_for(scenarios_cross_experiment_params)
)
def test_environment_init_cross_experiment_params(runs, cv_type, _cv_params, expected):
    env = Environment(
        **dict(
            default_env_params,
            **dict(runs=runs, cross_validation_type=cv_type, cross_validation_params=_cv_params),
        )
    )
    assert env == expected


##################################################
# `define_holdout_set` Scenarios
##################################################
def test_define_holdout_set_str(monkeypatch):
    dummy_df = pd.DataFrame(dict(a=[0, 1], b=[2, 3]))

    # noinspection PyUnusedLocal
    def mock_pandas_read_csv(*args, **kwargs):
        return dummy_df

    monkeypatch.setattr(pd, "read_csv", mock_pandas_read_csv)
    assert define_holdout_set(pd.DataFrame(dict(a=[4], b=[5])), "foo", "x")[1].equals(dummy_df)


@pytest.mark.parametrize("holdout_set", [42, np.array([[0, 1], [2, 3]])])
def test_define_holdout_set_type_error(holdout_set):
    with pytest.raises(TypeError, match="holdout_set must be None, DataFrame, callable, or str,.*"):
        define_holdout_set(pd.DataFrame(), holdout_set, "target")


def test_define_holdout_set_file_not_found_error():
    with pytest.raises(FileNotFoundError):
        define_holdout_set(pd.DataFrame(), "foo", "target")


@pytest.mark.parametrize("holdout_set", [dict(), dict(a=[0], c=[2]), dict(a=[0])])
def test_define_holdout_set_value_error(holdout_set):
    with pytest.raises(ValueError, match="Mismatched columns.*"):
        define_holdout_set(pd.DataFrame(dict(a=[0, 1], b=[2, 3])), pd.DataFrame(holdout_set), "x")


##################################################
# `validate_file_blacklist` Scenarios
##################################################
@pytest.mark.parametrize(
    ["blacklist", "expected"],
    [["ALL", "ALL"], [["current_heartbeat"], ["current_heartbeat", "heartbeat"]]],
)
def test_validate_file_blacklist(blacklist, expected):
    assert validate_file_blacklist(blacklist) == expected


@pytest.mark.parametrize("blacklist", ["foo", 42, dict(a=17, b=18)])
def test_validate_file_blacklist_type_error_list(blacklist):
    with pytest.raises(TypeError, match="Expected blacklist to be a list, not:.*"):
        validate_file_blacklist(blacklist)


@pytest.mark.parametrize("blacklist", [["foo", None], [1], [["foo"]], [dict(a="foo")]])
def test_validate_file_blacklist_type_error_contents(blacklist):
    with pytest.raises(TypeError, match="Expected blacklist contents to be strings, not:.*"):
        validate_file_blacklist(blacklist)


@pytest.mark.parametrize("blacklist", [["description", "foo"], ["foo"]])
def test_validate_file_blacklist_value_error(blacklist):
    with pytest.raises(ValueError, match="Invalid blacklist value: foo.*"):
        validate_file_blacklist(blacklist)
