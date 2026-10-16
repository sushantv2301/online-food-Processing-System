/**
 * Online Food Order Processing System - Core Client Application
 * Handles Cart, State Synchronization, Sound Effects, Queue Visualizer,
 * Live Order Tracking, Kitchen KDS, and Public Counter Displays.
 */

// Application State Store
const AppState = {
  currentTab: 'menu',
  cart: {}, // itemId -> { id, name, price, quantity, icon, is_veg }
  trackedOrderId: 'ORD-105',
  systemState: null,
  soundEnabled: true,
  autoCookTimer: null,
  autoPollInterval: null,
  previousReadyIds: new Set(),
};

// ==========================================
// Web Audio API Sound Synthesizer
// ==========================================
class SoundFX {
  static init() {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AudioContext();
    } catch (e) {
      console.warn("Web Audio API not supported", e);
    }
  }

  static play(type) {
    if (!AppState.soundEnabled) return;
    if (!this.ctx) this.init();
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }

    try {
      const now = this.ctx.currentTime;
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();
      osc.connect(gain);
      gain.connect(this.ctx.destination);

      if (type === 'chime' || type === 'order-placed') {
        // Cheerful ascending chime (C5 -> E5 -> G5)
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(523.25, now);
        osc.frequency.setValueAtTime(659.25, now + 0.1);
        osc.frequency.setValueAtTime(783.99, now + 0.2);
        gain.gain.setValueAtTime(0.2, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.45);
        osc.start(now);
        osc.stop(now + 0.45);
      } else if (type === 'ready' || type === 'bell') {
        // High attention bell sound
        osc.type = 'sine';
        osc.frequency.setValueAtTime(880, now);
        osc.frequency.exponentialRampToValueAtTime(440, now + 0.6);
        gain.gain.setValueAtTime(0.3, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.65);
        osc.start(now);
        osc.stop(now + 0.65);
      } else if (type === 'dequeue') {
        // Soft click / bubble sound
        osc.type = 'sine';
        osc.frequency.setValueAtTime(320, now);
        osc.frequency.exponentialRampToValueAtTime(640, now + 0.12);
        gain.gain.setValueAtTime(0.25, now);
        gain.gain.exponentialRampToValueAtTime(0.01, now + 0.15);
        osc.start(now);
        osc.stop(now + 0.15);
      }
    } catch (e) {
      console.warn("Error playing audio tone", e);
    }
  }
}

// ==========================================
// Tab Navigation
// ==========================================
function switchTab(tabName) {
  AppState.currentTab = tabName;

  // Update tab navigation buttons
  document.querySelectorAll('.nav-tab-btn').forEach(btn => {
    const isCurrent = btn.dataset.tab === tabName;
    if (isCurrent) {
      btn.classList.add('bg-orange-500', 'text-white', 'shadow-md');
      btn.classList.remove('text-gray-600', 'hover:bg-gray-100', 'dark:text-gray-300', 'dark:hover:bg-gray-800');
    } else {
      btn.classList.remove('bg-orange-500', 'text-white', 'shadow-md');
      btn.classList.add('text-gray-600', 'hover:bg-gray-100', 'dark:text-gray-300', 'dark:hover:bg-gray-800');
    }
  });

  // Show/Hide tab views
  document.querySelectorAll('.tab-view').forEach(view => {
    view.classList.add('hidden');
  });

  const activeView = document.getElementById(`tab-content-${tabName}`);
  if (activeView) {
    activeView.classList.remove('hidden');
  }

  // Specific tab triggers
  if (tabName === 'track' && AppState.trackedOrderId) {
    executeTrackOrder(AppState.trackedOrderId);
  }
}

// ==========================================
// Cart Operations
// ==========================================
function addToCart(itemId, name, price, icon, isVeg) {
  if (AppState.cart[itemId]) {
    AppState.cart[itemId].quantity += 1;
  } else {
    AppState.cart[itemId] = {
      id: itemId,
      name: name,
      price: price,
      icon: icon,
      is_veg: isVeg === 'True' || isVeg === true,
      quantity: 1,
    };
  }
  SoundFX.play('dequeue');
  renderCart();
  showToast(`Added ${name} to order ticket!`, 'success');
}

function updateCartQuantity(itemId, delta) {
  if (!AppState.cart[itemId]) return;
  AppState.cart[itemId].quantity += delta;
  if (AppState.cart[itemId].quantity <= 0) {
    delete AppState.cart[itemId];
  }
  renderCart();
}

function clearCart() {
  AppState.cart = {};
  renderCart();
}

