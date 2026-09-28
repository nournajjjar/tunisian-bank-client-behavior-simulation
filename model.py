# model.py
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import random

# Sector definitions
RETAIL_SECTORS = ["Retail", "Personal Services", "Hospitality", "Education"]
CORPORATE_SECTORS = ["Manufacturing", "Technology", "Finance", "Healthcare", "Construction", "Logistics"]
SECTORS = RETAIL_SECTORS + CORPORATE_SECTORS + ["Unknown"]

# Scenario effects
SCENARIO_EFFECTS = {
    "baseline": {"adopt_bonus": 0.00, "churn_bonus": 0.00},
    "currency_devaluation": {"adopt_bonus": -0.02, "churn_bonus": 0.03},
    "digital_transformation": {"adopt_bonus": 0.04, "churn_bonus": -0.01},
    "export_boom": {"adopt_bonus": 0.02, "churn_bonus": -0.01},
    "regional_instability": {"adopt_bonus": -0.03, "churn_bonus": 0.04},
    "economic_growth": {"adopt_bonus": 0.03, "churn_bonus": -0.02},
    "recession": {"adopt_bonus": -0.04, "churn_bonus": 0.05},
}

class ClientAgent(Agent):
    def __init__(self, unique_id, model, is_retail=True):
        super().__init__(unique_id, model)
        self.satisfaction = random.random()
        self.products = random.randint(0, 3)
        self.channel = random.choice(["branch", "digital", "hybrid", "direct_sales"])
        self.is_retail = is_retail
        self.sector = random.choice(RETAIL_SECTORS) if is_retail else random.choice(CORPORATE_SECTORS)
        self.adopted = False
        self.churned = False

    def step(self):
        if self.churned:
            return

        # Satisfaction drift
        self.satisfaction = min(1.0, max(0.0, self.satisfaction + random.gauss(0, 0.05)))

        # Chance to gain a product
        if random.random() < 0.08:
            self.products += 1

        # Adoption probability
        sc = SCENARIO_EFFECTS.get(self.model.market_scenario, SCENARIO_EFFECTS["baseline"])
        base = 0.04
        promo = 0.10 * self.model.discount_pct
        channel_fit = 0.05 if self.channel == self.model.campaign_channel else 0.0
        sector_match = (self.model.target_sector in (self.sector, "All", "All Retail", "All Corporate"))
        sector_fit = 0.04 if sector_match else -0.02
        sat_push = 0.04 * (self.satisfaction - 0.5)
        adopt_p = max(0.0, base + promo + channel_fit + sector_fit + sat_push + sc["adopt_bonus"])

        if not self.adopted and random.random() < adopt_p:
            self.adopted = True
            self.model.adopted_cum += 1

        # Churn probability
        churn_base = 0.015 + sc["churn_bonus"] - (0.01 if self.adopted else 0.0)
        churn_base = max(0.0, churn_base)
        if random.random() < churn_base:
            self.churned = True
            self.model.churned_cum += 1

class BankClientModel(Model):
    def __init__(self, N=50, width=20, height=20, campaign_channel="branch", 
                 target_sector="All", discount_pct=0.10, market_scenario="baseline", retail_ratio=0.7):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.campaign_channel = campaign_channel
        self.target_sector = target_sector
        self.discount_pct = discount_pct
        self.market_scenario = market_scenario
        self.retail_ratio = retail_ratio
        self.adopted_cum = 0
        self.churned_cum = 0

        # Create agents
        num_retail = int(N * retail_ratio)
        for i in range(N):
            is_retail = i < num_retail
            a = ClientAgent(i, self, is_retail)
            self.schedule.add(a)
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            self.grid.place_agent(a, (x, y))

        # Data collection
        self.datacollector = DataCollector(
            model_reporters={
                "n_active": lambda m: sum(1 for a in m.schedule.agents if not a.churned),
                "adopted_cum": "adopted_cum",
                "churned_cum": "churned_cum",
                "adoption_rate": lambda m: m.adopted_cum / max(1, m.num_agents),
                "avg_satisfaction": lambda m: sum(a.satisfaction for a in m.schedule.agents if not a.churned) / max(1, sum(1 for a in m.schedule.agents if not a.churned))
            },
            agent_reporters={
                "satisfaction": "satisfaction",
                "products": "products",
                "channel": "channel",
                "sector": "sector",
                "adopted": "adopted",
                "churned": "churned",
                "is_retail": "is_retail"
            }
        )

    def step(self):
        self.schedule.step()
        self.datacollector.collect(self)