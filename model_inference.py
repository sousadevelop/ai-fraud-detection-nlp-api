import re
import unicodedata
from typing import Any, Dict, List, Optional, Tuple


class FraudClassifier:
    DEFAULT_MODEL_NAME = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"

    def __init__(
        self,
        model_name: Optional[str] = None,
        score_threshold: float = 0.62,
        heuristic_threshold: float = 0.46,
        max_length: int = 256,
    ) -> None:
        self.model_name = model_name or self.DEFAULT_MODEL_NAME
        self.score_threshold = score_threshold
        self.heuristic_threshold = heuristic_threshold
        self.max_length = max_length
        self.pipeline = None
        self.pipeline_task: Optional[str] = None
        self.model_error: Optional[str] = None
        self._candidate_labels = [
            "fraude, phishing ou golpe",
            "mensagem legitima",
        ]
        self._load_pipeline()

    def predict(self, text: str) -> dict:
        original_text = text if isinstance(text, str) else ""
        normalized_text = self._normalize_text(original_text)

        if not normalized_text:
            return {
                "fraude": False,
                "confianca": 0.0,
                "motivo": "Texto vazio ou sem conteudo analisavel.",
            }

        heuristic_score, heuristic_reasons = self._heuristic_analysis(normalized_text)
        model_score = self._model_score(original_text)

        risk_score = heuristic_score
        if model_score is not None:
            risk_score = min(0.99, (0.65 * model_score) + (0.35 * heuristic_score))

        fraude = risk_score >= self.score_threshold or heuristic_score >= 0.72
        confidence = risk_score if fraude else (1.0 - risk_score)
        confidence = round(max(0.0, min(0.99, confidence)), 4)
        motivo = self._build_reason(
            fraude=fraude,
            risk_score=risk_score,
            heuristic_score=heuristic_score,
            heuristic_reasons=heuristic_reasons,
            model_score=model_score,
        )

        return {
            "fraude": fraude,
            "confianca": confidence,
            "motivo": motivo,
        }

    def _load_pipeline(self) -> None:
        try:
            from transformers import pipeline
        except Exception as exc:  # pragma: no cover
            self.model_error = f"transformers indisponivel: {exc}"
            return

        try:
            self.pipeline = pipeline(
                task="zero-shot-classification",
                model=self.model_name,
                tokenizer=self.model_name,
                device=-1,
            )
            self.pipeline_task = "zero-shot-classification"
            return
        except Exception as exc:
            self.model_error = str(exc)

        try:
            self.pipeline = pipeline(
                task="text-classification",
                model=self.model_name,
                tokenizer=self.model_name,
                device=-1,
                truncation=True,
            )
            self.pipeline_task = "text-classification"
            self.model_error = None
        except Exception as exc:  # pragma: no cover
            self.pipeline = None
            self.pipeline_task = None
            self.model_error = str(exc)

    def _model_score(self, text: str) -> Optional[float]:
        if self.pipeline is None or not text.strip():
            return None

        truncated_text = text.strip()[:4000]

        try:
            if self.pipeline_task == "zero-shot-classification":
                result = self.pipeline(
                    truncated_text,
                    candidate_labels=self._candidate_labels,
                    hypothesis_template="Este texto e {}.",
                    multi_label=False,
                    truncation=True,
                    max_length=self.max_length,
                )
                score_by_label = {
                    label.lower(): float(score)
                    for label, score in zip(result["labels"], result["scores"])
                }
                return max(
                    0.0,
                    min(
                        0.99,
                        score_by_label.get(self._candidate_labels[0].lower(), 0.0),
                    ),
                )

            result = self.pipeline(
                truncated_text,
                truncation=True,
                max_length=self.max_length,
                top_k=None,
            )

            if isinstance(result, list) and result and isinstance(result[0], dict):
                return self._score_text_classification(result)
        except Exception:
            return None

        return None

    def _score_text_classification(self, outputs: List[Dict[str, Any]]) -> float:
        fraud_terms = (
            "fraud",
            "phish",
            "spam",
            "scam",
            "malicious",
            "golpe",
            "suspect",
            "risk",
        )
        legit_terms = (
            "legit",
            "safe",
            "ham",
            "normal",
            "benign",
            "nao fraude",
            "legitimo",
        )

        fraud_score = 0.0
        legit_score = 0.0

        for item in outputs:
            label = str(item.get("label", "")).lower()
            score = float(item.get("score", 0.0))

            if any(term in label for term in fraud_terms):
                fraud_score = max(fraud_score, score)
            elif any(term in label for term in legit_terms):
                legit_score = max(legit_score, score)

        if fraud_score == 0.0 and legit_score == 0.0:
            top_score = float(outputs[0].get("score", 0.0))
            top_label = str(outputs[0].get("label", "")).lower()
            if "1" in top_label or "positive" in top_label:
                fraud_score = top_score
            else:
                fraud_score = 1.0 - top_score

        if legit_score > 0.0:
            fraud_score = max(fraud_score, 1.0 - legit_score)

        return max(0.0, min(0.99, fraud_score))

    def _heuristic_analysis(self, normalized_text: str) -> Tuple[float, List[str]]:
        categories: List[Tuple[str, float, List[str]]] = [
            (
                "Pix",
                0.17,
                [r"\bpix\b", r"\bchave pix\b", r"\bqr ?code\b", r"\bcomprovante\b"],
            ),
            (
                "falso boleto",
                0.16,
                [r"\bboleto\b", r"\b2a via\b", r"\bsegunda via\b", r"\bvencid[oa]\b"],
            ),
            (
                "banco",
                0.12,
                [
                    r"\bbanco\b",
                    r"\bconta\b",
                    r"\bagencia\b",
                    r"\bcaixa economica\b",
                    r"\bbradesco\b",
                    r"\bitau\b",
                    r"\bsantander\b",
                    r"\bnubank\b",
                ],
            ),
            (
                "Receita Federal",
                0.13,
                [r"\breceita federal\b", r"\bcpf\b", r"\bimposto\b", r"\brestituicao\b"],
            ),
            (
                "Correios",
                0.13,
                [r"\bcorreios\b", r"\bencomenda\b", r"\btaxa\b", r"\balfandeg[ao]\b"],
            ),
            (
                "bloqueio de conta",
                0.15,
                [
                    r"\bbloquei[oa]\b",
                    r"\bsuspens[ao]\b",
                    r"\bdesativad[ao]\b",
                    r"\bseguranca\b",
                    r"\bvalidacao cadastral\b",
                ],
            ),
            (
                "urgencia",
                0.12,
                [
                    r"\burgente\b",
                    r"\bimediatament[ea]\b",
                    r"\bagora\b",
                    r"\bultim[ao]s? horas\b",
                    r"\bevite\b",
                    r"\bnao perca\b",
                ],
            ),
            (
                "WhatsApp informal",
                0.10,
                [
                    r"\bwhats(?:app)?\b",
                    r"\bzap\b",
                    r"\boi[,! ]",
                    r"\bola[,! ]",
                    r"\bme chama\b",
                    r"\bresponde aqui\b",
                ],
            ),
            (
                "pedido de credencial",
                0.16,
                [
                    r"\bsenha\b",
                    r"\btoken\b",
                    r"\bcodigo\b",
                    r"\bcodigo sms\b",
                    r"\bconfirm(?:e|a)\s+seus dados\b",
                    r"\bcpf\b.*\bsenha\b",
                ],
            ),
            (
                "link suspeito",
                0.14,
                [
                    r"https?://",
                    r"\bbit\.ly\b",
                    r"\btinyurl\b",
                    r"\bcutt\.ly\b",
                    r"\bclique aqui\b",
                    r"\bacess[ea] o link\b",
                ],
            ),
        ]

        score = 0.0
        reasons: List[str] = []
        matched_labels = set()

        for label, weight, patterns in categories:
            if any(re.search(pattern, normalized_text) for pattern in patterns):
                score += weight
                reasons.append(label)
                matched_labels.add(label)

        if {"Pix", "urgencia"} <= matched_labels:
            score += 0.09
        if {"banco", "bloqueio de conta"} <= matched_labels:
            score += 0.10
        if {"Receita Federal", "link suspeito"} <= matched_labels:
            score += 0.08
        if "Correios" in matched_labels and re.search(r"\btaxa\b", normalized_text):
            score += 0.06
        if {"WhatsApp informal", "Pix"} <= matched_labels:
            score += 0.08
        if {"pedido de credencial", "link suspeito"} <= matched_labels:
            score += 0.11

        if re.search(r"\b(copie|transfira|pague|regularize|atualize)\b", normalized_text):
            score += 0.06
        if re.search(r"\b(valor|r\$ ?\d+|pagamento)\b", normalized_text):
            score += 0.05

        unique_reasons = reasons[:3]
        return min(0.99, score), unique_reasons

    def _build_reason(
        self,
        fraude: bool,
        risk_score: float,
        heuristic_score: float,
        heuristic_reasons: List[str],
        model_score: Optional[float],
    ) -> str:
        if heuristic_reasons:
            signal_summary = ", ".join(heuristic_reasons)
        else:
            signal_summary = "poucos sinais de engenharia social"

        if fraude:
            if model_score is None:
                return f"Fallback heuristico indicou risco elevado por: {signal_summary}."
            return f"Indicios de fraude detectados por: {signal_summary}."

        if heuristic_score >= self.heuristic_threshold:
            return f"Ha sinais suspeitos ({signal_summary}), mas abaixo do limiar final."

        if model_score is None and self.model_error:
            return "Classificacao heuristica sem sinais fortes de golpe nesta mensagem."

        if risk_score < 0.25:
            return "Baixa presenca de linguagem tipica de golpe ou phishing."

        return "Analise combinada sem evidencia suficiente para marcar como fraude."

    @staticmethod
    def _normalize_text(text: str) -> str:
        lowered = text.lower().strip()
        without_accents = unicodedata.normalize("NFKD", lowered)
        without_accents = "".join(
            char for char in without_accents if not unicodedata.combining(char)
        )
        return re.sub(r"\s+", " ", without_accents)