function renderCart() {
  const container = document.getElementById('cart-items-container');
  const countBadge = document.getElementById('cart-item-count-badge');
  const subtotalEl = document.getElementById('cart-subtotal');
  const taxEl = document.getElementById('cart-tax');
  const totalEl = document.getElementById('cart-total');
  const checkoutBtn = document.getElementById('btn-submit-order');

  const items = Object.values(AppState.cart);
  const totalCount = items.reduce((sum, itm) => sum + itm.quantity, 0);

  if (countBadge) {
    countBadge.textContent = totalCount;
    countBadge.classList.toggle('hidden', totalCount === 0);
  }

  if (!container) return;

  if (items.length === 0) {
    container.innerHTML = `
      <div class="py-8 text-center text-gray-400">
        <div class="text-4xl mb-2">🛒</div>
        <p class="font-medium text-sm">Your order ticket is empty.</p>
        <p class="text-xs text-gray-500 mt-1">Select items from the food menu to enqueue.</p>
      </div>
    `;
    if (subtotalEl) subtotalEl.textContent = '₹0';
    if (taxEl) taxEl.textContent = '₹0';
    if (totalEl) totalEl.textContent = '₹0';
    if (checkoutBtn) checkoutBtn.disabled = true;
    return;
  }

  let subtotal = 0;
  container.innerHTML = items.map(item => {
    const itemSubtotal = item.price * item.quantity;
    subtotal += itemSubtotal;
    return `
      <div class="flex items-center justify-between p-2.5 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-100 dark:border-gray-700">
        <div class="flex items-center space-x-3">
          <span class="text-xl">${item.icon}</span>
          <div>
            <div class="flex items-center space-x-1.5">
              <span class="text-xs ${item.is_veg ? 'text-green-600' : 'text-red-600'}">●</span>
              <p class="text-xs font-semibold text-gray-800 dark:text-gray-100">${item.name}</p>
            </div>
            <p class="text-xs text-gray-500">₹${item.price} each</p>
          </div>
        </div>

        <div class="flex items-center space-x-2">
          <div class="flex items-center border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700">
            <button onclick="updateCartQuantity('${item.id}', -1)" class="px-2 py-0.5 text-xs text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600">-</button>
            <span class="px-2 text-xs font-bold text-gray-800 dark:text-gray-100">${item.quantity}</span>
            <button onclick="updateCartQuantity('${item.id}', 1)" class="px-2 py-0.5 text-xs text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600">+</button>
          </div>
          <span class="text-xs font-bold text-gray-900 dark:text-gray-100 w-12 text-right">₹${itemSubtotal}</span>
        </div>
      </div>
    `;
  }).join('');

  const tax = Math.round(subtotal * 0.05); // 5% GST
  const grandTotal = subtotal + tax;

  if (subtotalEl) subtotalEl.textContent = `₹${subtotal}`;
  if (taxEl) taxEl.textContent = `₹${tax}`;
  if (totalEl) totalEl.textContent = `₹${grandTotal}`;
  if (checkoutBtn) checkoutBtn.disabled = false;
}

// ==========================================
// Place Order (Enqueue)
// ==========================================
async function submitOrder(e) {
  if (e) e.preventDefault();

  const customerName = document.getElementById('order-customer-name')?.value || 'Guest';
  const orderType = document.getElementById('order-dining-type')?.value || 'Dine-In';
  const tableNumber = document.getElementById('order-table-number')?.value || 'Table 1';
  const notes = document.getElementById('order-chef-notes')?.value || '';

  const items = Object.values(AppState.cart).map(itm => ({
    id: itm.id,
    quantity: itm.quantity,
  }));

  if (items.length === 0) {
    showToast('Please add items to your cart first!', 'error');
    return;
  }

  const btn = document.getElementById('btn-submit-order');
  if (btn) {
    btn.disabled = true;
    btn.innerHTML = `<i class="fas fa-spinner fa-spin mr-2"></i> Enqueuing Order...`;
  }

  try {
    const res = await fetch('/api/order/place', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        customer_name: customerName,
        items: items,
        order_type: orderType,
        table_or_token: tableNumber,
        notes: notes,
      }),
    });

    const data = await res.json();
    if (data.success) {
      SoundFX.play('order-placed');
      clearCart();
      AppState.trackedOrderId = data.order.order_id;

      // Show confirmation modal
      showOrderSuccessModal(data.order);
      fetchSystemStatus(); // Refresh global queue state
    } else {
      showToast(data.error || 'Failed to place order.', 'error');
    }
  } catch (err) {
    console.error('Error submitting order', err);
    showToast('Network error while placing order.', 'error');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = `<i class="fas fa-arrow-down mr-2"></i> Confirm & Enqueue Order`;
    }
  }
}

function showOrderSuccessModal(order) {
  const modal = document.getElementById('modal-order-success');
  if (!modal) return;

  document.getElementById('modal-token-id').textContent = order.order_id;
  document.getElementById('modal-queue-pos').textContent = `Position #${order.queue_position} in Line`;
  document.getElementById('modal-est-time').textContent = `${order.estimated_wait_mins} mins`;
  document.getElementById('modal-cust-name').textContent = order.customer_name;
  document.getElementById('modal-total-amt').textContent = `₹${order.total_price}`;

  modal.classList.remove('hidden');
}

function closeSuccessModal() {
  const modal = document.getElementById('modal-order-success');
  if (modal) modal.classList.add('hidden');
}

function viewTrackFromModal() {
  closeSuccessModal();
  switchTab('track');
  executeTrackOrder(AppState.trackedOrderId);
}

