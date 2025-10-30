# AI Agent Perplexity 🤖

Um agente de IA inteligente que realiza pesquisa automatizada na web e gera relatórios abrangentes usando LangGraph, OpenAI e Tavily.

## 📖 Descrição

Este projeto implementa um sistema de agentes de IA que funciona como uma versão alternativa do Perplexity AI. O sistema recebe uma pergunta do usuário e:

1. **Gera queries de pesquisa** inteligentes baseadas na pergunta
2. **Pesquisa na web** usando a API Tavily para cada query
3. **Processa e sintetiza** os resultados encontrados
4. **Gera um relatório final** técnico e abrangente em português brasileiro

## 🏗️ Arquitetura

O projeto utiliza **LangGraph** para criar um fluxo de trabalho em grafo com os seguintes nós:

```
┌─────────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│  build_first_queries │───▶│   spawn_researchers   │───▶│   single_search     │
│                     │    │                      │    │   (paralelo)        │
└─────────────────────┘    └──────────────────────┘    └─────────────────────┘
                                                                    │
                                                                    ▼
                                                        ┌─────────────────────┐
                                                        │   final_writer      │
                                                        │                     │
                                                        └─────────────────────┘
```

### Componentes Principais

- **LLMs**: GPT-4o-mini e o3-mini (OpenAI)
- **Pesquisa Web**: Tavily API
- **Orquestração**: LangGraph
- **Estados**: Pydantic BaseModel
- **Visualização**: Matplotlib para o grafo

## 🚀 Funcionalidades

- ✅ Geração automática de queries de pesquisa
- ✅ Pesquisa paralela na web
- ✅ Extração e síntese de conteúdo
- ✅ Geração de relatório técnico em português
- ✅ Referências automáticas com links
- ✅ Logging detalhado do processo
- ✅ Visualização do grafo de estados

## 🛠️ Instalação

### Pré-requisitos

- Python >= 3.12
- Conta OpenAI (para API keys)
- Conta Tavily (para pesquisa web)

### Setup

1. **Clone o repositório**

```bash
git clone <url-do-repositorio>
cd ai-agent-perpexity
```

2. **Instale as dependências**

```bash
# Usando uv (recomendado)
uv sync

# Ou usando pip
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto:

```env
OPENAI_API_KEY=sua_chave_openai_aqui
TAVILY_API_KEY=sua_chave_tavily_aqui
```

## 📊 Uso

### Execução Básica

```bash
# Usando uv
uv run graph.py

# Ou diretamente
python graph.py
```

O programa solicitará uma pergunta e gerará um relatório detalhado.

### Exemplo de Uso

```
💬 Por favor, insira o tópico para pesquisa e relatório:
> Como a IA está transformando o setor de seguros em 2025?

🤖 Gerando queries de pesquisa...
🔍 Pesquisando na web...
✍️ Criando relatório final...
💾 Salvando em final_report.txt
```

### Visualização do Grafo

```python
# Para gerar e visualizar o grafo
from graph import graph
import matplotlib.pyplot as plt

# O grafo será salvo como graph_visualization.png
```

## 📁 Estrutura do Projeto

```
ai-agent-perpexity/
├── graph.py                 # Lógica principal do grafo
├── prompt.py               # Templates de prompts
├── schemas.py              # Modelos Pydantic
├── pyproject.toml          # Configuração do projeto
├── .env                    # Variáveis de ambiente (criar)
├── final_report.txt        # Relatório gerado (saída)
├── graph_visualization.png # Visualização do grafo
└── README.md              # Este arquivo
```

## 🔧 Configuração

### Modelos LLM

O projeto está configurado para usar:

- **gpt-4o-mini**: Para processamento geral e síntese
- **o3-mini**: Para raciocínio final e geração do relatório

Você pode modificar os modelos em `graph.py`:

```python
llm = ChatOpenAI(model_name="gpt-4o-mini")
reasoning_llm = ChatOpenAI(model_name="o3-mini")
```

### Parâmetros de Pesquisa

- **Número de queries**: 3-5 (configurável em `prompt.py`)
- **Resultados por query**: 1 (configurável em `graph.py`)
- **Tamanho do relatório**: 500-800 palavras

## 📝 Exemplo de Saída

O sistema gera relatórios estruturados como este:

```markdown
Para 2025, a aplicação de agentes de Inteligência Artificial (IA) em empresas de seguros representa uma transformação profunda...

[Conteúdo técnico detalhado com dados e fatos]

References:
[1] - [Título do artigo](https://exemplo.com)
[2] - [Outro título](https://exemplo2.com)
```

## 🐛 Solução de Problemas

### Erro de API Key

```
❌ ERRO: OpenAI API key não configurada
```

**Solução**: Verifique se o arquivo `.env` está configurado corretamente.

### Erro de Conexão Tavily

```
❌ ERRO: Falha na pesquisa Tavily
```

**Solução**: Verifique sua chave Tavily e conexão com a internet.

### Dependências

```bash
# Reinstalar dependências
uv sync --force

# Ou
pip install --force-reinstall -r requirements.txt
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add: Amazing Feature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 🙏 Agradecimentos

- [LangChain](https://langchain.com/) pela framework de IA
- [Tavily](https://tavily.com/) pela API de pesquisa web
- [OpenAI](https://openai.com/) pelos modelos LLM
- Comunidade Python pelo ecossistema incrível

---

**Developed with ❤️ using Python and AI**
