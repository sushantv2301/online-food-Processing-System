"""Food Order Management System with Queue Data Structure Lifecycle.

Coordinates:
- Menu items and pricing
- Order placement into FIFO Waiting Queue
- Kitchen cooking allocation and status tracking
- Order completion and pick-up counter display
- Performance analytics (Wait times, FIFO verification)
"""

from datetime import datetime
import random
import time
from typing import Any, Dict, List, Optional
from src.queue_ds import OrderQueue


# Standard Food Menu catalog
DEFAULT_MENU: List[Dict[str, Any]] = [
    {
        "id": "item-01",
        "name": "Classic Cheeseburger",
        "category": "Burgers",
        "price": 180,
        "is_veg": False,
        "prep_time_mins": 8,
        "calories": 480,
        "icon": "🍔",
        "description": "Grilled patty with melted cheddar, crisp lettuce, tomatoes, and house secret sauce."
    },
    {
        "id": "item-02",
        "name": "Crispy Veggie Deluxe Burger",
        "category": "Burgers",
        "price": 150,
        "is_veg": True,
        "prep_time_mins": 6,
        "calories": 410,
        "icon": "🍔",
        "description": "Herb-infused golden vegetable patty topped with melted cheese slice and garlic mayo."
    },
    {
        "id": "item-03",
        "name": "Spicy Peri-Peri Chicken Burger",
        "category": "Burgers",
        "price": 210,
        "is_veg": False,
        "prep_time_mins": 9,
        "calories": 520,
        "icon": "🍔",
        "description": "Fiery peri-peri marinated chicken breast fillet with caramelized onions and jalapenos."
    },
    {
        "id": "item-04",
        "name": "Margherita Basil Pizza",
        "category": "Pizzas",
        "price": 280,
        "is_veg": True,
        "prep_time_mins": 12,
        "calories": 650,
        "icon": "🍕",
        "description": "Hand-stretched sourdough base, San Marzano tomato marinara, fresh mozzarella, and sweet basil."
    },
    {
        "id": "item-05",
        "name": "Farmhouse Supreme Pizza",
        "category": "Pizzas",
        "price": 340,
        "is_veg": True,
        "prep_time_mins": 14,
        "calories": 720,
        "icon": "🍕",
        "description": "Loaded with bell peppers, sweet corn, mushrooms, olives, and double mozzarella cheese."
    },
    {
        "id": "item-06",
        "name": "Paneer Tikka Kathi Wrap",
        "category": "Wraps & Bowls",
        "price": 170,
        "is_veg": True,
        "prep_time_mins": 7,
        "calories": 390,
        "icon": "🌯",
        "description": "Tandoori smoked paneer cubes tossed in mint chutney wrapped in a flaky whole-wheat paratha."
    },
    {
        "id": "item-07",
        "name": "Dum Biryani Bowl",
        "category": "Wraps & Bowls",
        "price": 240,
        "is_veg": True,
        "prep_time_mins": 10,
        "calories": 560,
        "icon": "🍚",
        "description": "Fragrant basmati rice layered with spiced vegetables, saffron, fried onions, served with mint raita."
    },
    {
        "id": "item-08",
        "name": "Crispy Peri Peri Fries",
        "category": "Sides",
        "price": 110,
        "is_veg": True,
        "prep_time_mins": 5,
        "calories": 310,
        "icon": "🍟",
        "description": "Skin-on golden french fries dusted generously with African peri-peri seasoning."
    },
    {
        "id": "item-09",
        "name": "Cheesy Mozzarella Sticks",
        "category": "Sides",
        "price": 160,
        "is_veg": True,
        "prep_time_mins": 6,
        "calories": 370,
        "icon": "🧀",
        "description": "Stretchy battered mozzarella sticks served with hot Italian marinara dip."
    },
    {
        "id": "item-10",
        "name": "Cold Brew Coffee",
        "category": "Beverages",
        "price": 120,
        "is_veg": True,
        "prep_time_mins": 3,
        "calories": 80,
        "icon": "☕",
        "description": "16-hour steeped Arabica cold brew poured over clear ice with vanilla froth."
    },
    {
        "id": "item-11",
        "name": "Belgian Chocolate Shake",
        "category": "Beverages",
        "price": 160,
        "is_veg": True,
        "prep_time_mins": 4,
        "calories": 420,
        "icon": "🥤",
        "description": "Rich artisanal dark chocolate blend topped with whipped cream and chocolate shavings."
    },
    {
        "id": "item-12",
        "name": "Warm Sizzling Brownie",
        "category": "Desserts",
        "price": 150,
        "is_veg": True,
        "prep_time_mins": 5,
        "calories": 450,
        "icon": "🍰",
        "description": "Fudgy walnut brownie served on a hot sizzler plate with vanilla bean gelato and warm chocolate fudge."
    }
]


