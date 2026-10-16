"""Flask Web Application for Online Food Order Processing System using Queue Data Structure (FIFO).

Engineering Mini Project:
- Project Title: Online Food Order Processing System using Queue Data Structure
- Students: Ingole Sushant Prakashrao & Bhalke Diksha Sangmeshwar
- College: Dr. D. Y. Patil College of Engineering and Innovation
- Department: Engineering Science and Humanities
- Academic Year: 2026-27
"""

import os
from flask import Flask, jsonify, render_template, request
from src.order_manager import FoodOrderSystem

app = Flask(__name__)

# Initialize the Food Order Processing System
system = FoodOrderSystem(kitchen_capacity=3)


@app.route("/")
def index():
    """Render the main single-page application dashboard."""
    menu = system.get_menu()
    dashboard = system.get_dashboard_state()
    return render_template(
        "index.html",
        menu=menu,
        dashboard=dashboard,
        categories=["All", "Burgers", "Pizzas", "Wraps & Bowls", "Sides", "Beverages", "Desserts"]
    )


@app.route("/api/menu", methods=["GET"])
def get_menu():
    """Retrieve food menu with optional category filtering."""
    category = request.args.get("category", "All")
    items = system.get_menu(category=category)
    return jsonify({"success": True, "category": category, "count": len(items), "items": items})


