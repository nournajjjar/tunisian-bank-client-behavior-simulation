import os
import json
import random
import pickle
import numpy as np
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
from groq import Groq
from sentence_transformers import SentenceTransformer
import networkx as nx
import matplotlib.pyplot as plt
from enum import Enum

# Import Azure Cosmos DB client
from cosmos_client import CosmosDBClient

# Define scenario types
class ScenarioType(Enum):
    NEW_PRODUCT_LAUNCH = "new_product_launch"
    DIGITAL_DISRUPTION = "digital_disruption"
    ECONOMIC_SHOCK = "economic_shock"
    REGULATORY_CHANGE = "regulatory_change"
    COMPETITOR_ACTION = "competitor_action"
    MERGER_ACQUISITION = "merger_acquisition"
    CAMPAIGN_ANALYSIS = "campaign_analysis"
    MARKET_TREND = "market_trend"

class NLPAnalyzer:
    """Simplified NLP analysis toolkit for banking content"""
    
    def __init__(self):
        # Initialize simple NLP tools
        try:
            import nltk
            from nltk.sentiment import SentimentIntensityAnalyzer
            from nltk.corpus import stopwords
            
            # Download all required NLTK data
            self._download_nltk_resources()
            
            self.sia = SentimentIntensityAnalyzer()
            
            try:
                self.stop_words = set(stopwords.words('english'))
            except:
                self.stop_words = set()
                print("⚠️  Stopwords not available")
            
        except Exception as e:
            print(f"⚠️  NLTK initialization failed: {e}")
            self.sia = None
            self.stop_words = set()
    
    def _download_nltk_resources(self):
        """Download all required NLTK resources"""
        try:
            import nltk
            
            resources = [
                'punkt',           # Basic tokenizer
                'vader_lexicon',   # Sentiment analysis
                'stopwords'        # Stopwords list
            ]
            
            for resource in resources:
                try:
                    nltk.data.find(resource)
                    print(f"✅ NLTK resource {resource} already available")
                except LookupError:
                    try:
                        print(f"📥 Downloading NLTK resource: {resource}")
                        nltk.download(resource, quiet=True)
                        print(f"✅ Successfully downloaded {resource}")
                    except Exception as e:
                        print(f"⚠️  Failed to download {resource}: {e}")
        except Exception as e:
            print(f"⚠️  NLTK download failed: {e}")
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Simple sentiment analysis using VADER"""
        if not text or len(text.strip()) < 10:
            return {"score": 0, "label": "neutral", "confidence": 0}
        
        try:
            if self.sia:
                scores = self.sia.polarity_scores(text)
                compound = scores['compound']
                
                if compound >= 0.05:
                    sentiment = "positive"
                elif compound <= -0.05:
                    sentiment = "negative"
                else:
                    sentiment = "neutral"
                
                return {
                    'sentiment': sentiment,
                    'confidence': abs(compound),
                    'scores': scores
                }
        except Exception as e:
            print(f"Sentiment analysis failed: {e}")
        
        return {"sentiment": "neutral", "confidence": 0, "scores": {}}
    
    def extract_key_phrases(self, text: str, num_phrases: int = 10) -> List[str]:
        """Extract key phrases from text using simple frequency analysis"""
        if not text:
            return []
        
        try:
            # Simple word-based approach without NLTK tokenization
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            words = [word for word in words if word not in self.stop_words]
            
            from collections import Counter
            word_counts = Counter(words)
            return [word for word, count in word_counts.most_common(num_phrases)]
            
        except Exception as e:
            print(f"Key phrase extraction failed: {e}")
            return []
    
    def summarize_text(self, text: str, num_sentences: int = 3) -> str:
        """Simple text summarization using sentence extraction"""
        if not text or len(text) < 50:
            return text
        
        try:
            # Simple approach: split by punctuation
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if len(sentences) <= num_sentences:
                return text
            
            # Return first few sentences
            return ". ".join(sentences[:num_sentences]) + "."
            
        except Exception as e:
            print(f"Text summarization failed: {e}")
            return text[:200] + "..." if len(text) > 200 else text
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Simple entity extraction using pattern matching"""
        if not text:
            return {}
        
        entities = {
            'ORGANIZATIONS': [],
            'LOCATIONS': [],
            'DATES': [],
            'NUMBERS': []
        }
        
        # Simple pattern matching for entities
        try:
            # Organizations (words in all caps or title case)
            org_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
            entities['ORGANIZATIONS'] = re.findall(org_pattern, text)
            
            # Locations (words that might be locations)
            location_keywords = ['bank', 'tunis', 'tunisia', 'street', 'avenue', 'boulevard']
            words = text.split()
            entities['LOCATIONS'] = [word for word in words if any(keyword in word.lower() for keyword in location_keywords)]
            
            # Dates (simple date patterns)
            date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'
            entities['DATES'] = re.findall(date_pattern, text, re.IGNORECASE)
            
            # Numbers (monetary values and percentages)
            number_pattern = r'\b\d+(?:\.\d+)?%?\b|\$\d+(?:\.\d+)?\b|\d+(?:\.\d+)?\s*(?:million|billion|thousand)\b'
            entities['NUMBERS'] = re.findall(number_pattern, text, re.IGNORECASE)
            
        except Exception as e:
            print(f"Entity extraction failed: {e}")
        
        return entities

