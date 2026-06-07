---
title: Classificador Fraude PT-BR
emoji: 🕵️‍♂️
colorFrom: blue
colorTo: red
sdk: docker
pinned: false
---

# API de Classificacao de Fraudes em PT-BR

## 1. Introducao formal

Este projeto define uma API para classificacao de mensagens potencialmente fraudulentas em portugues brasileiro. A proposta tecnica consiste em substituir regras estaticas por inferencia contextual baseada em Processamento de Linguagem Natural (NLP), preservando um mecanismo deterministico de fallback heuristico para manter disponibilidade operacional quando o modelo principal nao estiver disponivel ou quando a inferencia neural nao puder ser executada.

A classe central de inferencia e `FraudClassifier`, cuja interface publica e `predict(text: str) -> dict`. O retorno segue um contrato simples e auditavel, composto pelas chaves `fraude` (`bool`), `confianca` (`float`) e `motivo` (`str`). Essa estrutura permite integrar a classificacao a servicos consumidores sem expor detalhes internos do modelo, mantendo rastreabilidade minima da decisao por meio do campo `motivo`.

O modelo padrao adotado e `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli`, utilizado para classificacao zero-shot de texto em um enquadramento de Natural Language Inference (NLI) multilingue via Hugging Face Transformers. A API HTTP e implementada com FastAPI, validacao de entrada por Pydantic, execucao ASGI por Uvicorn e empacotamento em Docker com base `python:3.11-slim`, direcionado ao deploy em Hugging Face Spaces na porta `7860`.

## 2. Metodologia (Arquitetura)

### Arquitetura geral

A arquitetura do projeto e organizada em quatro camadas principais:

1. Camada de API HTTP, responsavel por expor as rotas `GET /health` e `POST /predict`.
2. Camada de validacao, baseada em Pydantic, com payload estrito contendo o campo `texto_mensagem`.
3. Camada de inferencia, representada pela classe `FraudClassifier` e pelo metodo `predict(text: str)`.
4. Camada de disponibilidade operacional, composta por heuristicas deterministicas em portugues brasileiro acionadas como fallback.

O ciclo de vida da aplicacao utiliza o mecanismo de `lifespan` do FastAPI para carregar uma unica instancia singleton do classificador. Essa decisao evita recarregamentos repetidos do modelo a cada requisicao, reduz latencia media apos a inicializacao e centraliza o estado de inferencia em um componente unico da aplicacao.

### Justificativa do uso de Transformer/NLI multilingue

Mensagens fraudulentas em portugues brasileiro apresentam variacao lexical, informalidade, omissao de contexto e estrategias de engenharia social que podem escapar de regras fixas. O uso de um modelo Transformer multilingue treinado para NLI permite avaliar a relacao semantica entre a mensagem de entrada e hipoteses de classificacao relacionadas a fraude, viabilizando classificacao zero-shot sem depender exclusivamente de um conjunto supervisionado local.

O modelo `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli` foi selecionado por combinar uma arquitetura baseada em DeBERTa multilingue com ajuste para tarefas de NLI e XNLI. Essa abordagem e adequada ao objetivo do projeto porque permite inferencia contextual sobre textos em portugues brasileiro, mantendo flexibilidade para novas formulacoes de golpes sem exigir retreinamento imediato.

O runtime de ML e composto por Python, Hugging Face Transformers, PyTorch e execucao em CPU por padrao. A execucao em CPU reduz requisitos de infraestrutura e favorece compatibilidade com ambientes de deploy simples, como containers e Hugging Face Spaces.

### Justificativa do uso de FastAPI

FastAPI foi adotado por oferecer uma interface HTTP objetiva, tipagem explicita, suporte nativo a validacao declarativa com Pydantic e compatibilidade direta com servidores ASGI, como Uvicorn. Para este projeto, esses elementos sao relevantes porque o contrato da API precisa ser estrito, previsivel e facil de consumir por sistemas externos.

A rota `GET /health` oferece verificacao operacional simples, enquanto `POST /predict` concentra o contrato de classificacao. A separacao entre saude da aplicacao e inferencia evita que consumidores precisem acionar o modelo para apenas verificar disponibilidade do servico.

### Justificativa do fallback heuristico

Embora o modelo Transformer seja o mecanismo principal de inferencia, a API inclui fallback heuristico deterministico para manter disponibilidade operacional. Esse fallback contempla indicadores recorrentes de fraude em portugues brasileiro, incluindo referencias a Pix, falso boleto, banco, Receita Federal, Correios, bloqueio de conta, urgencia linguistica, solicitacao de credenciais, links suspeitos e comunicacao informal via WhatsApp.

