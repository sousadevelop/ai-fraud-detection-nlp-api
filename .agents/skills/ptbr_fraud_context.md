---
name: ptbr_fraud_context
description: Fornece heurísticas e terminologia de engenharia social específicas do Brasil para calibração de prompts do LLM.
---

# Contexto de Classificação (PT-BR)
Ao desenhar os prompts internos da API que serão enviados ao LLM para inferência, assuma os seguintes padrões de ataque frequentes no Brasil:
- Falsos boletos ou descontos via "Pix".
- Engenharia social envolvendo "Atualização de segurança do banco", "Malha fina da Receita" ou "Pacote retido nos Correios".
- Uso excessivo de urgência linguística ("Sua conta será bloqueada hoje").

# Ação do Agente
Quando for escrever a lógica de pré-processamento de texto (NLP) ou o *system prompt* interno da API, otimize a extração de entidades considerando gramática informal, abreviações de WhatsApp (vc, tb, blz) e os padrões acima.