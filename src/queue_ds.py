"""Queue Data Structure Implementation for Online Food Order Processing System.

This module implements:
1. LinkedNode: Node for dynamic linked-queue implementation.
2. OrderQueue: Pure First-In-First-Out (FIFO) Queue with O(1) Enqueue & Dequeue.
3. CircularQueue: Fixed-capacity circular buffer demonstration.
4. QueueOperationLog: Operation audit trail for DSA verification and viva demonstrations.
"""

from typing import Any, Dict, List, Optional
import time


class QueueNode:
    """A node in a singly-linked FIFO Queue."""

    def __init__(self, data: Any):
        self.data: Any = data
        self.next: Optional["QueueNode"] = None
        self.enqueued_at: float = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "data": self.data if isinstance(self.data, dict) else str(self.data),
            "enqueued_at": self.enqueued_at,
        }


class OrderQueue:
    """Production-grade First-In-First-Out (FIFO) Queue for Food Order Processing.

    Theoretical Properties:
    - FIFO Principle: The first order placed is the first order processed.
    - Front Pointer: Points to the head element (next order to be cooked/dequeued).
    - Rear Pointer: Points to the tail element (most recently placed order).
    - Enqueue Complexity: O(1) - Constant time insertion at rear.
    - Dequeue Complexity: O(1) - Constant time deletion from front.
    - Peek Complexity: O(1) - Direct access to front node.
    - Space Complexity: O(N) where N is the number of active orders.
    """

    def __init__(self, capacity: Optional[int] = None):
        self.front: Optional[QueueNode] = None
        self.rear: Optional[QueueNode] = None
        self._size: int = 0
        self.capacity: Optional[int] = capacity
        self.total_enqueued: int = 0
        self.total_dequeued: int = 0
        self.operations_log: List[Dict[str, Any]] = []

    def is_empty(self) -> bool:
        """Check whether the queue contains any orders. O(1)"""
        return self._size == 0

    def is_full(self) -> bool:
        """Check whether the queue has reached its maximum capacity (if bounded). O(1)"""
        if self.capacity is None:
            return False
        return self._size >= self.capacity

    def size(self) -> int:
        """Return the current number of orders in the queue. O(1)"""
        return self._size

    def enqueue(self, order: Any) -> bool:
        """Insert a new order at the REAR of the queue.

        Time Complexity: O(1)
        Algorithm:
        1. Check if queue is full (if bounded).
        2. Create a new Node(order).
        3. If queue is empty, set both front and rear to the new node.
        4. Otherwise, set rear.next to new node and advance rear pointer.
        5. Increment size and log operation.
        """
        if self.is_full():
            raise OverflowError("Queue is full! Kitchen cannot take more incoming orders.")

        new_node = QueueNode(order)
        order_id = order.get("order_id", "N/A") if isinstance(order, dict) else str(order)

        if self.is_empty():
            self.front = new_node
            self.rear = new_node
        else:
            assert self.rear is not None
            self.rear.next = new_node
            self.rear = new_node

        self._size += 1
        self.total_enqueued += 1

        self._record_log("ENQUEUE", order_id, f"Order {order_id} added at REAR. Queue size is now {self._size}.")
        return True

    def dequeue(self) -> Any:
        """Remove and return the order at the FRONT of the queue.

        Time Complexity: O(1)
        Algorithm:
        1. Check if queue is empty (Underflow).
        2. Store reference to front.data.
        3. Advance front pointer to front.next.
        4. If front becomes None, also set rear to None.
        5. Decrement size and return stored order.
        """
        if self.is_empty():
            raise IndexError("Queue Underflow: Cannot dequeue from an empty queue.")

        assert self.front is not None
        removed_node = self.front
        order = removed_node.data
        order_id = order.get("order_id", "N/A") if isinstance(order, dict) else str(order)

        # Advance front pointer
        self.front = self.front.next
        if self.front is None:
            self.rear = None

        self._size -= 1
        self.total_dequeued += 1

        self._record_log("DEQUEUE", order_id, f"Order {order_id} processed from FRONT. Queue size is now {self._size}.")
        return order

    def peek(self) -> Optional[Any]:
        """Inspect the FRONT order without removing it.

        Time Complexity: O(1)
        """
        if self.is_empty():
            return None
        assert self.front is not None
        return self.front.data

    def get_position(self, order_id: str) -> int:
        """Find the 1-based position of an order in the queue.

        Returns 1 for the front order (next in line), 2 for second, etc.
        Returns -1 if not found.
        Time Complexity: O(N) traversal.
        """
        current = self.front
        pos = 1
        while current is not None:
            item = current.data
            item_id = item.get("order_id") if isinstance(item, dict) else str(item)
            if item_id == order_id:
                return pos
            current = current.next
            pos += 1
        return -1

    def to_list(self) -> List[Any]:
        """Convert queue elements from FRONT to REAR into a Python list for UI rendering."""
        result = []
        current = self.front
        while current is not None:
            result.append(current.data)
            current = current.next
        return result

    def get_state(self) -> Dict[str, Any]:
        """Return full serialized queue state including front/rear pointers and metrics."""
        items = self.to_list()
        front_order_id = None
        rear_order_id = None

        if self.front is not None and isinstance(self.front.data, dict):
            front_order_id = self.front.data.get("order_id")
        elif self.front is not None:
            front_order_id = str(self.front.data)

        if self.rear is not None and isinstance(self.rear.data, dict):
            rear_order_id = self.rear.data.get("order_id")
        elif self.rear is not None:
            rear_order_id = str(self.rear.data)

        return {
            "size": self._size,
            "is_empty": self.is_empty(),
            "front_pointer": front_order_id,
            "rear_pointer": rear_order_id,
            "total_enqueued": self.total_enqueued,
            "total_dequeued": self.total_dequeued,
            "items": items,
            "operations_log": self.operations_log[-12:],  # Last 12 operations
        }

    def clear(self) -> None:
        """Reset the queue."""
        self.front = None
        self.rear = None
        self._size = 0
        self.operations_log.clear()

    def _record_log(self, operation: str, order_id: str, description: str) -> None:
        """Record queue operation for visual step debugging and academic presentation."""
        self.operations_log.append({
            "operation": operation,
            "order_id": order_id,
            "description": description,
            "queue_size": self._size,
            "timestamp": time.strftime("%H:%M:%S"),
        })
        if len(self.operations_log) > 50:
            self.operations_log.pop(0)