O fallback nao substitui a inferencia contextual, mas atua como mecanismo de continuidade. Em cenarios de falha de carregamento do modelo, indisponibilidade de dependencias, restricoes de memoria ou erro de inferencia, a aplicacao ainda pode retornar uma decisao estruturada com base em sinais linguisticos conhecidos.

## 3. Desenvolvimento do Pre-projeto

O cronograma abaixo organiza o pre-projeto em 24 meses, indicando os elementos ja implementados conforme os metadados disponiveis.

| Mes | Atividade | Situacao |
| --- | --- | --- |
| 1 | Definicao do problema, escopo da API e foco em mensagens de fraude em portugues brasileiro. | Implementado |
| 2 | Definicao do contrato publico de inferencia `predict(text: str) -> dict`. | Implementado |
| 3 | Escolha da abordagem NLP contextual em substituicao a regras exclusivamente estaticas. | Implementado |
| 4 | Selecao do paradigma zero-shot text classification com NLI multilingue. | Implementado |
| 5 | Selecao do modelo padrao `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli`. | Implementado |
| 6 | Definicao do runtime de ML com Python, Transformers, PyTorch e CPU por padrao. | Implementado |
| 7 | Implementacao da classe de inferencia `FraudClassifier`. | Implementado |
| 8 | Definicao do formato de resposta com `fraude`, `confianca` e `motivo`. | Implementado |
| 9 | Levantamento de heuristicas PT-BR para sinais de fraude. | Implementado |
| 10 | Implementacao do fallback heuristico deterministico. | Implementado |
| 11 | Estruturacao da API HTTP com FastAPI. | Implementado |
| 12 | Definicao da validacao Pydantic com payload estrito `texto_mensagem`. | Implementado |
| 13 | Implementacao da rota `GET /health`. | Implementado |
| 14 | Implementacao da rota `POST /predict`. | Implementado |
| 15 | Configuracao do carregamento singleton do classificador no `lifespan` da aplicacao. | Implementado |
| 16 | Configuracao de execucao ASGI com Uvicorn. | Implementado |
| 17 | Criacao do container Docker baseado em `python:3.11-slim`. | Implementado |
| 18 | Adequacao do container para Hugging Face Spaces, porta `7860` e usuario Linux UID `1000`. | Implementado |
| 19 | Configuracao de CI/CD para sincronizacao da branch `main` com Hugging Face Spaces. | Implementado |
| 20 | Consolidacao da documentacao metodologica inicial do projeto. | Implementado |
| 21 | Planejamento de avaliacao quantitativa com amostras reais ou sinteticas de mensagens PT-BR. | Planejado |
| 22 | Planejamento de metricas de avaliacao, como precisao, revocacao, F1-score e analise de falsos positivos. | Planejado |
| 23 | Planejamento de observabilidade operacional, incluindo latencia, erros de inferencia e acionamento de fallback. | Planejado |
| 24 | Planejamento de evolucao para calibracao de confianca, versionamento de prompts/hipoteses e eventual fine-tuning. | Planejado |

## 4. Uso local e contrato da API

### Execucao local

Instale as dependencias Python do projeto:

```bash
pip install -r requirements.txt
```

Execute a API com Uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 7860
```

A porta `7860` e utilizada por compatibilidade com o deploy alvo em Hugging Face Spaces.

### Execucao com Docker

Construa a imagem:

```bash
docker build -t fraud-api-ptbr .
```

Execute o container:

```bash
docker run --rm -p 7860:7860 fraud-api-ptbr
```

### Verificacao de saude

Requisicao:

```http
GET /health
```

Uso com `curl`:

```bash
curl http://localhost:7860/health
```

### Predicao

Requisicao:

```http
POST /predict
Content-Type: application/json
```

Payload:

```json
{
  "texto_mensagem": "Seu Pix foi bloqueado. Acesse o link imediatamente para regularizar sua conta."
}
```

Uso com `curl`:

```bash
curl -X POST "http://localhost:7860/predict" \
  -H "Content-Type: application/json" \
  -d "{\"texto_mensagem\":\"Seu Pix foi bloqueado. Acesse o link imediatamente para regularizar sua conta.\"}"