class BankingAgent:
    def __init__(self):
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize NLP analyzer
        self.nlp_analyzer = NLPAnalyzer()
        self.memory_store = {}
        self.scenario_history = []
        self.cosmos_client = CosmosDBClient()
        self.all_banks_data = {}
        self.biat_enhanced_data = {}
        
        # Load all external data
        self._load_external_data()
    
    def _load_external_data(self):
        """Load all external data including economic indicators and enhanced BIAT data"""
        try:
            with open("index.pkl", "rb") as f:
                index_data = pickle.load(f)
                self.economic_indicators = index_data.get("economic_indicators", {})
                self.biat_enhanced_data = index_data.get("biat_data", {})
            print("✅ Economic indicators and enhanced BIAT data loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load external data: {e}")
            # Default economic indicators for Tunisia
            self.economic_indicators = {
                "inflation_rate": 7.2, "interest_rate": 6.5, "gdp_growth": 2.1,
                "unemployment_rate": 15.8, "exchange_rate": 3.11,
                "foreign_reserves": 2.5, "budget_deficit": 6.8, "public_debt": 79.5
            }
            self.biat_enhanced_data = {}
        
        try:
            import faiss
            self.faiss_index = faiss.read_index("index.faiss")
            print("✅ FAISS index loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load FAISS index: {e}")
            self.faiss_index = None
    
    def load_all_banks_data(self, days_back=30):
        """Load all banks data from Azure Cosmos DB"""
        try:
            query = f"SELECT * FROM c WHERE c.timestamp >= '{self._get_past_date(days_back)}'"
            results = self.cosmos_client.query_results(query)
            
            for item in results:
                bank_name = item.get('bank', 'Unknown')
                if bank_name not in self.all_banks_data:
                    self.all_banks_data[bank_name] = []
                
                # Enhance data with simple NLP analysis
                enhanced_item = self._enhance_with_nlp(item)
                self.all_banks_data[bank_name].append(enhanced_item)
            
            print(f"✅ Loaded data for {len(self.all_banks_data)} banks from Cosmos DB")
            return self.all_banks_data
            
        except Exception as e:
            print(f"❌ Failed to load banks data from Cosmos DB: {e}")
            return {}
    
    def _get_past_date(self, days_back):
        return (datetime.now() - timedelta(days=days_back)).isoformat()
    
    def _enhance_with_nlp(self, bank_data: Dict) -> Dict:
        """Enhance bank data with simple NLP analysis"""
        enhanced_data = bank_data.copy()
        
        # Analyze news sentiment
        news_items = bank_data.get('news', [])
        if news_items:
            enhanced_data['news_analysis'] = self._analyze_news_items(news_items)
        
        # Extract all text for overall analysis
        all_text = self._extract_all_text(bank_data)
        if all_text:
            enhanced_data['overall_sentiment'] = self.nlp_analyzer.analyze_sentiment(all_text)
            enhanced_data['key_phrases'] = self.nlp_analyzer.extract_key_phrases(all_text)
        
        return enhanced_data
    
    def _analyze_news_items(self, news_items: List[Dict]) -> Dict:
        """Perform simple NLP analysis on news items"""
        analysis = {
            'total_news': len(news_items),
            'sentiment_scores': [],
            'important_entities': {'ORGANIZATIONS': [], 'LOCATIONS': []}
        }
        
        all_news_text = []
        for news in news_items:
            news_text = f"{news.get('title', '')} {news.get('summary', '')}"
            if news_text.strip():
                all_news_text.append(news_text)
                
                # Individual news sentiment
                sentiment = self.nlp_analyzer.analyze_sentiment(news_text)
                analysis['sentiment_scores'].append(sentiment.get('sentiment', 'neutral'))
                
                # Entity extraction
                entities = self.nlp_analyzer.extract_entities(news_text)
                for entity_type in analysis['important_entities']:
                    analysis['important_entities'][entity_type].extend(entities.get(entity_type, []))
        
        # Remove duplicates
        for entity_type in analysis['important_entities']:
            analysis['important_entities'][entity_type] = list(set(analysis['important_entities'][entity_type]))
        
        # Overall news sentiment
        if all_news_text:
            combined_news_text = " ".join(all_news_text)
            analysis['overall_sentiment'] = self.nlp_analyzer.analyze_sentiment(combined_news_text)
        
        return analysis
    
    def _extract_all_text(self, bank_data: Dict) -> str:
        """Extract all text content from bank data"""
        texts = []
        
        # Extract from news
        for news in bank_data.get('news', []):
            if news.get('title'): texts.append(news.get('title'))
            if news.get('summary'): texts.append(news.get('summary'))
        
        # Extract from campaigns
        for campaign in bank_data.get('campaigns', []):
            if campaign.get('title'): texts.append(campaign.get('title'))
            if campaign.get('description'): texts.append(campaign.get('description'))
        
        # Extract from updates
        for update in bank_data.get('updates', []):
            if update.get('type'): texts.append(update.get('type'))
            if update.get('details'): texts.append(update.get('details'))
        
        return " ".join(filter(None, texts))
    
    def get_bank_summary(self, bank_name):
        """Get summary information for a specific bank"""
        if bank_name not in self.all_banks_data:
            return None
        
        bank_entries = self.all_banks_data[bank_name]
        latest_entry = max(bank_entries, key=lambda x: x.get('timestamp', ''))
        
        return {
            "bank": bank_name,
            "latest_update": latest_entry.get('timestamp'),
            "news_count": len(latest_entry.get('news', [])),
            "campaigns_count": len(latest_entry.get('campaigns', [])),
            "updates_count": len(latest_entry.get('updates', [])),
            "status": latest_entry.get('status', 'unknown')
        }
    
    def analyze_current_state(self):
        """Analyze current banking and economic conditions for all banks"""
        print("Analyzing current state for all Tunisian banks...")
        
        # Load all banks data
        self.load_all_banks_data(7)
        
        # Get economic context
        economic_context = self._get_economic_context()
        
        # Get bank summaries
        bank_summaries = []
        for bank_name in self.all_banks_data.keys():
            summary = self.get_bank_summary(bank_name)
            if summary:
                bank_summaries.append(summary)
        
        # Use Llama3 to analyze the current state
        prompt = f"""
        As a banking analyst, analyze the current economic and banking environment in Tunisia for all major banks.
        
        Economic Context: {economic_context}
        
        Bank Activities Summary: {json.dumps(bank_summaries, ensure_ascii=False)}
        
        Provide a comprehensive analysis including:
        1. Overall economic health and impact on Tunisian banking sector
        2. Comparative analysis of major banks' activities
        3. Key risks and opportunities across the banking sector
        4. Market trends and competitive landscape
        5. Specific insights for BIAT based on enhanced data availability
        
        Respond with a JSON object containing: overall_analysis, comparative_analysis, key_risks, key_opportunities, market_trends, biat_specific_insights
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            analysis = json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Analysis failed: {e}")
            analysis = {
                "overall_analysis": "Current economic conditions show moderate growth with elevated inflation across Tunisian banking sector.",
                "comparative_analysis": "Banks show varied activity levels with BIAT maintaining leadership position.",
                "key_risks": ["High inflation", "Economic volatility", "Regulatory changes", "Digital disruption"],
                "key_opportunities": ["Digital transformation", "Financial inclusion", "Regional expansion", "Product innovation"],
                "market_trends": ["Accelerated digital adoption", "Increased competition", "Regulatory evolution"],
                "biat_specific_insights": "BIAT shows strong market position with opportunities for digital leadership."
            }
        
        return analysis
    
    def generate_scenarios(self, analysis):
        """Generate what-if scenarios for the entire banking sector"""
        print("Generating scenarios for Tunisian banking sector...")
        
        # Get scenario types to generate
        scenario_types = self._determine_scenario_types(analysis)
        
        scenarios = []
        for scenario_type in scenario_types:
            scenario = self._create_scenario(scenario_type, analysis)
            scenarios.append(scenario)
        
        return scenarios
    
    def _determine_scenario_types(self, analysis):
        """Determine which scenario types to generate based on current state"""
        scenarios = [
            ScenarioType.MARKET_TREND,
            ScenarioType.ECONOMIC_SHOCK,
            ScenarioType.NEW_PRODUCT_LAUNCH,
            ScenarioType.REGULATORY_CHANGE,
            ScenarioType.COMPETITOR_ACTION,
            ScenarioType.CAMPAIGN_ANALYSIS
        ]
        
        return scenarios[:4]  # Limit to 4 scenarios
    
    def _create_scenario(self, scenario_type: ScenarioType, analysis):
        """Create a specific scenario based on type for the banking sector"""
        scenario_templates = {
            ScenarioType.MARKET_TREND: {
                "title": "Banking Sector Market Trends",
                "description": "Emerging trends affecting the entire Tunisian banking sector",
                "scope": "sector_wide"
            },
            ScenarioType.NEW_PRODUCT_LAUNCH: {
                "title": "Industry-wide Digital Banking Innovation",
                "description": "Wave of new digital banking products across multiple banks",
                "scope": "multiple_banks"
            },
            ScenarioType.ECONOMIC_SHOCK: {
                "title": "Economic Shock Impacting Banking Sector",
                "description": "Significant economic event affecting all Tunisian banks",
                "scope": "sector_wide"
            },
            ScenarioType.REGULATORY_CHANGE: {
                "title": "Regulatory Changes for Banking Sector",
                "description": "New regulations impacting the entire banking industry",
                "scope": "sector_wide"
            },
            ScenarioType.COMPETITOR_ACTION: {
                "title": "Competitive Dynamics in Banking",
                "description": "Strategic moves and counter-moves among major banks",
                "scope": "multiple_banks"
            },
            ScenarioType.CAMPAIGN_ANALYSIS: {
                "title": "Marketing Campaign Effectiveness Analysis",
                "description": "Analysis of marketing campaigns across major banks",
                "scope": "multiple_banks"
            }
        }
        
        template = scenario_templates[scenario_type]
        
        # Generate specific scenario details using Llama3
        prompt = f"""
        Create a detailed "what-if" scenario for the Tunisian banking sector based on this template:
        Title: {template['title']}
        Description: {template['description']}
        Scope: {template['scope']}
        
        Current economic context: {self._get_economic_context()}
        Sector analysis: {analysis['overall_analysis']}
        
        Generate a realistic scenario with specific details including:
        - Triggering event or trend
        - Timeline of development
        - Affected banks and entities
        - Potential impacts across the sector
        - Differential impact on major banks
        - Key metrics to monitor
        
        Respond with a JSON object containing: title, description, scope, trigger, timeline, affected_entities, 
        sector_impacts, differential_impacts, metrics
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            scenario = json.loads(response.choices[0].message.content)
            scenario["type"] = scenario_type.value
            scenario["id"] = f"scenario_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
            
        except Exception as e:
            print(f"Scenario generation failed: {e}")
            # Fallback scenario
            scenario = {
                "id": f"scenario_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
                "type": scenario_type.value,
                "title": template["title"],
                "description": template["description"],
                "scope": template["scope"],
                "trigger": "Market evolution and competitive dynamics",
                "timeline": "Next 3-12 months",
                "affected_entities": ["All major Tunisian banks", "Regulators", "Customers"],
                "sector_impacts": ["Changed competitive landscape", "Customer behavior shifts", "Regulatory response"],
                "differential_impacts": {"BIAT": "Market leadership challenges", "Other banks": "Opportunities for gain"},
                "metrics": ["Overall market share", "Digital adoption rates", "Customer satisfaction scores"]
            }
        
        # Store in memory
        self._memorize(f"scenario_{scenario['id']}", scenario)
        
        return scenario
    
    def evaluate_scenarios(self, scenarios):
        """Evaluate generated scenarios for the banking sector"""
        print("Evaluating scenarios for banking sector...")
        
        scenario_results = []
        for scenario in scenarios:
            result = self._evaluate_single_scenario(scenario)
            scenario_results.append(result)
        
        return scenario_results
    
    def _evaluate_single_scenario(self, scenario: Dict):
        """Evaluate a single scenario using Llama3 for banking sector"""
        prompt = f"""
        As a banking sector analyst, evaluate this scenario for the Tunisian banking industry:
        
        Scenario: {scenario['title']}
        Description: {scenario['description']}
        Scope: {scenario.get('scope', 'sector_wide')}
        
        Current economic context: {self._get_economic_context()}
        
        Please evaluate:
        1. Probability of occurrence (0-100%)
        2. Potential impact on banking sector (1-10 scale)
        3. Key risk factors across banks
        4. Potential opportunities for different banks
        5. Differential impact on major banks (BIAT, BT, ATB, etc.)
        6. Recommended monitoring indicators
        
        Respond with a JSON object containing: probability, impact_score, risk_factors, opportunities, 
        differential_impacts, indicators, recommended_actions
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            evaluation = json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Scenario evaluation failed: {e}")
            evaluation = {
                "probability": random.randint(20, 70),
                "impact_score": random.randint(4, 9),
                "risk_factors": ["Market share erosion", "Revenue pressure", "Regulatory compliance costs"],
                "opportunities": ["Digital transformation", "Market expansion", "Customer experience improvement"],
                "differential_impacts": {
                    "BIAT": "Challenges to market leadership but strong capacity to adapt",
                    "Other banks": "Opportunities to gain market share through innovation"
                },
                "indicators": ["Sector-wide performance metrics", "Individual bank market shares", "Digital adoption rates"],
                "recommended_actions": ["Enhanced monitoring", "Strategic planning", "Risk mitigation measures"]
            }
        
        # Combine scenario with evaluation
        result = {**scenario, **evaluation}
        
        # Store in memory
        self._memorize(f"evaluation_{scenario['id']}", result)
        
        return result
    
    def formulate_recommendations(self, scenario_results):
        """Formulate recommendations for the entire banking sector"""
        print("Formulating sector-wide recommendations...")
        
        # Use Llama3 to generate comprehensive recommendations
        scenario_summary = "\n".join([
            f"Scenario: {s['title']}, Probability: {s.get('probability', 'N/A')}%, Impact: {s.get('impact_score', 'N/A')}/10"
            for s in scenario_results
        ])
        
        # Get bank summaries for context
        bank_summaries = []
        for bank_name in self.all_banks_data.keys():
            summary = self.get_bank_summary(bank_name)
            if summary:
                bank_summaries.append(summary)
        
        prompt = f"""
        As a banking sector strategist, formulate strategic recommendations for the Tunisian banking industry:
        
        Scenario Evaluations: {scenario_summary}
        
        Current Bank Activities: {json.dumps(bank_summaries, ensure_ascii=False)}
        Economic Context: {self._get_economic_context()}
        
        Provide actionable recommendations including:
        1. Sector-wide immediate actions (next 30 days)
        2. Medium-term strategies for the banking industry (3-6 months)
        3. Long-term considerations for sector development (6+ months)
        4. Risk mitigation strategies for different bank categories
        5. Opportunity capture approaches for various bank sizes
        6. Specific recommendations for major banks (BIAT, BT, ATB, etc.)
        7. Enhanced recommendations for BIAT based on additional data availability
        
        Respond with a JSON object containing: sector_actions, medium_term_strategies, long_term_considerations, 
        risk_mitigation, opportunity_capture, bank_specific_recommendations, biat_enhanced_recommendations
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            recommendations = json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Recommendation generation failed: {e}")
            recommendations = {
                "sector_actions": [
                    "Enhance sector-wide risk monitoring",
                    "Strengthen cybersecurity collaboration",
                    "Improve regulatory compliance coordination"
                ],
                "medium_term_strategies": [
                    "Develop digital transformation frameworks",
                    "Enhance customer experience standards",
                    "Improve financial inclusion initiatives"
                ],
                "long_term_considerations": [
                    "Sector-wide innovation ecosystem development",
                    "Regional expansion strategies",
                    "Sustainable banking practices adoption"
                ],
                "risk_mitigation": {
                    "large_banks": "Diversify revenue streams and enhance digital capabilities",
                    "medium_banks": "Focus on niche markets and operational efficiency",
                    "small_banks": "Explore partnerships and specialized services"
                },
                "opportunity_capture": {
                    "all_banks": "Leverage digital banking trends and customer insights",
                    "innovative_banks": "Pioneer new products and services",
                    "traditional_banks": "Modernize operations and customer experiences"
                },
                "bank_specific_recommendations": {
                    "BIAT": "Leverage market leadership for digital innovation",
                    "BT": "Enhance customer service differentiation",
                    "ATB": "Strengthen digital banking offerings",
                    "BNA": "Focus on agricultural and rural banking"
                },
                "biat_enhanced_recommendations": [
                    "Utilize enhanced data capabilities for personalized services",
                    "Leverage market position for strategic partnerships",
                    "Accelerate digital transformation based on detailed insights"
                ]
            }
        
        # Store in memory
        self._memorize("recommendations", recommendations)
        
        return recommendations
    
    def _get_economic_context(self):
        """Get current economic context from indicators"""
        context = "Economic Context: "
        
        if self.economic_indicators:
            indicators = self.economic_indicators
            context += f"Inflation: {indicators.get('inflation_rate', 'N/A')}%. "
            context += f"Interest Rate: {indicators.get('interest_rate', 'N/A')}%. "
            context += f"GDP Growth: {indicators.get('gdp_growth', 'N/A')}%. "
            context += f"Unemployment: {indicators.get('unemployment_rate', 'N/A')}%. "
            context += f"Exchange Rate: {indicators.get('exchange_rate', 'N/A')} TND/USD. "
        
        return context
    
    def _memorize(self, key: str, value: Any):
        """Store information in memory"""
        self.memory_store[key] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
    
    def recall(self, key: str):
        """Recall information from memory"""
        return self.memory_store.get(key, {}).get("value")
    
    def get_memory_summary(self):
        """Get summary of memory contents"""
        return {
            "total_entries": len(self.memory_store),
            "scenario_count": sum(1 for k in self.memory_store if k.startswith("scenario_")),
            "evaluation_count": sum(1 for k in self.memory_store if k.startswith("evaluation_")),
            "banks_analyzed": len(self.all_banks_data),
            "latest_timestamp": max((v["timestamp"] for v in self.memory_store.values()), default="Never")
        }
    
    def ask_question(self, question):
        """Answer questions based on the analyzed data and scenarios"""
        print(f"\n🤔 Question: {question}")
        
        # Prepare context
        context = {
            "economic_context": self._get_economic_context(),
            "banks_analyzed": list(self.all_banks_data.keys()),
            "scenarios_generated": len([k for k in self.memory_store if k.startswith("scenario_")]),
            "biat_enhanced_data": bool(self.biat_enhanced_data)
        }
        
        prompt = f"""
        As a knowledgeable banking analyst for Tunisia, answer this question based on the available data:
        
        Question: {question}
        
        Available Context:
        - Economic situation: {context['economic_context']}
        - Banks analyzed: {', '.join(context['banks_analyzed'])}
        - Scenarios generated: {context['scenarios_generated']}
        - Enhanced BIAT data available: {context['biat_enhanced_data']}
        
        Provide a comprehensive, accurate answer based on the banking sector analysis.
        If the question requires specific data that might not be available, acknowledge that and provide
        the best possible answer based on general banking knowledge and the Tunisian context.
        
        Structure your response with clear insights and practical information.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            print(f"💡 Answer: {answer}")
            return answer
            
        except Exception as e:
            error_msg = f"Sorry, I couldn't process your question due to an error: {str(e)}"
            print(f"💡 {error_msg}")
            return error_msg
    
    def interactive_mode(self):
        """Start interactive question-answering mode"""
        print("\n" + "="*60)
        print("🤖 BANKING AGENT INTERACTIVE MODE")
        print("="*60)
        print("I have analyzed data from Azure Cosmos DB and enhanced BIAT information.")
        print("You can ask me questions about Tunisian banks, scenarios, or recommendations.")
        print("Type 'quit' to exit, 'summary' for analysis summary, or 'help' for options.")
        print("="*60)
        
        while True:
            try:
                question = input("\n🎯 Your question: ").strip()
                
                if question.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye! 👋")
                    break
                elif question.lower() in ['summary', 'overview']:
                    self._show_analysis_summary()
                elif question.lower() in ['help', '?']:
                    self._show_help()
                elif question:
                    self.ask_question(question)
                else:
                    print("Please enter a question or command.")
                    
            except KeyboardInterrupt:
                print("\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def _show_analysis_summary(self):
        """Show summary of the current analysis"""
        summary = self.get_memory_summary()
        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"   Banks analyzed: {summary['banks_analyzed']}")
        print(f"   Scenarios generated: {summary['scenario_count']}")
        print(f"   Memory entries: {summary['total_entries']}")
        print(f"   Last updated: {summary['latest_timestamp']}")
        
        # Show list of banks
        print(f"\n   Banks in analysis:")
        for i, bank in enumerate(self.all_banks_data.keys(), 1):
            print(f"   {i}. {bank}")
    
    def _show_help(self):
        """Show help information"""
        print("\n💡 HELP - Available questions and commands:")
        print("   'summary' - Show analysis overview")
        print("   'quit' - Exit interactive mode")
        print("   'help' - Show this help message")
        print("\n   Example questions:")
        print("   - What is the current state of BIAT?")
        print("   - How are other banks performing compared to BIAT?")
        print("   - What are the main risks for Tunisian banks?")
        print("   - What recommendations do you have for ATB?")
        print("   - Tell me about the economic shock scenario")
    
    def run_analysis(self):
        """Run complete analysis workflow for all banks"""
        print("Starting comprehensive banking sector analysis...")
        print(f"Economic context: {self._get_economic_context()}")
        
        # Step 1: Analyze current state for all banks
        analysis = self.analyze_current_state()
        
        # Step 2: Generate scenarios
        scenarios = self.generate_scenarios(analysis)
        
        # Step 3: Evaluate scenarios
        evaluated_scenarios = self.evaluate_scenarios(scenarios)
        
        # Step 4: Formulate recommendations
        recommendations = self.formulate_recommendations(evaluated_scenarios)
        
        # Print summary
        print("\n=== ANALYSIS COMPLETE ===")
        summary = self.get_memory_summary()
        print(f"Banks analyzed: {summary['banks_analyzed']}")
        print(f"Scenarios generated: {len(scenarios)}")
        print(f"Memory entries: {summary['total_entries']}")
        
        return {
            "analysis": analysis,
            "scenarios": evaluated_scenarios,
            "recommendations": recommendations
        }