// ==========================================
// Order Tracking
// ==========================================
async function executeTrackOrder(orderId) {
  if (!orderId) {
    orderId = document.getElementById('track-order-input')?.value;
  }
  if (!orderId) {
    showToast('Please enter an Order ID (e.g. ORD-105)', 'warning');
    return;
  }

  orderId = orderId.trim().toUpperCase();
  AppState.trackedOrderId = orderId;

  const container = document.getElementById('track-results-container');
  if (!container) return;

  container.innerHTML = `
    <div class="py-12 text-center text-gray-500">
      <i class="fas fa-circle-notch fa-spin text-3xl text-orange-500 mb-3"></i>
      <p class="text-sm font-medium">Querying Queue & Order Lifecycle Engine for ${orderId}...</p>
    </div>
  `;

  try {
    const res = await fetch(`/api/order/track/${orderId}`);
    const data = await res.json();

    if (!data.success) {
      container.innerHTML = `
        <div class="p-6 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-xl text-center">
          <div class="text-3xl mb-2 text-red-500"><i class="fas fa-exclamation-triangle"></i></div>
          <h4 class="font-bold text-gray-800 dark:text-gray-100">Order Not Found</h4>
          <p class="text-xs text-gray-600 dark:text-gray-400 mt-1">${data.error}</p>
          <div class="mt-4 flex flex-wrap justify-center gap-2">
            <span class="text-xs text-gray-500">Try recent tickets:</span>
            ${['ORD-103', 'ORD-104', 'ORD-105', 'ORD-106'].map(id => `
              <button onclick="executeTrackOrder('${id}')" class="px-2 py-1 text-xs bg-white dark:bg-gray-800 border rounded font-mono text-orange-600 hover:bg-orange-50">${id}</button>
            `).join('')}
          </div>
        </div>
      `;
      return;
    }

    renderTrackingDashboard(data.order);
  } catch (err) {
    console.error('Error tracking order', err);
    container.innerHTML = `<p class="text-red-500 text-center py-6">Failed to retrieve order status.</p>`;
  }
}

