import json

# Load profiles from your profiling step
with open("corporate_profiles.json", "r", encoding="utf-8") as f:
    retail_profiles = json.load(f)

archetypes = []
for cid, prof in retail_profiles.items():
    archetype = {
        "id": f"Retail_Cluster{cid}",
        "type": "Retail",
        "weight": prof["size"],  # how many clients it represents
        "avg_age": prof.get("avg_age"),
        "avg_annual_salary": prof.get("avg_annual_salary"),
        "gender": prof.get("top_gender"),
        "civil_status": prof.get("top_civil_status"),
        "occupation": prof.get("top_occupation"),
        "region": prof.get("top_region")
    }
    archetypes.append(archetype)

with open("corporate_archetypes.json", "w", encoding="utf-8") as f:
    json.dump(archetypes, f, indent=4, ensure_ascii=False)