class FoodOrderSystem:
    """Manages the full lifecycle of food orders backed by an OrderQueue."""

    def __init__(self, kitchen_capacity: int = 3):
        self.menu: List[Dict[str, Any]] = DEFAULT_MENU
        self.kitchen_capacity: int = kitchen_capacity
        self.order_counter: int = 100

        # Core Queue Data Structure: Strict FIFO Queue for Incoming Orders
        self.waiting_queue = OrderQueue(capacity=50)

        # Active preparation slots (orders currently being cooked)
        self.preparing_orders: List[Dict[str, Any]] = []

        # Orders ready for pickup at the counter
        self.ready_orders: List[Dict[str, Any]] = []

        # Completed/Delivered orders archive
        self.completed_orders: List[Dict[str, Any]] = []

        # Master lookup dictionary for O(1) status queries by order_id
        self.all_orders_lookup: Dict[str, Dict[str, Any]] = {}

        # Simulation settings
        self.auto_cook_enabled: bool = False
        self.simulation_speed_secs: int = 5

        # Seed initial realistic state for presentation
        self._seed_sample_orders()

    def get_menu(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return menu items, optionally filtered by category."""
        if not category or category == "All":
            return self.menu
        return [item for item in self.menu if item["category"].lower() == category.lower()]

    def place_order(
        self,
        customer_name: str,
        items: List[Dict[str, Any]],
        order_type: str = "Dine-In",
        table_or_token: str = "Table 4",
        notes: str = ""
    ) -> Dict[str, Any]:
        """Create and ENQUEUE a new order into the waiting queue.

        Demonstrates ENQUEUE operation of Queue Data Structure.
        """
        if not items:
            raise ValueError("An order must contain at least one item.")

        self.order_counter += 1
        order_id = f"ORD-{self.order_counter}"
        now_ts = time.time()
        time_str = datetime.now().strftime("%I:%M %p")

        # Calculate totals and prep time
        total_price = 0
        max_item_prep = 5
        order_summary_items = []

        menu_map = {item["id"]: item for item in self.menu}

        for entry in items:
            item_id = entry.get("id")
            quantity = int(entry.get("quantity", 1))
            if item_id in menu_map and quantity > 0:
                m_item = menu_map[item_id]
                item_total = m_item["price"] * quantity
                total_price += item_total
                max_item_prep = max(max_item_prep, m_item["prep_time_mins"])
                order_summary_items.append({
                    "id": m_item["id"],
                    "name": m_item["name"],
                    "icon": m_item["icon"],
                    "price": m_item["price"],
                    "quantity": quantity,
                    "subtotal": item_total,
                    "is_veg": m_item["is_veg"]
                })

        if not order_summary_items:
            raise ValueError("No valid menu items selected.")

        # Estimate wait time based on queue length
        # Estimated time = (waiting_queue_size * 2 mins) + max_item_prep
        estimated_wait_mins = (self.waiting_queue.size() * 2) + max_item_prep

        order_record: Dict[str, Any] = {
            "order_id": order_id,
            "order_number": self.order_counter,
            "customer_name": customer_name.strip() or f"Guest-{self.order_counter}",
            "order_type": order_type,
            "table_or_token": table_or_token,
            "notes": notes.strip(),
            "items": order_summary_items,
            "total_items": sum(i["quantity"] for i in order_summary_items),
            "total_price": total_price,
            "estimated_prep_mins": max_item_prep,
            "estimated_wait_mins": estimated_wait_mins,
            "status": "WAITING_IN_QUEUE",
            "status_label": "Waiting in Queue (FIFO)",
            "queue_position": self.waiting_queue.size() + 1,
            "placed_at_ts": now_ts,
            "placed_at_str": time_str,
            "prep_started_at_ts": None,
            "ready_at_ts": None,
            "completed_at_ts": None,
            "history_trail": [
                {
                    "stage": "ORDER_PLACED",
                    "title": "Order Received & Enqueued",
                    "timestamp": time_str,
                    "description": f"Added to REAR of waiting queue. Position: #{self.waiting_queue.size() + 1}."
                }
            ]
        }

        # ENQUEUE into FIFO Waiting Queue
        self.waiting_queue.enqueue(order_record)
        self.all_orders_lookup[order_id] = order_record

        # Update dynamic positions of all waiting orders
        self._refresh_queue_positions()

        return order_record

    def process_next_order(self) -> Optional[Dict[str, Any]]:
        """DEQUEUE the front order from the Waiting Queue and move to Kitchen Preparation.

        Demonstrates DEQUEUE operation of Queue Data Structure.
        Follows strict FIFO: Earliest order received is processed first.
        """
        if self.waiting_queue.is_empty():
            return None

        # Dequeue from FRONT of queue (O(1))
        order = self.waiting_queue.dequeue()
        order_id = order["order_id"]
        time_str = datetime.now().strftime("%I:%M %p")

        order["status"] = "PREPARING"
        order["status_label"] = "Chef Cooking in Kitchen"
        order["prep_started_at_ts"] = time.time()
        order["queue_position"] = 0

        # Calculate actual waiting duration in queue
        queue_wait_duration = int(order["prep_started_at_ts"] - order["placed_at_ts"])
        order["actual_queue_wait_seconds"] = max(1, queue_wait_duration)

        order["history_trail"].append({
            "stage": "PREPARING",
            "title": "Dequeued & Cooking Started",
            "timestamp": time_str,
            "description": f"Dequeued from FRONT of Queue into Kitchen Chef Station. Waited in queue: {order['actual_queue_wait_seconds']}s."
        })

        self.preparing_orders.append(order)
        self.all_orders_lookup[order_id] = order

        self._refresh_queue_positions()
        return order

    def mark_order_ready(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Move an order from Preparing to Ready for Pickup Counter."""
        found_order = None
        for i, o in enumerate(self.preparing_orders):
            if o["order_id"] == order_id:
                found_order = self.preparing_orders.pop(i)
                break

        if not found_order:
            return None

        now_ts = time.time()
        time_str = datetime.now().strftime("%I:%M %p")
        prep_duration = int(now_ts - (found_order["prep_started_at_ts"] or now_ts))

        found_order["status"] = "READY_FOR_PICKUP"
        found_order["status_label"] = "Ready at Pickup Counter!"
        found_order["ready_at_ts"] = now_ts
        found_order["actual_prep_seconds"] = max(2, prep_duration)

        found_order["history_trail"].append({
            "stage": "READY",
            "title": "Cooking Complete - Ready for Pickup",
            "timestamp": time_str,
            "description": f"Ready at pickup counter. Prep duration: {found_order['actual_prep_seconds']}s."
        })

        # Insert at front of ready orders so newest ready appear first
        self.ready_orders.insert(0, found_order)
        self.all_orders_lookup[order_id] = found_order
        return found_order

    def complete_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Mark an order as picked up / completed by customer."""
        found_order = None
        for i, o in enumerate(self.ready_orders):
            if o["order_id"] == order_id:
                found_order = self.ready_orders.pop(i)
                break

        if not found_order:
            # Check if it was directly in preparing
            for i, o in enumerate(self.preparing_orders):
                if o["order_id"] == order_id:
                    found_order = self.preparing_orders.pop(i)
                    break

        if not found_order:
            return None

        now_ts = time.time()
        time_str = datetime.now().strftime("%I:%M %p")
        total_duration = int(now_ts - found_order["placed_at_ts"])

        found_order["status"] = "COMPLETED"
        found_order["status_label"] = "Completed & Handed Over"
        found_order["completed_at_ts"] = now_ts
        found_order["total_turnaround_seconds"] = max(5, total_duration)

        found_order["history_trail"].append({
            "stage": "COMPLETED",
            "title": "Order Handover Completed",
            "timestamp": time_str,
            "description": f"Customer collected order. Total processing time: {found_order['total_turnaround_seconds']}s."
        })

        self.completed_orders.insert(0, found_order)
        self.all_orders_lookup[order_id] = found_order
        return found_order

    def track_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve real-time tracking status for a specific order."""
        clean_id = order_id.strip().upper()
        if not clean_id.startswith("ORD-") and clean_id.isdigit():
            clean_id = f"ORD-{clean_id}"

        order = self.all_orders_lookup.get(clean_id)
        if not order:
            return None

        # Dynamically compute position if waiting
        if order["status"] == "WAITING_IN_QUEUE":
            order["queue_position"] = self.waiting_queue.get_position(clean_id)

        return order

    def get_dashboard_state(self) -> Dict[str, Any]:
        """Aggregate complete system state for real-time frontend synchronization."""
        queue_state = self.waiting_queue.get_state()

        # Update dynamic positions
        for idx, item in enumerate(queue_state["items"]):
            item["queue_position"] = idx + 1

        return {
            "waiting_queue": queue_state,
            "preparing_orders": self.preparing_orders,
            "ready_orders": self.ready_orders,
            "completed_orders": self.completed_orders[:15],  # latest 15 completed
            "auto_cook_enabled": self.auto_cook_enabled,
            "simulation_speed_secs": self.simulation_speed_secs,
            "analytics": self.get_analytics(),
        }

    def get_analytics(self) -> Dict[str, Any]:
        """Compute performance metrics and verify FIFO principle."""
        total_orders = len(self.all_orders_lookup)
        total_revenue = sum(o["total_price"] for o in self.all_orders_lookup.values())

        # Average queue wait time from completed and preparing orders
        recorded_waits = [
            o.get("actual_queue_wait_seconds", 0)
            for o in self.all_orders_lookup.values()
            if "actual_queue_wait_seconds" in o
        ]
        avg_wait_sec = round(sum(recorded_waits) / len(recorded_waits), 1) if recorded_waits else 0

        # Verify FIFO sequence invariant:
        # Check if dequeued order timestamps follow strictly non-decreasing order
        fifo_verified = True
        prev_ts = 0.0
        for log in self.waiting_queue.operations_log:
            if log["operation"] == "DEQUEUE":
                oid = log["order_id"]
                placed_ts = self.all_orders_lookup.get(oid, {}).get("placed_at_ts", 0)
                if placed_ts < prev_ts:
                    fifo_verified = False
                prev_ts = placed_ts

        return {
            "total_orders_received": total_orders,
            "currently_in_queue": self.waiting_queue.size(),
            "currently_preparing": len(self.preparing_orders),
            "currently_ready": len(self.ready_orders),
            "total_completed": len(self.completed_orders),
            "total_revenue_inr": total_revenue,
            "avg_queue_wait_seconds": avg_wait_sec,
            "fifo_invariant_satisfied": fifo_verified,
            "front_order_id": self.waiting_queue.get_state()["front_pointer"],
            "rear_order_id": self.waiting_queue.get_state()["rear_pointer"],
        }

    def simulate_random_order(self) -> Dict[str, Any]:
        """Generate a random realistic customer order for rapid testing and demonstrations."""
        names = ["Aarav Sharma", "Pooja Patel", "Rahul Verma", "Sneha Kulkarni", "Aditya Deshmukh", "Ananya Iyer", "Vikram Rathod", "Rohan Mehta", "Priyanka Joshi"]
        order_types = ["Dine-In", "Takeaway", "Drive-Through"]
        tables = ["Table 1", "Table 4", "Table 7", "Counter Pick", "Table 12"]

        cust = random.choice(names)
        otype = random.choice(order_types)
        table = random.choice(tables)

        sample_items = random.sample(self.menu, k=random.randint(1, 3))
        order_items = [{"id": itm["id"], "quantity": random.randint(1, 2)} for itm in sample_items]

        return self.place_order(
            customer_name=cust,
            items=order_items,
            order_type=otype,
            table_or_token=table,
            notes="Prepared fresh with extra care."
        )

    def step_simulation(self) -> Dict[str, Any]:
        """Perform one discrete simulation step for demonstration:
        1. If any order has been preparing long enough, move to ready.
        2. If any ready order has waited long enough, move to completed.
        3. If kitchen has capacity and queue is not empty, dequeue next order.
        """
        now = time.time()
        actions_taken = []

        # 1. Check ready orders -> complete some
        for o in list(self.ready_orders):
            if now - (o.get("ready_at_ts") or now) >= 15:  # Ready for 15+ seconds
                self.complete_order(o["order_id"])
                actions_taken.append(f"Order {o['order_id']} picked up by customer.")

        # 2. Check preparing orders -> mark ready
        for o in list(self.preparing_orders):
            if now - (o.get("prep_started_at_ts") or now) >= 12:  # Cooked for 12+ seconds
                self.mark_order_ready(o["order_id"])
                actions_taken.append(f"Chef finished cooking {o['order_id']} -> Moved to pickup counter.")

        # 3. Kitchen capacity check -> dequeue from waiting queue
        if len(self.preparing_orders) < self.kitchen_capacity and not self.waiting_queue.is_empty():
            dq = self.process_next_order()
            if dq:
                actions_taken.append(f"Dequeued {dq['order_id']} from FRONT -> Started cooking in kitchen.")

        return {
            "actions_taken": actions_taken,
            "status": self.get_dashboard_state()
        }

    def reset_system(self) -> None:
        """Reset the system and re-seed clean demonstration state."""
        self.waiting_queue.clear()
        self.preparing_orders.clear()
        self.ready_orders.clear()
        self.completed_orders.clear()
        self.all_orders_lookup.clear()
        self.order_counter = 100
        self._seed_sample_orders()

    def _refresh_queue_positions(self) -> None:
        """Update 1-based queue position for all waiting items."""
        curr = self.waiting_queue.front
        pos = 1
        while curr is not None:
            if isinstance(curr.data, dict):
                curr.data["queue_position"] = pos
            curr = curr.next
            pos += 1

    def _seed_sample_orders(self) -> None:
        """Seed realistic initial workload so the application looks rich immediately."""
        now = time.time()

        # Seed 2 completed orders
        for offset, (cid, name, items, price) in enumerate([
            ("ORD-101", "Kunal Sharma", [("item-01", 1), ("item-08", 1)], 290),
            ("ORD-102", "Neha Patil", [("item-04", 1), ("item-10", 1)], 400),
        ]):
            order_data: Dict[str, Any] = {
                "order_id": cid,
                "order_number": 101 + offset,
                "customer_name": name,
                "order_type": "Dine-In",
                "table_or_token": f"Table {offset + 2}",
                "notes": "Fast order",
                "items": [{"name": "Classic Burger / Pizza", "quantity": 1, "price": price, "is_veg": True, "icon": "🍔"}],
                "total_items": 2,
                "total_price": price,
                "estimated_prep_mins": 8,
                "estimated_wait_mins": 8,
                "status": "COMPLETED",
                "status_label": "Completed & Handed Over",
                "queue_position": 0,
                "placed_at_ts": now - 360,
                "placed_at_str": "12:45 PM",
                "prep_started_at_ts": now - 300,
                "ready_at_ts": now - 180,
                "completed_at_ts": now - 60,
                "actual_queue_wait_seconds": 60,
                "actual_prep_seconds": 120,
                "total_turnaround_seconds": 300,
                "history_trail": [
                    {"stage": "ORDER_PLACED", "title": "Order Placed", "timestamp": "12:45 PM", "description": "Enqueued at rear"},
                    {"stage": "PREPARING", "title": "Dequeued to Kitchen", "timestamp": "12:46 PM", "description": "Front of queue reached"},
                    {"stage": "READY", "title": "Cooking Complete", "timestamp": "12:48 PM", "description": "Ready at counter"},
                    {"stage": "COMPLETED", "title": "Customer Handover", "timestamp": "12:50 PM", "description": "Collected successfully"}
                ]
            }
            self.completed_orders.append(order_data)
            self.all_orders_lookup[cid] = order_data

        # Seed 1 Ready order at Pickup Counter
        ready_order: Dict[str, Any] = {
            "order_id": "ORD-103",
            "order_number": 103,
            "customer_name": "Rohan Gupta",
            "order_type": "Takeaway",
            "table_or_token": "Token #12",
            "notes": "Extra ketchup sachets",
            "items": [
                {"name": "Crispy Peri Peri Fries", "quantity": 1, "price": 110, "is_veg": True, "icon": "🍟"},
                {"name": "Belgian Chocolate Shake", "quantity": 1, "price": 160, "is_veg": True, "icon": "🥤"}
            ],
            "total_items": 2,
            "total_price": 270,
            "estimated_prep_mins": 5,
            "estimated_wait_mins": 7,
            "status": "READY_FOR_PICKUP",
            "status_label": "Ready at Pickup Counter!",
            "queue_position": 0,
            "placed_at_ts": now - 180,
            "placed_at_str": "12:52 PM",
            "prep_started_at_ts": now - 120,
            "ready_at_ts": now - 15,
            "completed_at_ts": None,
            "actual_queue_wait_seconds": 60,
            "actual_prep_seconds": 105,
            "history_trail": [
                {"stage": "ORDER_PLACED", "title": "Order Placed", "timestamp": "12:52 PM", "description": "Enqueued into Queue"},
                {"stage": "PREPARING", "title": "Kitchen Dequeue", "timestamp": "12:53 PM", "description": "Chef started preparation"},
                {"stage": "READY", "title": "Ready for Pickup", "timestamp": "12:55 PM", "description": "Food on pickup counter!"}
            ]
        }
        self.ready_orders.append(ready_order)
        self.all_orders_lookup["ORD-103"] = ready_order

        # Seed 1 Preparing Order in Kitchen
        prep_order: Dict[str, Any] = {
            "order_id": "ORD-104",
            "order_number": 104,
            "customer_name": "Ayesha Khan",
            "order_type": "Dine-In",
            "table_or_token": "Table 8",
            "notes": "Make it extra crispy",
            "items": [
                {"name": "Spicy Peri-Peri Chicken Burger", "quantity": 1, "price": 210, "is_veg": False, "icon": "🍔"},
                {"name": "Cold Brew Coffee", "quantity": 1, "price": 120, "is_veg": True, "icon": "☕"}
            ],
            "total_items": 2,
            "total_price": 330,
            "estimated_prep_mins": 9,
            "estimated_wait_mins": 10,
            "status": "PREPARING",
            "status_label": "Chef Cooking in Kitchen",
            "queue_position": 0,
            "placed_at_ts": now - 90,
            "placed_at_str": "12:54 PM",
            "prep_started_at_ts": now - 30,
            "ready_at_ts": None,
            "completed_at_ts": None,
            "actual_queue_wait_seconds": 60,
            "history_trail": [
                {"stage": "ORDER_PLACED", "title": "Order Placed", "timestamp": "12:54 PM", "description": "Enqueued at rear"},
                {"stage": "PREPARING", "title": "Cooking Started", "timestamp": "12:55 PM", "description": "Dequeued to kitchen station"}
            ]
        }
        self.preparing_orders.append(prep_order)
        self.all_orders_lookup["ORD-104"] = prep_order

        # Seed 3 orders in the Waiting FIFO Queue
        sample_waiting = [
            ("ORD-105", "Tanvi Joshi", [("item-02", 2), ("item-09", 1)], "Table 3", 460),
            ("ORD-106", "Siddharth Rao", [("item-05", 1), ("item-11", 1)], "Takeaway", 500),
            ("ORD-107", "Meera Kulkarni", [("item-07", 1), ("item-12", 1)], "Table 6", 390),
        ]

        menu_dict = {item["id"]: item for item in self.menu}

        for idx, (oid, cname, itm_tuples, table_tok, tot_price) in enumerate(sample_waiting):
            order_items = []
            for iid, qty in itm_tuples:
                m = menu_dict[iid]
                order_items.append({
                    "id": m["id"],
                    "name": m["name"],
                    "icon": m["icon"],
                    "price": m["price"],
                    "quantity": qty,
                    "subtotal": m["price"] * qty,
                    "is_veg": m["is_veg"]
                })

            order_obj: Dict[str, Any] = {
                "order_id": oid,
                "order_number": 105 + idx,
                "customer_name": cname,
                "order_type": "Dine-In" if "Table" in table_tok else "Takeaway",
                "table_or_token": table_tok,
                "notes": "Standard preparation",
                "items": order_items,
                "total_items": sum(i["quantity"] for i in order_items),
                "total_price": tot_price,
                "estimated_prep_mins": 8,
                "estimated_wait_mins": (idx + 1) * 3 + 8,
                "status": "WAITING_IN_QUEUE",
                "status_label": "Waiting in Queue (FIFO)",
                "queue_position": idx + 1,
                "placed_at_ts": now - (50 - idx * 15),
                "placed_at_str": f"12:{55 + idx} PM",
                "prep_started_at_ts": None,
                "ready_at_ts": None,
                "completed_at_ts": None,
                "history_trail": [
                    {
                        "stage": "ORDER_PLACED",
                        "title": "Order Placed & Enqueued",
                        "timestamp": f"12:{55 + idx} PM",
                        "description": f"Added to REAR of Queue. Position #{idx + 1}."
                    }
                ]
            }
            self.waiting_queue.enqueue(order_obj)
            self.all_orders_lookup[oid] = order_obj

        self.order_counter = 107
        self._refresh_queue_positions()
