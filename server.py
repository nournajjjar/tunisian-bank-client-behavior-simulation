# server.py
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from model import BankClientModel

def agent_portrayal(agent):
    # color by state: churned -> gray, adopted -> green, else red
    if agent.churned:
        color = "#9aa0a6"
    elif agent.adopted:
        color = "#34a853"
    else:
        color = "#ea4335"
    return {
        "Shape": "circle",
        "r": 0.7,
        "Filled": "true",
        "Color": color,
        "Layer": 0,
        "text": f"{agent.products}"  # show product count
    }

grid = CanvasGrid(agent_portrayal, 20, 20, 700, 700)

kpi_chart = ChartModule(
    [
        {"Label": "adopted_cum", "Color": "Green"},
        {"Label": "churned_cum", "Color": "Red"},
        {"Label": "n_active", "Color": "Black"},
        {"Label": "avg_satisfaction", "Color": "Blue"},
    ],
    data_collector_name="datacollector"
)

server = ModularServer(
    BankClientModel,
    [grid, kpi_chart],
    "Product Adoption – Agent Simulation",
    {
        "N": 200, "width": 20, "height": 20,
        "campaign_channel": "branch",
        "target_sector": "All",
        "discount_pct": 0.10,
        "market_scenario": "digital_transformation",
    },
)
server.port = 8521
server.launch()
