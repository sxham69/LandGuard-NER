from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "ml" / "landslide_model.joblib"

FEATURES = ["rainfall24","rainfall72","soil","slope","elevation","ndvi","road_dist","history"]

def build_dataset(n=8000, seed=26001):
    rng = np.random.default_rng(seed)
    rainfall24 = rng.gamma(2.2,22,n).clip(0,300)
    rainfall72 = (rainfall24*2.1+rng.gamma(2,30,n)).clip(0,600)
    soil = rng.normal(58,18,n).clip(10,100)
    slope = rng.normal(28,11,n).clip(2,65)
    elevation = rng.normal(1200,650,n).clip(50,3500)
    ndvi = rng.beta(5,2,n)
    road_dist = rng.exponential(220,n).clip(5,1500)
    history = rng.gamma(1.8,1.1,n).clip(0,12)

    # Synthetic label-generation function for demo only.
    latent = (
        .020*rainfall24 + .009*rainfall72 + .035*soil +
        .070*slope + .22*history - 1.8*ndvi -
        .0005*road_dist + rng.normal(0,1.1,n)
    )
    y = pd.cut(latent, [-np.inf,4.0,6.3,np.inf], labels=[0,1,2]).astype(int)

    X = pd.DataFrame({
        "rainfall24":rainfall24,"rainfall72":rainfall72,"soil":soil,
        "slope":slope,"elevation":elevation,"ndvi":ndvi,
        "road_dist":road_dist,"history":history
    })
    return X, y

def train():
    X,y=build_dataset()
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,random_state=26001,stratify=y)
    model=RandomForestClassifier(
        n_estimators=300,max_depth=12,min_samples_leaf=3,
        random_state=26001,class_weight="balanced_subsample"
    )
    model.fit(Xtr,ytr)
    pred=model.predict(Xte)
    acc=accuracy_score(yte,pred)
    print("Validation accuracy:", round(acc,4))
    print(classification_report(yte,pred))
    joblib.dump(model,MODEL_PATH)
    return acc

if __name__ == "__main__":
    train()