function renderTrackingDashboard(order) {
  const container = document.getElementById('track-results-container');
  if (!container) return;

  // Determine stage active states
  // Stages: 1: Placed, 2: Waiting in Queue, 3: Preparing, 4: Ready, 5: Completed
  let stageNumber = 1;
  let statusBadgeClass = "bg-yellow-100 text-yellow-800 border-yellow-300";
  let statusIcon = "fa-clock";

  if (order.status === 'WAITING_IN_QUEUE') {
    stageNumber = 2;
    statusBadgeClass = "bg-amber-100 text-amber-800 border-amber-300 dark:bg-amber-900/40 dark:text-amber-300";
    statusIcon = "fa-layer-group";
  } else if (order.status === 'PREPARING') {
    stageNumber = 3;
    statusBadgeClass = "bg-blue-100 text-blue-800 border-blue-300 dark:bg-blue-900/40 dark:text-blue-300";
    statusIcon = "fa-fire";
  } else if (order.status === 'READY_FOR_PICKUP') {
    stageNumber = 4;
    statusBadgeClass = "bg-emerald-100 text-emerald-800 border-emerald-300 dark:bg-emerald-900/40 dark:text-emerald-300 ready-pulse";
    statusIcon = "fa-bell";
  } else if (order.status === 'COMPLETED') {
    stageNumber = 5;
    statusBadgeClass = "bg-gray-100 text-gray-800 border-gray-300 dark:bg-gray-800 dark:text-gray-300";
    statusIcon = "fa-check-double";
  }

  const stages = [
    { num: 1, name: "Order Placed", desc: "Received into System" },
    { num: 2, name: "In Queue (FIFO)", desc: order.status === 'WAITING_IN_QUEUE' ? `Position #${order.queue_position} in line` : "Waiting stage passed" },
    { num: 3, name: "Cooking in Kitchen", desc: "Chef actively preparing" },
    { num: 4, name: "Ready for Pickup", desc: "Collect at counter!" },
    { num: 5, name: "Completed", desc: "Enjoy your food!" }
  ];

  container.innerHTML = `
    <!-- Order Header Card -->
    <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 shadow-sm mb-6">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-gray-100 dark:border-gray-700">
        <div>
          <div class="flex items-center space-x-3">
            <h3 class="text-2xl font-black text-gray-900 dark:text-white font-mono">${order.order_id}</h3>
            <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold border ${statusBadgeClass}">
              <i class="fas ${statusIcon} mr-1.5"></i> ${order.status_label}
            </span>
          </div>
          <p class="text-xs text-gray-500 mt-1">Placed by <span class="font-semibold text-gray-700 dark:text-gray-300">${order.customer_name}</span> at ${order.placed_at_str} • ${order.order_type} (${order.table_or_token})</p>
        </div>

        <div class="flex items-center space-x-6 text-right">
          ${order.status === 'WAITING_IN_QUEUE' ? `
            <div class="bg-orange-50 dark:bg-orange-950/40 px-4 py-2 rounded-xl border border-orange-200 dark:border-orange-800 text-center">
              <span class="text-xs text-orange-600 dark:text-orange-400 font-semibold uppercase tracking-wider">Queue Position</span>
              <p class="text-2xl font-black text-orange-600 dark:text-orange-400 font-mono">#${order.queue_position}</p>
            </div>
          ` : ''}

          <div class="bg-gray-50 dark:bg-gray-700/50 px-4 py-2 rounded-xl border border-gray-200 dark:border-gray-600 text-center">
            <span class="text-xs text-gray-500 dark:text-gray-400 font-semibold uppercase tracking-wider">Estimated Wait</span>
            <p class="text-2xl font-black text-gray-800 dark:text-gray-100 font-mono">${order.status === 'READY_FOR_PICKUP' ? 'Ready!' : `${order.estimated_wait_mins}m`}</p>
          </div>
        </div>
      </div>

      <!-- 5-Stage Visual Stepper -->
      <div class="py-6">
        <h4 class="text-xs font-bold uppercase tracking-wider text-gray-400 mb-6">Queue & Fulfillment Lifecycle Progress</h4>
        <div class="relative flex items-center justify-between">
          <!-- Connector Background Bar -->
          <div class="absolute left-6 right-6 top-1/2 -translate-y-1/2 h-1.5 bg-gray-200 dark:bg-gray-700 -z-0"></div>
          <!-- Progress Active Fill Bar -->
          <div class="absolute left-6 top-1/2 -translate-y-1/2 h-1.5 bg-orange-500 transition-all duration-500 -z-0"
               style="width: ${((Math.min(stageNumber, 5) - 1) / 4) * 88}%;"></div>

          ${stages.map((stg, idx) => {
            const isCompleted = stageNumber > stg.num;
            const isCurrent = stageNumber === stg.num;
            let nodeBg = "bg-gray-200 text-gray-500 border-gray-300 dark:bg-gray-700 dark:text-gray-400";
            if (isCompleted) nodeBg = "bg-emerald-500 text-white border-emerald-500";
            if (isCurrent) nodeBg = "bg-orange-500 text-white border-orange-500 ring-4 ring-orange-100 dark:ring-orange-950/60";

            return `
              <div class="relative z-10 flex flex-col items-center">
                <div class="w-10 h-10 rounded-full border-2 flex items-center justify-center font-bold text-sm shadow-sm transition-all ${nodeBg}">
                  ${isCompleted ? '<i class="fas fa-check"></i>' : stg.num}
                </div>
                <div class="text-center mt-2">
                  <p class="text-xs font-bold ${isCurrent ? 'text-orange-600 dark:text-orange-400' : 'text-gray-700 dark:text-gray-300'}">${stg.name}</p>
                  <p class="text-[10px] text-gray-400 max-w-[80px] hidden sm:block">${stg.desc}</p>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>

      <!-- Order Details & Activity Log Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-gray-100 dark:border-gray-700">
        <!-- Items in Ticket -->
        <div>
          <h4 class="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3 flex items-center justify-between">
            <span>Ticket Items (${order.total_items})</span>
            <span class="text-orange-600 dark:text-orange-400 font-bold font-mono">Total: ₹${order.total_price}</span>
          </h4>
          <div class="space-y-2">
            ${order.items.map(itm => `
              <div class="flex items-center justify-between text-xs py-1.5 px-3 bg-gray-50 dark:bg-gray-700/40 rounded-lg">
                <span class="flex items-center space-x-2">
                  <span>${itm.icon || '🍽️'}</span>
                  <span class="font-medium text-gray-800 dark:text-gray-200">${itm.name}</span>
                  <span class="text-gray-400">×${itm.quantity}</span>
                </span>
                <span class="font-bold text-gray-700 dark:text-gray-300">₹${itm.price * itm.quantity}</span>
              </div>
            `).join('')}
          </div>
          ${order.notes ? `
            <p class="text-xs text-gray-500 italic mt-2"><i class="fas fa-comment-alt mr-1"></i> "${order.notes}"</p>
          ` : ''}
        </div>

        <!-- FIFO Queue Audit Trail -->
        <div>
          <h4 class="text-xs font-bold uppercase tracking-wider text-gray-500 mb-3">DSA Queue Audit Trail</h4>
          <div class="space-y-2">
            ${(order.history_trail || []).map(step => `
              <div class="text-xs flex items-start space-x-2 p-2 rounded-lg bg-gray-50 dark:bg-gray-700/40 border border-gray-100 dark:border-gray-700">
                <div class="mt-0.5 text-orange-500"><i class="fas fa-check-circle"></i></div>
                <div>
                  <div class="flex items-center space-x-2">
                    <span class="font-semibold text-gray-800 dark:text-gray-200">${step.title}</span>
                    <span class="text-[10px] text-gray-400 font-mono">${step.timestamp}</span>
                  </div>
                  <p class="text-[11px] text-gray-500 dark:text-gray-400">${step.description}</p>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    </div>
  `;
}

// ==========================================
// Kitchen Operations (KDS) & Queue Actions
// ==========================================
async function dequeueNextOrder() {
  const btn = document.getElementById('btn-dequeue-action');
  if (btn) btn.disabled = true;

  try {
    const res = await fetch('/api/kitchen/process-next', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      SoundFX.play('dequeue');
      showToast(`Dequeued ${data.order.order_id} from FRONT! Chef station started.`, 'success');
      fetchSystemStatus();
    } else {
      showToast(data.error || 'Cannot dequeue order.', 'warning');
    }
  } catch (err) {
    console.error('Error dequeuing order', err);
    showToast('Network error during dequeue.', 'error');
  } finally {
    if (btn) btn.disabled = false;
  }
}

async function markOrderReady(orderId) {
  try {
    const res = await fetch('/api/kitchen/mark-ready', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ order_id: orderId }),
    });
    const data = await res.json();
    if (data.success) {
      SoundFX.play('ready');
      showToast(`Order ${orderId} is READY for pickup!`, 'success');
      fetchSystemStatus();
    } else {
      showToast(data.error || 'Failed to update order.', 'error');
    }
  } catch (err) {
    console.error('Error marking order ready', err);
  }
}

