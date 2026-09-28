import os
import json
from datetime import datetime
from dotenv import load_dotenv
from banking_agent import BankingAgent

load_dotenv()

def main():
    try:
        # Initialize the agent
        print("🔄 Initializing Banking Agent...")
        agent = BankingAgent()
        
        # Run the complete analysis
        print("🚀 Running comprehensive banking sector analysis...")
        results = agent.run_analysis()
        
        # Print summary of results
        print("\n=== ANALYSIS RESULTS ===")
        print(f"📋 Scenarios generated: {len(results['scenarios'])}")
        
        # Show banks analyzed
        banks_count = len(agent.all_banks_data)
        print(f"🏦 Banks analyzed: {banks_count}")
        
        # Print scenario results
        print("\n=== SCENARIO RESULTS ===")
        for i, scenario in enumerate(results["scenarios"], 1):
            print(f"\n{i}. {scenario['title']}")
            print(f"   Type: {scenario.get('type', 'N/A')}")
            print(f"   Probability: {scenario.get('probability', 'N/A')}%")
            print(f"   Impact Score: {scenario.get('impact_score', 'N/A')}/10")
        
        # Print memory summary
        memory_summary = agent.get_memory_summary()
        print(f"\n=== MEMORY SUMMARY ===")
        print(f"Total entries: {memory_summary['total_entries']}")
        print(f"Scenarios: {memory_summary['scenario_count']}")
        print(f"Evaluations: {memory_summary['evaluation_count']}")
        
        # Save full results to JSON
        with open("scenario_analysis_results.json", "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "economic_context": agent._get_economic_context(),
                "banks_analyzed": list(agent.all_banks_data.keys()),
                "scenarios": results["scenarios"],
                "recommendations": results["recommendations"],
                "memory_summary": memory_summary
            }, f, indent=2, ensure_ascii=False)
        
        print("\n✅ Full results saved to scenario_analysis_results.json")
        
        # Start interactive mode
        agent.interactive_mode()
        
    except Exception as e:
        print(f"❌ Error running analysis: {e}")
        print("Please check your environment variables and dependencies:")
        print("1. Ensure GROQ_API_KEY is set in .env file")
        print("2. Ensure COSMOS_ENDPOINT and COSMOS_PRIMARY_KEY are set")
        print("3. Install required packages: pip install groq sentence-transformers nltk faiss-cpu networkx matplotlib python-dotenv")

if __name__ == "__main__":
    main()