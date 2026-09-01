from backend.risk_engine import predict

def test_prediction_contract():
    f = {
        "rainfall24": 100, "rainfall72": 250, "soil": 80, "slope": 40,
        "elevation": 1200, "ndvi": .5, "road_dist": 100, "history": 5
    }
    p = predict(f)
    assert p["risk_level"] in {"LOW","MODERATE","HIGH","CRITICAL"}
    assert 0 <= p["risk_score"] <= 100
    assert 0 <= p["confidence"] <= 1
    assert 0 <= p["operational_priority"] <= 100
