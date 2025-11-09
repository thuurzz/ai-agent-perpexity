from langgraph.graph import START, END, StateGraph
from langgraph.types import Send
from langchain_openai import ChatOpenAI

from pydantic import BaseModel
from schemas import *
from prompt import *
from dotenv import load_dotenv
from tavily import TavilyClient
import logging

from datetime import datetime
from pdf_generator import generate_report_files

# Configurar logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()
logger.info("🚀 Aplicação iniciada e variáveis de ambiente carregadas")

# LLMs
logger.info("🤖 Inicializando LLMs...")
llm = ChatOpenAI(model_name="gpt-4o-mini")
reasoning_llm = ChatOpenAI(model_name="o3-mini")
logger.info("✅ LLMs inicializados com sucesso")

# Nós


def build_first_queries(state: ReportState) -> ReportState:
    logger.info("🔍 Iniciando build_first_queries...")
    logger.info(f"📝 Estado recebido: {state}")

    class QueryList(BaseModel):
        queries: List[str]

    user_input = state.user_input
    logger.info(f"👤 Input do usuário: {user_input}")

    prompt = build_queries.format(user_input=user_input)
    logger.info(f"📋 Prompt gerado: {prompt[:100]}...")

    query_llm = llm.with_structured_output(QueryList)
    logger.info("🔄 Enviando prompt para LLM...")

    response = query_llm.invoke(prompt)
    logger.info(f"📊 Resposta do LLM: {response}")

    state.queries = response.queries
    logger.info(f"✅ Queries geradas: {state.queries}")
    logger.info(f"📤 Estado final: {state}")

    return state


def single_search(query: str):
    logger.info(f"🔎 Iniciando busca para query: {query}")

    tavily_client = TavilyClient()
    logger.info("🌐 Cliente Tavily inicializado")

    results = tavily_client.search(
        query, max_results=1, include_raw_content=False)
    logger.info(
        f"📋 Resultados da busca: {len(results.get('results', []))} resultado(s)")

    query_results = []
    for i, result in enumerate(results["results"]):
        logger.info(f"📄 Processando resultado {i+1}: {result['title']}")
        url = result["url"]
        logger.info(f"🔗 URL: {url}")

        url_extraction = tavily_client.extract(url)
        if len(url_extraction["results"]) > 0:
            raw_content = url_extraction["results"][0]["raw_content"]
            logger.info(f"📝 Conteúdo extraído: {len(raw_content)} caracteres")

            prompt = resume_search.format(user_input=query,  # Corrigido: usar query em vez de user_input
                                          search_results=raw_content)
            logger.info("🤖 Enviando para LLM para resumo...")

            llm_result = llm.invoke(prompt)
            logger.info(
                f"✅ Resumo gerado: {len(llm_result.content)} caracteres")

            query_results += [QueryResult(title=result["title"],
                                          url=url,
                                          resume=llm_result.content)]
        else:
            logger.warning(f"⚠️ Não foi possível extrair conteúdo de {url}")

    logger.info(f"🎯 Total de resultados processados: {len(query_results)}")
    return {"queries_results": query_results}


def spawn_researchers(state: ReportState):
    logger.info(
        f"👥 Iniciando spawn_researchers com {len(state.queries)} queries")
    logger.info(f"📋 Queries: {state.queries}")

    sends = [Send("single_search", query) for query in state.queries]
    logger.info(f"🚀 Criando {len(sends)} tarefas de busca paralela")

    return sends


def final_writer(state: ReportState):
    logger.info("✍️ Iniciando final_writer...")
    logger.info(
        f"📊 Estado recebido: queries_results = {len(state.queries_results)} resultados")

    search_results = ""
    references = ""
    for i, result in enumerate(state.queries_results):
        logger.info(f"📄 Processando resultado {i+1}: {result.title}")
        search_results += f"[{i+1}]\n\n"
        search_results += f"Title: {result.title}\n"
        search_results += f"URL: {result.url}\n"
        search_results += f"Content: {result.resume}\n"
        search_results += f"================\n\n"

        references += f"[{i+1}] - [{result.title}]({result.url})\n"

    logger.info(f"📝 Conteúdo compilado: {len(search_results)} caracteres")
    logger.info(f"🔗 Referências: {len(references)} caracteres")

    prompt = build_final_response.format(user_input=state.user_input,  # Corrigido: usar state.user_input
                                         search_results=search_results)
    logger.info("🤖 Enviando para LLM de reasoning...")

    llm_result = reasoning_llm.invoke(prompt)
    logger.info(
        f"✅ Resposta final gerada: {len(llm_result.content)} caracteres")

    final_response = llm_result.content + "\n\n References:\n" + references
    logger.info(f"📋 Resposta final completa: {len(final_response)} caracteres")

    # Gerar PDF e Markdown usando o módulo dedicado
    try:
        logger.info("📄 Gerando relatório profissional (PDF + Markdown)...")
        
        # Usar o módulo de geração de PDF com o user_input para nome do arquivo
        report_files = generate_report_files(final_response, user_input=state.user_input)
        
        logger.info(f"✅ PDF profissional: {report_files['pdf_path']}")
        logger.info(f"📝 Arquivo Markdown: {report_files['markdown_path']}")
        
    except Exception as e:
        logger.error(f"❌ Erro ao gerar relatório: {str(e)}")
        logger.error(f"🔍 Tipo do erro: {type(e).__name__}")
        # Continuar execução mesmo se a geração falhar

    return {"final_response": final_response}


# Criando o grafo de estados com nós e arestas
logger.info("🏗️ Construindo o grafo de estados...")
builder = StateGraph(ReportState)

logger.info("➕ Adicionando nós...")
builder.add_node("build_first_queries", build_first_queries)
builder.add_node("single_search", single_search)
builder.add_node("final_writer", final_writer)

logger.info("🔗 Adicionando arestas...")
builder.add_edge(START, "build_first_queries")
builder.add_conditional_edges("build_first_queries",
                              spawn_researchers,
                              ["single_search"])
builder.add_edge("single_search", "final_writer")
builder.add_edge("final_writer", END)

logger.info("⚙️ Compilando o grafo...")
graph = builder.compile()
logger.info("✅ Grafo compilado com sucesso")


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("🎯 INICIANDO EXECUÇÃO PRINCIPAL")
    logger.info("=" * 60)

    user_input = input(
        "💬 Por favor, insira o tópico para pesquisa e relatório: ")
    logger.info(f"💬 Input do usuário: {user_input}")

    initial_state = {"user_input": user_input}
    logger.info(f"🏁 Estado inicial: {initial_state}")

    try:
        logger.info("🚀 Invocando o grafo...")
        result = graph.invoke(initial_state)
        logger.info(f"✅ Execução concluída com sucesso!")
        logger.info(f"📊 Tipo do resultado: {type(result)}")
        logger.info(
            f"📋 Chaves do resultado: {result.keys() if isinstance(result, dict) else 'Não é dict'}")

        # O PDF e Markdown já foram gerados na função final_writer
        logger.info("✅ Execução concluída! Arquivos gerados:")
        logger.info("📄 PDF profissional salvo em: reports/")
        logger.info("📝 Arquivo Markdown salvo em: reports/")
        logger.info("🎯 Processo completo finalizado com sucesso!")

    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"❌ ERRO DURANTE A EXECUÇÃO: {str(e)}")
        logger.error(f"🔍 Tipo do erro: {type(e).__name__}")
        logger.error("=" * 60)
        raise