```

Resposta esperada:

```json
{
  "fraude": true,
  "confianca": 0.0,
  "motivo": "string explicativa da classificacao"
}
```

O campo `confianca` e um valor numerico de ponto flutuante. O campo `motivo` descreve, de forma tecnica e resumida, a razao da classificacao, podendo refletir a inferencia do modelo principal ou o acionamento de heuristicas deterministicas.

### Contrato tecnico

Entrada da rota `POST /predict`:

| Campo | Tipo | Obrigatorio | Descricao |
| --- | --- | --- | --- |
| `texto_mensagem` | `str` | Sim | Texto da mensagem em portugues brasileiro a ser classificada. |

Saida da rota `POST /predict`:

| Campo | Tipo | Descricao |
| --- | --- | --- |
| `fraude` | `bool` | Indica se a mensagem foi classificada como potencialmente fraudulenta. |
| `confianca` | `float` | Escore de confianca associado a classificacao. |
| `motivo` | `str` | Justificativa sintetica da decisao de classificacao. |

## 5. Referencias

```bibtex
@software{fastapi,
  title = {FastAPI},
  author = {Ramirez, Sebastian},
  url = {https://fastapi.tiangolo.com/},
  note = {Web framework for building APIs with Python based on standard type hints}
}
```

```bibtex
@software{pydantic,
  title = {Pydantic},
  author = {Colvin, Samuel and contributors},
  url = {https://docs.pydantic.dev/},
  note = {Data validation using Python type hints}
}
```

```bibtex
@software{uvicorn,
  title = {Uvicorn},
  author = {Encode},
  url = {https://www.uvicorn.org/},
  note = {ASGI web server implementation for Python}
}
```

```bibtex
@inproceedings{wolf2020transformers,
  title = {Transformers: State-of-the-Art Natural Language Processing},
  author = {Wolf, Thomas and Debut, Lysandre and Sanh, Victor and Chaumond, Julien and Delangue, Clement and Moi, Anthony and Cistac, Pierric and Rault, Tim and Louf, Remi and Funtowicz, Morgan and Davison, Joe and Shleifer, Sam and von Platen, Patrick and Ma, Clara and Jernite, Yacine and Plu, Julien and Xu, Canwen and Le Scao, Teven and Gugger, Sylvain and Drame, Mariama and Lhoest, Quentin and Rush, Alexander M.},
  booktitle = {Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing: System Demonstrations},
  year = {2020},
  pages = {38--45},
  publisher = {Association for Computational Linguistics},
  url = {https://aclanthology.org/2020.emnlp-demos.6/}
}
```

```bibtex
@inproceedings{paszke2019pytorch,
  title = {PyTorch: An Imperative Style, High-Performance Deep Learning Library},
  author = {Paszke, Adam and Gross, Sam and Massa, Francisco and Lerer, Adam and Bradbury, James and Chanan, Gregory and Killeen, Trevor and Lin, Zeming and Gimelshein, Natalia and Antiga, Luca and Desmaison, Alban and Kopf, Andreas and Yang, Edward and DeVito, Zachary and Raison, Martin and Tejani, Alykhan and Chilamkurthy, Sasank and Steiner, Benoit and Fang, Lu and Bai, Junjie and Chintala, Soumith},
  booktitle = {Advances in Neural Information Processing Systems},
  volume = {32},
  year = {2019},
  url = {https://papers.neurips.cc/paper_files/paper/2019/hash/bdbca288fee7f92f2bfa9f7012727740-Abstract.html}
}
```

```bibtex
@article{he2021deberta,
  title = {DeBERTa: Decoding-enhanced BERT with Disentangled Attention},
  author = {He, Pengcheng and Liu, Xiaodong and Gao, Jianfeng and Chen, Weizhu},
  journal = {International Conference on Learning Representations},
  year = {2021},
  url = {https://openreview.net/forum?id=XPZIaotutsD}
}
```

```bibtex
@inproceedings{conneau2018xnli,
  title = {XNLI: Evaluating Cross-lingual Sentence Representations},
  author = {Conneau, Alexis and Rinott, Ruty and Lample, Guillaume and Williams, Adina and Bowman, Samuel R. and Schwenk, Holger and Stoyanov, Veselin},
  booktitle = {Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing},
  year = {2018},
  pages = {2475--2485},
  publisher = {Association for Computational Linguistics},
  url = {https://aclanthology.org/D18-1269/}
}
```

```bibtex
@inproceedings{williams2018mnli,
  title = {A Broad-Coverage Challenge Corpus for Sentence Understanding through Inference},
  author = {Williams, Adina and Nangia, Nikita and Bowman, Samuel R.},
  booktitle = {Proceedings of the 2018 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies},
  year = {2018},
  pages = {1112--1122},
  publisher = {Association for Computational Linguistics},
  url = {https://aclanthology.org/N18-1101/}
}
```

```bibtex
@misc{laurer_mdeberta_mnli_xnli,
  title = {mDeBERTa-v3-base-mnli-xnli},
  author = {Laurer, Moritz},
  howpublished = {Hugging Face model repository},
  url = {https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-mnli-xnli},
  note = {Multilingual DeBERTa model fine-tuned for MNLI and XNLI}
}
```

```bibtex
@misc{huggingface_spaces,
  title = {Hugging Face Spaces},
  author = {{Hugging Face}},
  howpublished = {Platform documentation},
  url = {https://huggingface.co/docs/hub/spaces},
  note = {Hosting platform for machine learning applications}
}
```
