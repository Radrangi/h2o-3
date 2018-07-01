import xgboost as xgb
import time
import random

from h2o.estimators.xgboost import *
from tests import pyunit_utils

'''
The goal of this test is to compare the results of H2OXGBoost and natibve XGBoost for binomial classification.
The dataset contains only enum columns.
'''
def comparison_test():
    assert H2OXGBoostEstimator.available() is True
    runSeed = random.randint(1, 1073741824)
    ntrees = 10
    h2oParamsS = {"ntrees":ntrees, "max_depth":4, "seed":runSeed, "learn_rate":0.7, "col_sample_rate_per_tree" : 0.9,
                  "min_rows" : 5, "score_tree_interval": ntrees+1, "dmatrix_type":"sparse", "tree_method": "exact", "backend": "cpu"}
    nativeParam = {'colsample_bytree': h2oParamsS["col_sample_rate_per_tree"],
                   'tree_method': 'exact',
                   'seed': h2oParamsS["seed"],
                   'booster': 'gbtree',
                   'objective': 'binary:logistic',
                   'lambda': 0.0,
                   'eta': h2oParamsS["learn_rate"],
                   'grow_policy': 'depthwise',
                   'alpha': 0.0,
                   'subsample': 1.0,
                   'colsample_bylevel': 1.0,
                   'max_delta_step': 0.0,
                   'min_child_weight': h2oParamsS["min_rows"],
                   'gamma': 0.0,
                   'max_depth': h2oParamsS["max_depth"]}

    nrows=10000

    trainFile = pyunit_utils.genTrainFrame(nrows, 0, enumCols=10, enumFactors=2, miscfrac=0.5)       # load in dataset and add response column
    print(trainFile)
    myX = trainFile.names
    y='response'
    myX.remove(y)
    nativeTrain = pyunit_utils.convertH2OFrameToDMatrixSparse(trainFile, y, enumCols=myX)

    h2oModelS = H2OXGBoostEstimator(**h2oParamsS)
    # gather, print and save performance numbers for h2o model
    h2oModelS.train(x=myX, y=y, training_frame=trainFile)
    h2oTrainTimeS = h2oModelS._model_json["output"]["run_time"]
    time1 = time.time()
    h2oPredictS = h2oModelS.predict(trainFile)
    h2oPredictTimeS = time.time()-time1

    # train the native XGBoost

    nativeModel = xgb.train(params=nativeParam,
                            dtrain=nativeTrain, num_boost_round=10)
    nativeTrainTime = time.time()-time1
    time1=time.time()
    nativePred = nativeModel.predict(data=nativeTrain, ntree_limit=ntrees)
    nativeScoreTime = time.time()-time1

    print("Comparing H2OXGBoost results with native XGBoost result when DMatrix is set to sparse.....")
    pyunit_utils.summarizeResult_binomial(h2oPredictS, nativePred, h2oTrainTimeS, nativeTrainTime, h2oPredictTimeS,
                                          nativeScoreTime, tolerance=1e-6)


if __name__ == "__main__":
    pyunit_utils.standalone_test(comparison_test)
else:
    comparison_test()
