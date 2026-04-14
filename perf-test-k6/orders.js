// Order Creation Performance Test - 1000 Concurrency
// Target: Response time < 300ms, Error rate < 0.1%

import http from 'k6/http';
import { check, sleep, timing } from 'k6';
import { Rate, Average, Median, min, max, percentile } from 'k6/metrics';

// Custom metrics for detailed analysis
const orderSuccessRate = new Rate('order_success_rate');
const responseTimeAvg = new Average('response_time_ms');
const responseTimeP95 = new Percentile('response_time_p95', 95);
const responseTimeP99 = new Percentile('response_time_p99', 99);

// Configuration
const config = {
  baseURL: process.env.BASE_URL || 'http://localhost:8080', // Change to your actual API URL
  rampUp: 60,  // seconds - gradual ramp up over 60s
  duration: '5m', // total test duration
  
  // Test data generators (replace with actual user/order IDs)
  userIds: Array.from({ length: 100 }, (_, i) => `user_${i + 1}`),
};

// Test data pool for realistic testing
const orderData = [];
for (let i = 0; i < 5000; i++) {
  orderData.push({
    orderId: `order_${Math.random().toString(36).substr(2, 9)}`,
    userId: config.userIds[Math.floor(Math.random() * config.userIds.length)],
    items: [{
      productId: `prod_${Math.floor(Math.random() * 1000) + 1}`,
      quantity: Math.floor(Math.random() * 5) + 1,
      price: (Math.random() * 100).toFixed(2),
    }],
    totalAmount: (Math.random() * 500 + 50).toFixed(2),
    shippingAddress: {
      street: 'Test Street ' + Math.floor(Math.random() * 1000),
      city: ['Beijing', 'Shanghai', 'Guangzhou', 'Shenzhen'][Math.floor(Math.random() * 4)],
      province: ['Beijing', 'Shanghai', 'Guangdong'][Math.floor(Math.random() * 3)],
      postalCode: Math.floor(Math.random() * 90000) + 10000,
    },
    paymentMethod: Math.random() > 0.5 ? 'credit_card' : 'wechat_pay',
  });
}

export let options = {
  stages: [
    { duration: config.rampUp, target: 100 },   // Warmup phase
    { duration: 30, target: 200 },             // Gradual increase to 40%
    { duration: 30, target: 500 },             // Medium load (50%)
    { duration: 30, target: 800 },             // High load (80%)
    { duration: 60, target: 1000 },            // Peak load - 1000 concurrent users
    { duration: 60, target: 1000 },            // Sustained peak
    { duration: 30, target: 500 },             // Cool down
    { duration: '1m', target: 0 },              // Ramp to zero
  ],
  thresholds: {
    http_req_duration: ['p(95)<300', 'p(99)<500'], // 95% under 300ms, 99% under 500ms
    order_success_rate: ['rate>0.999'],           // Error rate < 0.1%
    checks: ['rate==1'],                          // All checks must pass
  },
};

// Order creation endpoint - replace with your actual API
function createOrder() {
  const orderId = orderData[Math.floor(Math.random() * orderData.length)];
  
  // Simulate network delay for realistic testing (remove in production)
  sleep(Math.random() * 0.1);
  
  const payload = JSON.stringify({
    ...orderId,
    status: 'pending',
    timestamp: new Date().toISOString(),
  });
  
  const response = http.post(`${config.baseURL}/api/v1/orders`, payload, {
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': process.env.API_KEY || 'test-key',
      // Add any required authentication headers here
    },
    tags: { type: 'order_create' },
  });
  
  const status = response.status;
  const durationMs = (response.time * 1000).toFixed(2);
  
  // Check response
  check(response, {
    'Order creation returned 2xx': (r) => r.status >= 200 && r.status < 300,
    'Response has order_id': (r) => r.json().orderId !== undefined || status === 400, // Allow 400 for validation errors
    'Success rate check': () => {
      const success = status >= 200 && status < 300;
      orderSuccessRate.add(success);
      return success;
    },
  });
  
  // Record metrics
  responseTimeAvg.add(durationMs, { type: 'order_create' });
  responseTimeP95.add(durationMs, { type: 'order_create' });
  responseTimeP99.add(durationMs, { type: 'order_create' });
  
  return response;
}

// Optional: Add think time between requests (remove if not needed)
export function default思() {
  // No think time for pure load testing - remove this function or keep empty
}

// Handle test summary
export function handleSummary(data) {
  const thresholds = {};
  
  for (const [name, values] of Object.entries(data.metrics)) {
    if (values.thresholds) {
      let passed = true;
      for (const threshold of values.thresholds) {
        const [metricName, condition] = threshold.split(':');
        if (!condition || parseFloat(condition.replace('>', '')) > 1.0) {
          thresholds[name] = `passed: ${values.thresholds.filter(t => t.startsWith(name + ':')).length}`;
        }
      }
    } else {
      thresholds[name] = `avg: ${Math.round(values.avg)}, p95: ${values.p[95].toFixed(2)}`;
    }
  }
  
  return { 'stdout': JSON.stringify(thresholds), 'type': 'stdout' };
}