@app.route("/api/order/place", methods=["POST"])
def place_order():
    """Place a new food order and enqueue it into the waiting queue.

    Demonstrates the ENQUEUE operation of the Queue Data Structure.
    """
    try:
        data = request.get_json(force=True) or {}
        customer_name = data.get("customer_name", "").strip() or "Guest Customer"
        items = data.get("items", [])
        order_type = data.get("order_type", "Dine-In")
        table_or_token = data.get("table_or_token", "Table 1")
        notes = data.get("notes", "")

        if not items:
            return jsonify({"success": False, "error": "Order must contain at least one item."}), 400

        order = system.place_order(
            customer_name=customer_name,
            items=items,
            order_type=order_type,
            table_or_token=table_or_token,
            notes=notes
        )

        return jsonify({
            "success": True,
            "message": f"Order {order['order_id']} successfully placed and enqueued at position #{order['queue_position']}.",
            "order": order,
            "queue_state": system.waiting_queue.get_state()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/order/track/<order_id>", methods=["GET"])
def track_order(order_id):
    """Retrieve live status, history trail, and queue position for an order."""
    order = system.track_order(order_id)
    if not order:
        return jsonify({
            "success": False,
            "error": f"Order ID '{order_id}' was not found. Please verify the ID (e.g., ORD-105)."
        }), 404

    return jsonify({"success": True, "order": order})


@app.route("/api/queue/status", methods=["GET"])
def queue_status():
    """Retrieve the full system state including Waiting Queue, Kitchen, Counter, and Analytics."""
    state = system.get_dashboard_state()
    return jsonify({"success": True, "state": state})


@app.route("/api/kitchen/process-next", methods=["POST"])
def kitchen_process_next():
    """DEQUEUE the front order from the queue and send to the kitchen.

    Demonstrates the DEQUEUE operation (FIFO).
    """
    if system.waiting_queue.is_empty():
        return jsonify({
            "success": False,
            "error": "Queue Underflow: Waiting queue is empty! No incoming orders to dequeue."
        }), 400

    order = system.process_next_order()
    return jsonify({
        "success": True,
        "message": f"Order {order['order_id']} dequeued from FRONT and sent to kitchen chef station.",
        "order": order,
        "queue_state": system.waiting_queue.get_state()
    })


@app.route("/api/kitchen/mark-ready", methods=["POST"])
def kitchen_mark_ready():
    """Move an order from Kitchen Preparation to Ready for Pickup Counter."""
    data = request.get_json(force=True) or {}
    order_id = data.get("order_id", "").strip().upper()

    order = system.mark_order_ready(order_id)
    if not order:
        return jsonify({"success": False, "error": f"Active preparing order '{order_id}' not found."}), 404

    return jsonify({
        "success": True,
        "message": f"Order {order_id} marked READY! Displayed at pickup counter.",
        "order": order
    })


@app.route("/api/kitchen/complete", methods=["POST"])
def kitchen_complete():
    """Complete order handover to customer."""
    data = request.get_json(force=True) or {}
    order_id = data.get("order_id", "").strip().upper()

    order = system.complete_order(order_id)
    if not order:
        return jsonify({"success": False, "error": f"Ready order '{order_id}' not found."}), 404

    return jsonify({
        "success": True,
        "message": f"Order {order_id} marked COMPLETED and archived.",
        "order": order
    })


@app.route("/api/kitchen/step", methods=["POST"])
def kitchen_step():
    """Trigger one simulation tick."""
    result = system.step_simulation()
    return jsonify({"success": True, "actions": result["actions_taken"], "state": result["status"]})


@app.route("/api/queue/simulate-order", methods=["POST"])
def simulate_order():
    """Generate and enqueue a realistic random order for demonstration."""
    order = system.simulate_random_order()
    return jsonify({
        "success": True,
        "message": f"Simulated order {order['order_id']} placed by {order['customer_name']} (enqueued at rear).",
        "order": order,
        "queue_state": system.waiting_queue.get_state()
    })


@app.route("/api/queue/reset", methods=["POST"])
def queue_reset():
    """Reset the order processing system and reload sample state."""
    system.reset_system()
    return jsonify({
        "success": True,
        "message": "Order processing system reset to default demonstrative state.",
        "state": system.get_dashboard_state()
    })


@app.route("/api/dsa-info", methods=["GET"])
def dsa_info():
    """Return academic DSA concepts, pseudocode, and viva resources."""
    return jsonify({
        "topic": "Queue Data Structure in Food Order Processing",
        "principle": "FIFO (First In, First Out)",
        "complexity": {
            "enqueue": "O(1) Constant Time",
            "dequeue": "O(1) Constant Time",
            "peek": "O(1) Constant Time",
            "is_empty": "O(1) Constant Time",
            "search_by_id": "O(N) Linear Time"
        },
        "pseudocode": {
            "enqueue": (
                "Algorithm Enqueue(Queue, order):\n"
                "  1. newNode = new Node(order)\n"
                "  2. if Queue.isEmpty():\n"
                "         Queue.front = newNode\n"
                "         Queue.rear = newNode\n"
                "     else:\n"
                "         Queue.rear.next = newNode\n"
                "         Queue.rear = newNode\n"
                "  3. Queue.size = Queue.size + 1\n"
                "  4. return True"
            ),
            "dequeue": (
                "Algorithm Dequeue(Queue):\n"
                "  1. if Queue.isEmpty():\n"
                "         raise QueueUnderflowError\n"
                "  2. order = Queue.front.data\n"
                "  3. Queue.front = Queue.front.next\n"
                "  4. if Queue.front is NULL:\n"
                "         Queue.rear = NULL\n"
                "  5. Queue.size = Queue.size - 1\n"
                "  6. return order"
            )
        },
        "academic_details": {
            "title": "Online Food Order Processing System using Queue Data Structure",
            "college": "Dr. D. Y. Patil College of Engineering and Innovation",
            "students": "Ingole Sushant Prakashrao & Bhalke Diksha Sangmeshwar",
            "academic_year": "2026-27"
        }
    })


def find_port():
    import socket
    preferred = int(os.environ.get("PORT", 5001))
    for p in [preferred, 5002, 5003, 8080]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("0.0.0.0", p))
                return p
            except OSError:
                continue
    return preferred


if __name__ == "__main__":
    port = find_port()
    print("=" * 66)
    print(f"  🍔 FoodQueue Pro Web Server Active")
    print(f"  URL: http://127.0.0.1:{port}")
    print("=" * 66)
    app.run(host="0.0.0.0", port=port, debug=True)