async function completeOrderHandover(orderId) {
  try {
    const res = await fetch('/api/kitchen/complete', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ order_id: orderId }),
    });
    const data = await res.json();
    if (data.success) {
      showToast(`Order ${orderId} collected and marked completed.`, 'info');
      fetchSystemStatus();
    } else {
      showToast(data.error || 'Failed to complete order.', 'error');
    }
  } catch (err) {
    console.error('Error completing order', err);
  }
}

async function triggerSimulationStep() {
  try {
    const res = await fetch('/api/kitchen/step', { method: 'POST' });
    const data = await res.json();
    if (data.success && data.actions.length > 0) {
      showToast(data.actions.join(' | '), 'info');
    }
    fetchSystemStatus();
  } catch (err) {
    console.error('Error stepping simulation', err);
  }
}

async function simulateQuickOrder() {
  try {
    const res = await fetch('/api/queue/simulate-order', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      SoundFX.play('order-placed');
      showToast(`Simulated Order ${data.order.order_id} placed by ${data.order.customer_name}!`, 'success');
      fetchSystemStatus();
    }
  } catch (err) {
    console.error('Error simulating order', err);
  }
}

async function resetSystemWorkload() {
  if (!confirm('Reset the queue state and reload clean demonstration orders?')) return;
  try {
    const res = await fetch('/api/queue/reset', { method: 'POST' });
    const data = await res.json();
    if (data.success) {
      showToast('System reset to default state.', 'info');
      fetchSystemStatus();
    }
  } catch (err) {
    console.error('Error resetting system', err);
  }
}

function toggleAutoCookSimulation() {
  const checkbox = document.getElementById('auto-cook-toggle');
  const isEnabled = checkbox ? checkbox.checked : !AppState.autoCookTimer;

  if (isEnabled) {
    AppState.autoCookTimer = setInterval(triggerSimulationStep, 4500);
    showToast('Auto Kitchen Chef Simulation ENABLED (stepping every 4.5s)', 'success');
  } else {
    if (AppState.autoCookTimer) {
      clearInterval(AppState.autoCookTimer);
      AppState.autoCookTimer = null;
    }
    showToast('Auto Kitchen Simulation PAUSED.', 'warning');
  }
}

function toggleSound() {
  AppState.soundEnabled = !AppState.soundEnabled;
  const btn = document.getElementById('btn-sound-toggle');
  if (btn) {
    btn.innerHTML = AppState.soundEnabled
      ? '<i class="fas fa-volume-up"></i>'
      : '<i class="fas fa-volume-mute text-red-400"></i>';
  }
  showToast(AppState.soundEnabled ? 'Audio notifications enabled' : 'Audio notifications muted', 'info');
}

// ==========================================
// Real-Time System State Synchronization
// ==========================================
async function fetchSystemStatus() {
  try {
    const res = await fetch('/api/queue/status');
    const data = await res.json();
    if (data.success) {
      AppState.systemState = data.state;
      renderAllViews(data.state);
    }
  } catch (err) {
    console.warn('Status poll warning', err);
  }
}

function renderAllViews(state) {
  // 1. Update Global Header Counters
  const waitingCount = state.waiting_queue.size;
  const preparingCount = state.preparing_orders.length;
  const readyCount = state.ready_orders.length;
  const completedCount = state.completed_orders.length;

  const headerQueueBadge = document.getElementById('header-queue-size-badge');
  if (headerQueueBadge) headerQueueBadge.textContent = waitingCount;

  // Sound alert if new order reached ready state
  const currentReadyIds = new Set(state.ready_orders.map(o => o.order_id));
  for (const rid of currentReadyIds) {
    if (!AppState.previousReadyIds.has(rid)) {
      SoundFX.play('ready');
      break;
    }
  }
  AppState.previousReadyIds = currentReadyIds;

  // 2. Render Kitchen KDS
  renderKitchenKDS(state);

  // 3. Render Public Pickup Counter Display
  renderCounterDisplay(state);

  // 4. Render Queue DSA Visualizer
  renderQueueDSAVisualizer(state);

  // 5. If tracking tab is active, refresh tracked order if present
  if (AppState.currentTab === 'track' && AppState.trackedOrderId) {
    const found = [
      ...state.waiting_queue.items,
      ...state.preparing_orders,
      ...state.ready_orders,
      ...state.completed_orders
    ].find(o => o.order_id === AppState.trackedOrderId);
    if (found) {
      renderTrackingDashboard(found);
    }
  }
}

