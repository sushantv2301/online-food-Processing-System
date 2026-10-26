# 🍔 Online Food Order Processing System using Queue Data Structure

An interactive, production-grade Web Application and Data Structures & Algorithms (DSA) Mini Project demonstrating the **First-In-First-Out (FIFO) Queue Data Structure** for fair order placement, live status tracking, kitchen preparation dispatch, and order completion counter display.

---

## 🏛️ Academic Project Information
- **Project Title:** Online Food Order Processing System using Queue Data Structure
- **Institution:** Dr. D. Y. Patil College of Engineering and Innovation (DYPCOEI), Varale, Pune
- **Department:** Department of Engineering Science and Humanities
- **Subject / Domain:** Data Structures & Algorithms (Linear Data Structures & Real-World Systems)
- **Academic Year:** 2026-27
- **Project Developers:**
  - **Ingole Sushant Prakashrao**
  - **Bhalke Diksha Sangmeshwar**
  - **More Aniket Arun**

---

## 📌 Problem Statement & Motivation
Quick-service restaurants and online food ordering platforms process hundreds of concurrent customer requests. If orders are processed haphazardly or via a Last-In-First-Out (LIFO / Stack) approach, earlier customers experience indefinite starvation and severe delays.

To guarantee **absolute fairness, deterministic wait times, and zero starvation**, this system implements a strict **First-In-First-Out (FIFO) Queue Data Structure**:
1. **Order Placement ($\text{Enqueue}$):** New customer orders are appended exclusively to the **`REAR`** of the queue in $O(1)$ constant time.
2. **Kitchen Dispatch ($\text{Dequeue}$):** Kitchen chefs process orders exclusively from the **`FRONT`** of the queue in $O(1)$ constant time.
3. **Queue Position Tracking:** Waiting customers observe their dynamic position (`#1 in line`, `#2 in line`, etc.) and estimated preparation wait times in real-time.
4. **Counter Notification:** Prepared orders move to a public digital status board (McDonald's / fast food style) with sound alert chimes.

---

## 🚀 Key Functional Modules

### 1. 🍕 Customer Ordering Station (Enqueue Engine)
- Diverse food catalog across 6 categories (Burgers, Pizzas, Wraps & Bowls, Sides, Beverages, Desserts).
- Detailed attributes: Vegetarian/Non-vegetarian indicators, preparation time in minutes, calories, and prices.
- Live Shopping Cart with item quantity controls, table/token assignments, and special chef notes.
- Instant checkout that creates and **enqueues** the order, immediately issuing an Order ID (e.g., `#ORD-108`), queue position, and dynamic wait estimation.

### 2. 🔍 Real-Time Order Tracking & Visual Stepper
- Customer lookup by Order ID.
- Dynamic 5-stage visual progress timeline:
  1. `Order Placed`: Timestamped and enqueued at queue tail.
  2. `Waiting in Queue`: Live queue position countdown (`Position #K in line`).
  3. `Cooking in Kitchen`: Dequeued by chef; active preparation progress.
  4. `Ready for Pickup`: Flashing alert at pickup counter with audio notification.
  5. `Completed`: Handed over to customer with archived turnaround statistics.

### 3. 📺 Public Pickup Counter Display (Digital Signage)
- Split-screen digital display modeled after McDonald's / Shake Shack order status boards:
  - **Left Section (NOW PREPARING):** Orders actively cooking with remaining minute estimations.
  - **Right Section (READY FOR PICKUP):** Orders ready at the pickup window with glowing badges and audio bell chime.
  - Fullscreen display toggle for counter screens.

### 4. 👨‍🍳 Kitchen Display System (KDS - Dequeue Engine)
- Chef workstation showing the waiting FIFO queue in exact arrival sequence.
- Distinct visual badges for **`👑 FRONT (Next in Line)`** and **`📍 REAR (Tail)`**.
- One-click `Dequeue & Start Cooking` operation.
- Dedicated cooking bays (Chef Station 1, 2, 3) with `Mark Ready` action.
- Automated Kitchen Simulation toggle for unattended classroom presentations.

### 5. 🧠 Queue DSA Visualizer & Memory Lab
- Live interactive memory diagram rendering each node block, data payload, and pointer connections (`.next`).
- Real-time `FRONT` and `REAR` pointer indicators.
- **FIFO Invariant Verification Badge:** Algorithmic validator confirming no order bypassed queue sequence.
- Operations audit log tracking every `ENQUEUE` and `DEQUEUE` timestamp and payload.
- Asymptotic time and space complexity reference table.

---

## 📐 Queue Data Structure Mathematical & Algorithmic Formulation

### 1. The FIFO Principle
Let $O = \{o_1, o_2, o_3, \dots, o_n\}$ be the sequence of orders arriving at timestamps $t(o_1) < t(o_2) < \dots < t(o_n)$.
The Queue invariant mandates that the order of processing satisfies:
$$\text{Dequeue Sequence: } \quad o_1 \prec o_2 \prec o_3 \prec \dots \prec o_n$$

### 2. Algorithm Enqueue ($O(1)$)
```text
Algorithm Enqueue(Queue Q, Order order):
  Input:  Queue Q with pointers front and rear, and a new Order
  Output: Boolean success status

  1.  newNode = allocate Node(order)
  2.  newNode.next = NULL
  3.  if Q.isEmpty() then:
  4.      Q.front = newNode
  5.      Q.rear = newNode
  6.  else:
  7.      Q.rear.next = newNode
  8.      Q.rear = newNode
  9.  Q.size = Q.size + 1
  10. return True
```

### 3. Algorithm Dequeue ($O(1)$)
```text
Algorithm Dequeue(Queue Q):
  Input:  Queue Q with pointers front and rear
  Output: The oldest unserved Order

  1.  if Q.isEmpty() then:
  2.      throw QueueUnderflowException("Cannot dequeue from an empty queue")
  3.  removedNode = Q.front
  4.  order = removedNode.data
  5.  Q.front = Q.front.next
  6.  if Q.front == NULL then:
  7.      Q.rear = NULL
  8.  Q.size = Q.size - 1
  9.  return order
```

### 4. Asymptotic Complexity Analysis
| Operation | Linked-List Queue | Fixed Linear Array | Circular Array Buffer |
| :--- | :---: | :---: | :---: |
| **Enqueue** | $\mathbf{O(1)}$ | $O(1)$ | $\mathbf{O(1)}$ |
| **Dequeue** | $\mathbf{O(1)}$ | $O(N)$ (requires shifting) | $\mathbf{O(1)}$ |
| **Peek / Front** | $\mathbf{O(1)}$ | $O(1)$ | $\mathbf{O(1)}$ |
| **isEmpty** | $\mathbf{O(1)}$ | $O(1)$ | $\mathbf{O(1)}$ |
| **Search by ID** | $\mathbf{O(N)}$ | $O(N)$ | $\mathbf{O(N)}$ |
| **Space Overhead** | $\mathbf{O(N)}$ | $O(\text{Capacity})$ | $\mathbf{O(\text{Capacity})}$ |

---

## 🛠️ Project Directory Structure

```plaintext
MOVIE RECOMMENDATION/
├── app.py                      # Flask Application Controller & REST API
├── run_website.sh              # One-click shell launcher
├── requirements.txt            # Python dependencies (Flask 3.x, etc.)
├── README.md                   # Comprehensive Mini Project Documentation
│
├── src/
│   ├── __init__.py
│   ├── queue_ds.py             # OrderQueue (FIFO), QueueNode, CircularQueue
│   └── order_manager.py        # FoodOrderSystem, Menu, Lifecycle State Manager
│
├── static/
│   ├── css/
│   │   └── styles.css          # Glassmorphism, animations, pointer glows
│   └── js/
│       └── app.js              # Cart, Web Audio API, Tracker, KDS, DSA Visualizer
│
└── templates/
    └── index.html              # Responsive single-page application dashboard
```

---

## ⚡ Quick Start & Execution

### Prerequisites
- Python 3.10+ (Python 3.14 recommended)
- Virtual environment with Flask installed (pre-configured in `./venv`)

### Running the Application
Open a terminal in the project directory and execute:
```bash
./run_website.sh
```

Or manually using Python:
```bash
./venv/bin/python app.py
```

Then open your browser and navigate to:
```
http://127.0.0.1:5001
```

---

## 🎓 Mini Project Viva Examination Guide (Top 10 Q&A)

### Q1. Why is a Queue suitable for food order management rather than a Stack?
> **Answer:** A Stack operates on LIFO (Last-In-First-Out). If a restaurant used a stack, the most recently placed order would be prepared first, while customers who ordered 30 minutes earlier would wait indefinitely (starvation). A Queue enforces FIFO (First-In-First-Out), guaranteeing fairness and predictability.

### Q2. How do you achieve $O(1)$ time complexity for both Enqueue and Dequeue?
> **Answer:** By maintaining two dedicated pointers: `front` pointing to the head of the linked list and `rear` pointing to the tail. Enqueuing updates `rear.next` and advances `rear` in $O(1)$. Dequeuing reads `front.data` and advances `front = front.next` in $O(1)$.

### Q3. What is "False Overflow" in an array-based linear queue?
> **Answer:** In a fixed linear array, when items are dequeued, empty cells appear at the beginning of the array. However, because the `rear` pointer only advances forward, it can hit the maximum index even when the array has plenty of empty space. This is called False Overflow. It is solved using Circular Queues or Linked-List Queues.

### Q4. How does a Circular Queue solve the False Overflow problem?
> **Answer:** A Circular Queue uses modulo arithmetic: `rear = (rear + 1) % capacity`. When the rear pointer reaches the end of the array, it wraps around to index `0` if empty space is available from earlier dequeues.

### Q5. What happens when `dequeue()` is called on an empty queue?
> **Answer:** This condition is known as **Queue Underflow**. In our implementation, `dequeue()` validates `isEmpty()` first and raises an `IndexError / QueueUnderflowException` to prevent null pointer dereferencing.

### Q6. How does the system compute estimated waiting time for an incoming order?
> **Answer:** It uses the formula:
> $$\text{Wait Time} = (\text{Position in Queue} \times \text{Avg Chef Slot Duration}) + \text{Item Prep Duration}$$
> As orders ahead are dequeued, the queue position decrements, dynamically updating the customer's wait time.

### Q7. What is a Priority Queue, and when would it be used in food delivery?
> **Answer:** A Priority Queue serves elements according to priority rank rather than strict arrival time (implemented using a Binary Heap with $O(\log N)$ insertion). In food delivery, Priority Queues are used for VIP members, ambulance/hospital meal deliveries, or cold dessert priority before melting.

### Q8. What is the space complexity of this system?
> **Answer:** $O(N)$ where $N$ is the total number of orders concurrently in the queue and preparation stations. Memory is dynamically allocated when orders are placed and reclaimed upon order completion.

### Q9. Can you cite 3 real-world operating system applications of Queues?
> **Answer:**
> 1. **CPU Process Scheduling:** FCFS (First Come First Served) and Round Robin ready queues.
> 2. **I/O Device Buffers:** Print spoolers storing print requests until the hardware is ready.
> 3. **Asynchronous Message Brokers:** RabbitMQ, Kafka, and Redis message queues in distributed backends.

### Q10. How does the frontend stay synchronized with the backend queue state?
> **Answer:** The frontend polls the REST API endpoint `/api/queue/status` every 3 seconds. Any changes to the queue (new orders, dequeue actions, cooking progress) trigger immediate reactive DOM updates and audio notifications via the Web Audio API.

---

## 📄 License & Attribution
Developed for educational demonstration as an Engineering Mini Project at **Dr. D. Y. Patil College of Engineering and Innovation**, Varale, Pune.
Academic Year: 2026-27.
