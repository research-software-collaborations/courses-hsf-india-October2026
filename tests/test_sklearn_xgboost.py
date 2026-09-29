import sklearn
import xgboost as xgb
import numpy as np

print(f"scikit-learn version: {sklearn.__version__}")
print(f"XGBoost version: {xgb.__version__}")

rng = np.random.default_rng(42)
X = rng.standard_normal((200, 10))
y = (X[:, 0] + X[:, 1] > 0).astype(int)

# scikit-learn
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score
clf = GradientBoostingClassifier(n_estimators=20, random_state=42)
clf.fit(X, y)
acc = accuracy_score(y, clf.predict(X))
print(f"sklearn GradientBoosting OK, train accuracy: {acc:.3f}")

# xgboost — try GPU first, fall back to CPU
for device in ("cuda", "cpu"):
    try:
        dtrain = xgb.DMatrix(X, label=y)
        params = {"max_depth": 3, "objective": "binary:logistic", "device": device}
        booster = xgb.train(params, dtrain, num_boost_round=10, verbose_eval=False)
        preds = (booster.predict(dtrain) > 0.5).astype(int)
        acc = accuracy_score(y, preds)
        print(f"XGBoost OK on {device}, train accuracy: {acc:.3f}")
        break
    except xgb.core.XGBoostError as e:
        print(f"XGBoost {device} unavailable ({e}), trying CPU")

print("PASS: sklearn + xgboost")
