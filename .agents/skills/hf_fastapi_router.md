---
name: hf_fastapi_router
description: Define o padrão arquitetural obrigatório para carregar modelos do Hugging Face em rotas FastAPI.
---

# Regras de Execução (FastAPI + Transformers)
1. NUNCA instancie o pipeline do modelo dentro da função da rota.
2. O modelo LLM deve ser carregado APENAS durante o evento de `lifespan` do FastAPI (startup) e anexado ao `app.state`.
3. Utilize `pydantic.BaseModel` estrito para o payload de entrada, contendo apenas o campo `texto_mensagem` (string).
4. O retorno da rota `/predict` deve ser obrigatoriamente um JSON com a estrutura: `{"fraude": boolean, "confianca": float, "motivo": string}`.
5. Se for sugerir código, retorne apenas o trecho modificado. Sem explicações verbosas.