from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from pydantic import BaseModel, ConfigDict

from model_inference import FraudClassifier


class PredictPayload(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    texto_mensagem: str


class PredictResponse(BaseModel):
    fraude: bool
    confianca: float
    motivo: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.classifier = FraudClassifier()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictPayload, request: Request) -> dict[str, Any]:
    classifier: FraudClassifier = request.app.state.classifier
    prediction = classifier.predict(payload.texto_mensagem)

    return {
        "fraude": prediction["fraude"],
        "confianca": prediction["confianca"],
        "motivo": prediction["motivo"],
    }
