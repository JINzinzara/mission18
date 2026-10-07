from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).resolve().parent / "data" / "sentiment_model.joblib"
_model = None


def load_model():
    """모델을 최초 호출에만 읽고, 이 후 보관된 모델을 반환"""
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)

    return _model


def analyze(text: str) -> dict:
    """리뷰의 감성과 긍정 확률을 label, score로 반환"""
    model = load_model()
    predict = float(model.predict_proba([text])[0][1])
    return {"label": "긍정" if predict >= 0.5 else "부정", "score": round(predict, 4)}


if __name__ == "__main__":
    loaded_model = load_model()
    print(loaded_model.classes_)
    print(loaded_model is load_model())
    print(analyze("연출도 좋고 배우 연기가 정말 훌륭했어요"))
    print(analyze("시간이 아깝다. 최악"))
