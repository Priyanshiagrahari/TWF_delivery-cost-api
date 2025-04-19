from flask import Flask, request, jsonify
from itertools import permutations

app = Flask(__name__)

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

def calculate_min_cost(order):
    centers = ["C1", "C2", "C3"]
    min_cost = float('inf')

    for start in centers:
        required = {}
        for item, qty in order.items():
            if qty > 0:
                required[item] = qty

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
                for loc in route:
                    full_path.extend([loc, "L1"])
                full_path.append("L1")
                best = min(best, get_cost(full_path))
            return best if pickups else costs[(center, "L1")]

        route_cost = generate_routes(start)
        if route_cost < min_cost:
            min_cost = route_cost

    return min_cost

@app.route('/')
def home():
    return "Welcome to Delivery Cost API. Use POST /calculate"

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400
    try:
        cost = calculate_min_cost(data)
        return jsonify({"minimum_cost": cost})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