// ==========================================
// Kitchen Display System (KDS) View
// ==========================================
function renderKitchenKDS(state) {
  const waitingContainer = document.getElementById('kds-waiting-queue-list');
  const preparingContainer = document.getElementById('kds-preparing-stations');
  const dequeBtn = document.getElementById('btn-dequeue-action');

  if (dequeBtn) {
    dequeBtn.disabled = state.waiting_queue.size === 0;
  }

  // Incoming Waiting Orders Queue
  if (waitingContainer) {
    const items = state.waiting_queue.items;
    if (items.length === 0) {
      waitingContainer.innerHTML = `
        <div class="py-12 text-center text-gray-400 bg-gray-50 dark:bg-gray-800/40 rounded-xl border border-dashed border-gray-300 dark:border-gray-700">
          <i class="fas fa-check-circle text-3xl text-emerald-400 mb-2"></i>
          <p class="font-bold text-sm text-gray-600 dark:text-gray-300">Queue is Clear!</p>
          <p class="text-xs text-gray-400 mt-1">No incoming orders waiting. Customers can place new orders.</p>
        </div>
      `;
    } else {
      waitingContainer.innerHTML = items.map((order, idx) => {
        const isFront = idx === 0;
        const isRear = idx === items.length - 1;

        return `
          <div class="p-4 rounded-xl border transition-all ${
            isFront
              ? 'bg-orange-50/60 dark:bg-orange-950/30 border-orange-300 dark:border-orange-700 queue-front-card shadow-sm'
              : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700'
          }">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-2">
                <span class="text-lg font-black font-mono text-gray-900 dark:text-white">${order.order_id}</span>
                ${isFront ? `
                  <span class="px-2 py-0.5 text-[10px] font-black uppercase tracking-wider bg-orange-600 text-white rounded-md shadow-sm">
                    👑 FRONT (Next in Line)
                  </span>
                ` : ''}
                ${isRear && items.length > 1 ? `
                  <span class="px-2 py-0.5 text-[10px] font-black uppercase tracking-wider bg-blue-600 text-white rounded-md shadow-sm">
                    📍 REAR (Tail)
                  </span>
                ` : ''}
              </div>
              <span class="text-xs font-bold font-mono px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300">
                Position #${idx + 1}
              </span>
            </div>

            <div class="mt-2 flex items-center justify-between text-xs text-gray-500">
              <span>Customer: <strong class="text-gray-800 dark:text-gray-200">${order.customer_name}</strong></span>
              <span>${order.order_type} • ${order.table_or_token}</span>
            </div>

            <div class="mt-2.5 py-2 px-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg text-xs">
              <span class="font-semibold text-gray-700 dark:text-gray-300">Items: </span>
              <span class="text-gray-600 dark:text-gray-400">
                ${order.items.map(i => `${i.quantity}× ${i.name}`).join(', ')}
              </span>
            </div>

            ${isFront ? `
              <div class="mt-3 flex justify-end">
                <button onclick="dequeueNextOrder()" class="px-3 py-1.5 text-xs font-bold bg-orange-500 hover:bg-orange-600 text-white rounded-lg shadow-sm flex items-center space-x-1.5">
                  <i class="fas fa-fire"></i>
                  <span>Process This Front Order (Dequeue)</span>
                </button>
              </div>
            ` : ''}
          </div>
        `;
      }).join('');
    }
  }

  // Active Preparing Cooking Stations
  if (preparingContainer) {
    const prepOrders = state.preparing_orders;
    if (prepOrders.length === 0) {
      preparingContainer.innerHTML = `
        <div class="py-8 text-center text-gray-400 col-span-3 bg-gray-50 dark:bg-gray-800/40 rounded-xl border border-dashed border-gray-300 dark:border-gray-700">
          <i class="fas fa-utensils text-2xl text-gray-400 mb-2"></i>
          <p class="text-xs font-medium">All chef cooking stations are currently idle.</p>
          <p class="text-[11px] text-gray-400 mt-1">Dequeue an order from the waiting queue to begin cooking.</p>
        </div>
      `;
    } else {
      preparingContainer.innerHTML = prepOrders.map(order => `
        <div class="p-4 rounded-xl border border-blue-200 dark:border-blue-800 bg-blue-50/40 dark:bg-blue-950/20 shadow-sm flex flex-col justify-between">
          <div>
            <div class="flex items-center justify-between pb-2 border-b border-blue-100 dark:border-blue-900">
              <span class="font-black text-blue-900 dark:text-blue-200 font-mono text-base">${order.order_id}</span>
              <span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300">
                <i class="fas fa-fire mr-1 text-orange-500"></i> Cooking
              </span>
            </div>
            <p class="text-xs font-semibold text-gray-800 dark:text-gray-200 mt-2">${order.customer_name}</p>
            <p class="text-[11px] text-gray-500">${order.order_type} (${order.table_or_token})</p>

            <div class="mt-3 space-y-1">
              ${order.items.map(itm => `
                <div class="text-xs text-gray-700 dark:text-gray-300 flex items-center justify-between">
                  <span>${itm.icon || '🍲'} ${itm.name}</span>
                  <span class="font-bold text-gray-500">×${itm.quantity}</span>
                </div>
              `).join('')}
            </div>
          </div>

          <div class="mt-4 pt-3 border-t border-blue-100 dark:border-blue-900/60 flex items-center justify-between">
            <span class="text-[11px] text-gray-500 font-mono">Est: ${order.estimated_prep_mins}m</span>
            <button onclick="markOrderReady('${order.order_id}')" class="px-3 py-1.5 text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg shadow-sm flex items-center space-x-1">
              <i class="fas fa-check"></i>
              <span>Mark Ready</span>
            </button>
          </div>
        </div>
      `).join('');
    }
  }
}

