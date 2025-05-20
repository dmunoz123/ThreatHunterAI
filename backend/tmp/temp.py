import time
from autogluon.tabular import TabularPredictor
import pandas as pd

# load your model and a tiny sample
predictor = TabularPredictor.load(r"..\..\ag-20250412_023747")
df = pd.read_csv("capture_2025-04-22_19-30-17.csv")
X = df.sample(n=10).drop(columns=["bad_packet"], errors="ignore")

start = time.time()
preds = predictor.predict(X)
print("Time:", time.time()-start)
print(preds)
