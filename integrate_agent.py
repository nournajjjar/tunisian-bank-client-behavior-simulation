# integrate_agent.py
from run_scenario_agent import main as run_scenario
from behavioral import rag_answer, llm_media_shock

def run_scenario_agent():
    """
    Run the BankingAgent scenario analysis and return scenarios.
    """
    # This calls the main() function from run_scenario_agent.py
    results = run_scenario()  
    return results

def query_mesa_agent(user_query: str):
    """
    Query the behavioral/RAG agent directly (without full Mesa simulation).
    Returns answer and media shock.
    """
    answer = rag_answer(user_query)
    shock = llm_media_shock(user_query)
    return answer, shock