// ==========================================
// Pickup Counter Display Board View
// ==========================================
function renderCounterDisplay(state) {
  const prepDisplay = document.getElementById('counter-preparing-grid');
  const readyDisplay = document.getElementById('counter-ready-grid');

  if (prepDisplay) {
    const list = state.preparing_orders;
    if (list.length === 0) {
      prepDisplay.innerHTML = `<p class="text-xs text-gray-400 italic py-6 text-center">No orders currently cooking.</p>`;
    } else {
      prepDisplay.innerHTML = list.map(o => `
        <div class="p-3 bg-gray-800/80 border border-gray-700 rounded-xl flex items-center justify-between">
          <div>
            <span class="text-xl font-black font-mono text-amber-400">${o.order_id}</span>
            <p class="text-[11px] text-gray-400">${o.customer_name} • ${o.table_or_token}</p>
          </div>
          <span class="text-xs font-mono px-2 py-1 bg-amber-500/20 text-amber-300 rounded border border-amber-500/30">
            Cooking...
          </span>
        </div>
      `).join('');
    }
  }

  if (readyDisplay) {
    const list = state.ready_orders;
    if (list.length === 0) {
      readyDisplay.innerHTML = `<p class="text-xs text-gray-400 italic py-6 text-center">No orders awaiting pickup right now.</p>`;
    } else {
      readyDisplay.innerHTML = list.map(o => `
        <div class="p-4 bg-emerald-950/60 border-2 border-emerald-500 rounded-2xl flex items-center justify-between ready-pulse">
          <div>
            <div class="flex items-center space-x-2">
              <span class="text-2xl font-black font-mono text-emerald-400">${o.order_id}</span>
              <span class="text-[10px] font-black uppercase px-2 py-0.5 rounded bg-emerald-500 text-black">READY!</span>
            </div>
            <p class="text-xs text-emerald-200 mt-1">${o.customer_name} • ${o.table_or_token}</p>
          </div>
          <button onclick="completeOrderHandover('${o.order_id}')" class="px-3 py-1.5 text-xs font-bold bg-emerald-500 hover:bg-emerald-400 text-black rounded-lg shadow-sm">
            Collect / Done
          </button>
        </div>
      `).join('');
    }
  }
}

