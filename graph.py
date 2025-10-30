from langgraph.graph import START, END, StateGraph
from langgraph.types import Send
from langchain_openai import ChatOpenAI

from pydantic import BaseModel
from schemas import *
from prompt import *
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()

# LLMs
llm = ChatOpenAI(model_name="gpt-4o-mini")
reasoning_llm = ChatOpenAI(model_name="o3-mini")

# Nós
def build_first_queries(state: ReportState) -> ReportState:
    class QueryList(BaseModel):
        queries: List[str]

    user_input = state.user_input
    prompt = build_queries.format(user_input=user_input)
    query_llm = llm.with_structured_output(QueryList)
    response = query_llm.invoke(prompt)

    state.queries = response.queries
    return state


def single_search(query: str):
    tavily_client = TavilyClient()

    results = tavily_client.search(query, max_results=1, include_raw_content=False)

    query_results = []
    for result in results["results"]:
        url = result["url"]
        url_extraction = tavily_client.extract(url)
        if len(url_extraction["results"]) > 0:
            raw_content = url_extraction["results"][0]["raw_content"]
            prompt = resume_search.format(user_input=user_input,
                                        search_results=raw_content)

            llm_result = llm.invoke(prompt)
            query_results += [QueryResult(title=result["title"],
                                    url=url,
                                    resume=llm_result.content)]
    return {"queries_results": query_results}


def spawn_researchers(state: ReportState):
    return [Send("single_search", query) for query in state.queries]

def final_writer(state: ReportState):
    search_results = ""
    references = ""
    for i, result in enumerate(state.queries_results):
        search_results += f"[{i+1}]\n\n"
        search_results += f"Title: {result.title}\n"
        search_results += f"URL: {result.url}\n"
        search_results += f"Content: {result.resume}\n"
        search_results += f"================\n\n"

        references += f"[{i+1}] - [{result.title}]({result.url})\n"
    

    prompt = build_final_response.format(user_input=user_input,
                                    search_results=search_results)

    llm_result = reasoning_llm.invoke(prompt)

    final_response = llm_result.content + "\n\n References:\n" + references

    return {"final_response": final_response}



# Criando o grafo de estados com nós e arestas
builder = StateGraph(ReportState)

builder.add_node("build_first_queries", build_first_queries)
builder.add_node("single_search", single_search)
builder.add_node("final_writer", final_writer)

builder.add_edge(START, "build_first_queries")
builder.add_conditional_edges("build_first_queries", 
                              spawn_researchers, 
                              ["single_search"])
builder.add_edge("single_search", "final_writer")
builder.add_edge("final_writer", END) 

graph = builder.compile()



if __name__ == "__main__":
    user_input = "What are the latest advancements in AI Agents?"

    graph.invoke(
        {"user_input": user_input}
    )

    # cria um arquivo pdf com a reposta final
    with open("final_report.pdf", "wb") as f:
        f.write(graph.state.final_response.encode("utf-8"))