class CircularQueue:
    """Fixed-Array Circular Queue Demonstration for DSA Academic Comparison.

    Demonstrates how Circular Queues solve the 'False Overflow' issue of linear arrays.
    Front and Rear pointers wrap around using modulo arithmetic: (rear + 1) % capacity.
    """

    def __init__(self, capacity: int = 8):
        self.capacity: int = capacity
        self.array: List[Optional[Any]] = [None] * capacity
        self.front: int = -1
        self.rear: int = -1
        self._size: int = 0

    def is_empty(self) -> bool:
        return self._size == 0

    def is_full(self) -> bool:
        return self._size == self.capacity

    def enqueue(self, item: Any) -> bool:
        if self.is_full():
            return False
        if self.is_empty():
            self.front = 0
            self.rear = 0
        else:
            self.rear = (self.rear + 1) % self.capacity
        self.array[self.rear] = item
        self._size += 1
        return True

    def dequeue(self) -> Optional[Any]:
        if self.is_empty():
            return None
        item = self.array[self.front]
        self.array[self.front] = None
        if self.front == self.rear:
            self.front = -1
            self.rear = -1
        else:
            self.front = (self.front + 1) % self.capacity
        self._size -= 1
        return item

    def get_array_representation(self) -> List[Dict[str, Any]]:
        """Return the raw array buffer with front/rear markings for visualization."""
        result = []
        for i in range(self.capacity):
            result.append({
                "index": i,
                "value": self.array[i],
                "is_front": (i == self.front),
                "is_rear": (i == self.rear),
            })
        return result