// ==========================================
// Queue DSA Visualizer View
// ==========================================
function renderQueueDSAVisualizer(state) {
  const memoryContainer = document.getElementById('dsa-memory-array-container');
  const logContainer = document.getElementById('dsa-operations-log');
  const sizeBadge = document.getElementById('dsa-metric-size');
  const enqBadge = document.getElementById('dsa-metric-enqueued');
  const deqBadge = document.getElementById('dsa-metric-dequeued');
  const invariantBadge = document.getElementById('dsa-fifo-invariant-badge');

  if (sizeBadge) sizeBadge.textContent = state.waiting_queue.size;
  if (enqBadge) enqBadge.textContent = state.waiting_queue.total_enqueued;
  if (deqBadge) deqBadge.textContent = state.waiting_queue.total_dequeued;

  if (invariantBadge) {
    const isSatisfied = state.analytics.fifo_invariant_satisfied;
    invariantBadge.innerHTML = isSatisfied
      ? `<span class="inline-flex items-center text-xs font-bold text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/50 px-2.5 py-1 rounded-full border border-emerald-200 dark:border-emerald-800"><i class="fas fa-check-shield mr-1.5"></i> Strict FIFO Invariant Validated</span>`
      : `<span class="inline-flex items-center text-xs font-bold text-red-600 bg-red-50 px-2.5 py-1 rounded-full border border-red-200"><i class="fas fa-times-circle mr-1.5"></i> Sequence Invariant Broken</span>`;
  }

  // Memory Nodes Linked Representation
  if (memoryContainer) {
    const items = state.waiting_queue.items;
    if (items.length === 0) {
      memoryContainer.innerHTML = `
        <div class="py-10 text-center w-full text-gray-400">
          <div class="text-2xl mb-1">⊘</div>
          <p class="text-xs font-mono">Queue is Empty: FRONT = NULL, REAR = NULL, Size = 0</p>
        </div>
      `;
    } else {
      let html = '';
      items.forEach((item, index) => {
        const isFront = index === 0;
        const isRear = index === items.length - 1;

        html += `
          <div class="queue-memory-node flex flex-col items-center">
            <!-- Pointers Indicator Row -->
            <div class="h-6 flex items-center justify-center space-x-1 mb-1">
              ${isFront ? `
                <span class="text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded bg-orange-500 text-white shadow-sm flex items-center">
                  FRONT <i class="fas fa-arrow-down ml-1"></i>
                </span>
              ` : ''}
              ${isRear ? `
                <span class="text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded bg-blue-500 text-white shadow-sm flex items-center">
                  REAR <i class="fas fa-arrow-down ml-1"></i>
                </span>
              ` : ''}
            </div>

            <!-- Memory Node Block -->
            <div class="w-32 p-3 rounded-xl border-2 ${
              isFront
                ? 'border-orange-500 bg-orange-50 dark:bg-orange-950/40 text-orange-950 dark:text-orange-200 shadow-md'
                : isRear
                ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/40 text-blue-950 dark:text-blue-200'
                : 'border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100'
            } text-center">
              <div class="text-[10px] font-mono text-gray-400 uppercase tracking-widest pb-1 border-b border-gray-200 dark:border-gray-700">
                Node [${index}]
              </div>
              <div class="text-sm font-black font-mono my-1.5">${item.order_id}</div>
              <div class="text-[10px] truncate font-medium text-gray-600 dark:text-gray-400">${item.customer_name}</div>
              <div class="text-[9px] text-gray-400 mt-0.5 font-mono">₹${item.total_price} • ${item.total_items} items</div>
            </div>

            <!-- Arrow to next -->
            <div class="mt-2 text-xs font-mono text-gray-400">
              ${index < items.length - 1 ? '↓ .next' : '↓ NULL'}
            </div>
          </div>
        `;

        if (index < items.length - 1) {
          html += `<div class="self-center pt-8 text-gray-300 dark:text-gray-600 font-black text-xl">➔</div>`;
        }
      });

      memoryContainer.innerHTML = html;
    }
  }

  // Operations Log
  if (logContainer) {
    const logs = state.waiting_queue.operations_log || [];
    if (logs.length === 0) {
      logContainer.innerHTML = `<p class="text-xs text-gray-400 italic">No queue operations executed yet.</p>`;
    } else {
      logContainer.innerHTML = logs.slice().reverse().map(l => `
        <div class="flex items-center justify-between text-xs py-1.5 px-3 rounded bg-gray-50 dark:bg-gray-800/80 border border-gray-100 dark:border-gray-700 font-mono">
          <div class="flex items-center space-x-2">
            <span class="px-1.5 py-0.5 rounded text-[10px] font-bold ${
              l.operation === 'ENQUEUE' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300' : 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300'
            }">${l.operation}</span>
            <span class="font-bold text-gray-800 dark:text-gray-200">${l.order_id}</span>
            <span class="text-gray-500 text-[11px]">${l.description}</span>
          </div>
          <span class="text-[10px] text-gray-400">${l.timestamp}</span>
        </div>
      `).join('');
    }
  }
}

// ==========================================
// Toast Notifications
// ==========================================
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  const bgColors = {
    success: 'bg-emerald-600 text-white',
    error: 'bg-red-600 text-white',
    warning: 'bg-amber-500 text-white',
    info: 'bg-gray-800 text-white',
  };

  toast.className = `px-4 py-2.5 rounded-xl shadow-lg text-xs font-semibold flex items-center space-x-2 transition-all duration-300 transform translate-y-2 opacity-0 ${bgColors[type] || bgColors.info}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✓' : type === 'error' ? '✕' : 'ℹ'}</span>
    <span>${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.remove('translate-y-2', 'opacity-0');
  }, 10);

  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2');
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

// ==========================================
// Application Bootstrap
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  // Initialize Sound synthesizer on first user gesture
  document.body.addEventListener('click', () => SoundFX.init(), { once: true });

  // Setup Menu Category Filter Buttons
  document.querySelectorAll('.menu-category-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.menu-category-btn').forEach(b => {
        b.classList.remove('bg-orange-500', 'text-white');
        b.classList.add('bg-white', 'text-gray-700', 'dark:bg-gray-800', 'dark:text-gray-200');
      });
      btn.classList.add('bg-orange-500', 'text-white');
      btn.classList.remove('bg-white', 'text-gray-700', 'dark:bg-gray-800', 'dark:text-gray-200');

      const selectedCategory = btn.dataset.category;
      document.querySelectorAll('.food-card-item').forEach(card => {
        if (selectedCategory === 'All' || card.dataset.category === selectedCategory) {
          card.classList.remove('hidden');
        } else {
          card.classList.add('hidden');
        }
      });
    });
  });

  // Initial State Poll and Rendering
  fetchSystemStatus();
  renderCart();

  // Polling interval every 3 seconds for live synchronized dashboard
  AppState.autoPollInterval = setInterval(fetchSystemStatus, 3000);
});
