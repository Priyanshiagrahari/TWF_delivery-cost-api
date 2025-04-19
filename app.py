from fastapi import FastAPI, Request
from itertools import permutations
from typing import Dict
import os

app = FastAPI()

# Product availability at each center
center_stock = {
    "C1": ["A", "B", "C", "G", "H", "I"],
    "C2": ["B", "C", "D", "E"],
    "C3": ["C", "D", "E", "F", "G", "H", "I"]
}

# Travel costs
costs = {
    ("C1", "L1"): 10,
    ("C2", "L1"): 20,
    ("C3", "L1"): 25,
    ("C1", "C2"): 15,
    ("C2", "C1"): 15,
    ("C2", "C3"): 10,
    ("C3", "C2"): 10,
    ("C1", "C3"): 30,
    ("C3", "C1"): 30
}

def get_cost(path):
    cost = 0
    for i in range(len(path) - 1):
        cost += costs.get((path[i], path[i+1]), float('inf'))
    return cost

def calculate_min_cost(order: Dict[str, int]):
    centers = ["C1", "C2", "C3"]
    min_cost = float('inf')

    for start in centers:
        required = {item: qty for item, qty in order.items() if qty > 0}

        product_to_center = {}
        for item in required:
            product_to_center[item] = [c for c in centers if item in center_stock[c]]

        def generate_routes(center):
            pickups = set()
            for item in required:
                if center not in product_to_center[item]:
                    pickups.update(product_to_center[item])
            pickups = list(pickups)
            all_routes = permutations(pickups)
            best = float('inf')
            for route in all_routes:
                full_path = [center]
                full_path.extend(route)
                full_path.append("L1")
                best = min(best, get_cost(full_path))
            return best if pickups else costs[(center, "L1")]

        route_cost = generate_routes(start)
        if route_cost < min_cost:
            min_cost = route_cost

    return min_cost

@app.get("/")
def home():
    return {"message": "Welcome to Delivery Cost API. Use POST /calculate"}

@app.post("/calculate")
async def calculate(request: Request):
    try:
        data = await request.json()
        cost = calculate_min_cost(data)
        return {"minimum_cost": cost}
    except Exception as e:
        return {"error": str(e)}


# Deployment entry
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
