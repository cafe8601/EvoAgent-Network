# Microservices Implementation Patterns

실제 구현 코드와 함께하는 마이크로서비스 패턴 가이드 (2025).

## Service Discovery

### Consul 기반 Service Discovery

```python
# Python - Consul Service Registry
import consul
from typing import List, Optional

class ServiceRegistry:
    """서비스 등록 및 검색을 담당하는 레지스트리"""

    def __init__(self, consul_host: str = "localhost", consul_port: int = 8500):
        self.consul = consul.Consul(host=consul_host, port=consul_port)

    def register_service(
        self,
        service_name: str,
        service_id: str,
        host: str,
        port: int,
        health_check_path: str = "/health"
    ) -> None:
        """서비스 등록 with health check"""
        self.consul.agent.service.register(
            name=service_name,
            service_id=service_id,
            address=host,
            port=port,
            check=consul.Check.http(
                f"http://{host}:{port}{health_check_path}",
                interval="10s",
                timeout="5s"
            ),
            tags=["api", "v1"]
        )

    def deregister_service(self, service_id: str) -> None:
        """서비스 등록 해제"""
        self.consul.agent.service.deregister(service_id)

    def discover_service(self, service_name: str) -> List[str]:
        """정상 상태의 서비스 인스턴스 검색"""
        _, services = self.consul.health.service(service_name, passing=True)
        return [
            f"{s['Service']['Address']}:{s['Service']['Port']}"
            for s in services
        ]

    def get_service_url(self, service_name: str) -> Optional[str]:
        """서비스 URL 하나 반환 (로드 밸런싱용)"""
        instances = self.discover_service(service_name)
        if not instances:
            return None
        # Simple round-robin (production에서는 더 정교한 로직 필요)
        import random
        return f"http://{random.choice(instances)}"


# FastAPI 앱에서 사용
from fastapi import FastAPI
from contextlib import asynccontextmanager

registry = ServiceRegistry()
SERVICE_NAME = "user-service"
SERVICE_ID = f"{SERVICE_NAME}-{os.getpid()}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: 서비스 등록
    registry.register_service(
        service_name=SERVICE_NAME,
        service_id=SERVICE_ID,
        host="0.0.0.0",
        port=8000
    )
    yield
    # Shutdown: 서비스 해제
    registry.deregister_service(SERVICE_ID)

app = FastAPI(lifespan=lifespan)
```

```typescript
// TypeScript/Node.js - Consul Integration
import Consul from 'consul';

interface ServiceInstance {
  address: string;
  port: number;
  id: string;
}

class ServiceDiscovery {
  private consul: Consul.Consul;
  private serviceCache: Map<string, ServiceInstance[]> = new Map();
  private cacheExpiry: Map<string, number> = new Map();
  private cacheTTL = 30000; // 30 seconds

  constructor(host: string = 'localhost', port: number = 8500) {
    this.consul = new Consul({ host, port });
  }

  async register(
    name: string,
    id: string,
    address: string,
    port: number
  ): Promise<void> {
    await this.consul.agent.service.register({
      name,
      id,
      address,
      port,
      check: {
        http: `http://${address}:${port}/health`,
        interval: '10s',
        timeout: '5s',
      },
    });
  }

  async deregister(id: string): Promise<void> {
    await this.consul.agent.service.deregister(id);
  }

  async discover(serviceName: string): Promise<ServiceInstance[]> {
    // Check cache
    const cached = this.serviceCache.get(serviceName);
    const expiry = this.cacheExpiry.get(serviceName);

    if (cached && expiry && Date.now() < expiry) {
      return cached;
    }

    // Fetch from Consul
    const result = await this.consul.health.service({
      service: serviceName,
      passing: true,
    });

    const instances = result.map((entry: any) => ({
      address: entry.Service.Address,
      port: entry.Service.Port,
      id: entry.Service.ID,
    }));

    // Update cache
    this.serviceCache.set(serviceName, instances);
    this.cacheExpiry.set(serviceName, Date.now() + this.cacheTTL);

    return instances;
  }

  async getServiceUrl(serviceName: string): Promise<string | null> {
    const instances = await this.discover(serviceName);
    if (instances.length === 0) return null;

    // Simple random selection
    const instance = instances[Math.floor(Math.random() * instances.length)];
    return `http://${instance.address}:${instance.port}`;
  }
}
```

## Event-Driven Architecture

### RabbitMQ Event Bus

```python
# Python - Event Bus with RabbitMQ (aio-pika)
import asyncio
import json
from typing import Callable, Dict, Any
from datetime import datetime
import aio_pika
from aio_pika import connect_robust, Message, ExchangeType

class EventBus:
    """비동기 이벤트 버스 - RabbitMQ 기반"""

    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self.connection = None
        self.channel = None
        self.exchange = None
        self.handlers: Dict[str, list[Callable]] = {}

    async def connect(self) -> None:
        """RabbitMQ 연결 설정"""
        self.connection = await connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()

        # Topic exchange for flexible routing
        self.exchange = await self.channel.declare_exchange(
            "domain_events",
            ExchangeType.TOPIC,
            durable=True
        )

    async def close(self) -> None:
        """연결 종료"""
        if self.connection:
            await self.connection.close()

    async def publish(
        self,
        event_type: str,
        data: Dict[str, Any],
        correlation_id: str = None
    ) -> None:
        """이벤트 발행"""
        if not self.exchange:
            raise RuntimeError("EventBus not connected")

        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "correlation_id": correlation_id or str(uuid.uuid4())
        }

        message = Message(
            body=json.dumps(event).encode(),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )

        await self.exchange.publish(
            message,
            routing_key=event_type  # e.g., "user.created", "order.completed"
        )

    async def subscribe(
        self,
        event_pattern: str,  # e.g., "user.*", "order.#"
        handler: Callable,
        queue_name: str = None
    ) -> None:
        """이벤트 구독"""
        queue = await self.channel.declare_queue(
            queue_name or f"handler-{event_pattern}",
            durable=True
        )

        await queue.bind(self.exchange, routing_key=event_pattern)

        async def process_message(message: aio_pika.IncomingMessage):
            async with message.process():
                event = json.loads(message.body.decode())
                try:
                    await handler(event)
                except Exception as e:
                    # Dead letter or retry logic
                    print(f"Handler error: {e}")
                    raise

        await queue.consume(process_message)


# 사용 예시
async def main():
    event_bus = EventBus("amqp://guest:guest@localhost/")
    await event_bus.connect()

    # 이벤트 핸들러 등록
    async def on_user_created(event):
        print(f"User created: {event['data']}")
        # 환영 이메일 발송, 분석 이벤트 기록 등

    await event_bus.subscribe("user.created", on_user_created)

    # 이벤트 발행
    await event_bus.publish("user.created", {
        "user_id": "123",
        "email": "user@example.com"
    })
```

```typescript
// TypeScript - Event Bus with RabbitMQ (amqplib)
import amqp, { Channel, Connection, ConsumeMessage } from 'amqplib';

interface DomainEvent<T = any> {
  type: string;
  data: T;
  timestamp: string;
  correlationId: string;
}

type EventHandler<T = any> = (event: DomainEvent<T>) => Promise<void>;

class EventBus {
  private connection: Connection | null = null;
  private channel: Channel | null = null;
  private exchange = 'domain_events';

  constructor(private amqpUrl: string) {}

  async connect(): Promise<void> {
    this.connection = await amqp.connect(this.amqpUrl);
    this.channel = await this.connection.createChannel();

    // Prefetch for fair dispatching
    await this.channel.prefetch(10);

    // Topic exchange
    await this.channel.assertExchange(this.exchange, 'topic', {
      durable: true,
    });
  }

  async close(): Promise<void> {
    await this.channel?.close();
    await this.connection?.close();
  }

  async publish<T>(eventType: string, data: T, correlationId?: string): Promise<void> {
    if (!this.channel) throw new Error('EventBus not connected');

    const event: DomainEvent<T> = {
      type: eventType,
      data,
      timestamp: new Date().toISOString(),
      correlationId: correlationId || crypto.randomUUID(),
    };

    this.channel.publish(
      this.exchange,
      eventType,
      Buffer.from(JSON.stringify(event)),
      {
        persistent: true,
        contentType: 'application/json',
      }
    );
  }

  async subscribe<T>(
    eventPattern: string,
    handler: EventHandler<T>,
    queueName?: string
  ): Promise<void> {
    if (!this.channel) throw new Error('EventBus not connected');

    const queue = await this.channel.assertQueue(
      queueName || `handler-${eventPattern}-${process.pid}`,
      { durable: true }
    );

    await this.channel.bindQueue(queue.queue, this.exchange, eventPattern);

    await this.channel.consume(queue.queue, async (msg: ConsumeMessage | null) => {
      if (!msg) return;

      try {
        const event = JSON.parse(msg.content.toString()) as DomainEvent<T>;
        await handler(event);
        this.channel?.ack(msg);
      } catch (error) {
        console.error('Handler error:', error);
        // Negative ack with requeue for retry
        this.channel?.nack(msg, false, true);
      }
    });
  }
}

// 사용 예시
const eventBus = new EventBus('amqp://localhost');

// NestJS에서 사용
@Injectable()
class OrderService {
  constructor(private eventBus: EventBus) {}

  async createOrder(data: CreateOrderDto): Promise<Order> {
    const order = await this.orderRepo.create(data);

    // 이벤트 발행
    await this.eventBus.publish('order.created', {
      orderId: order.id,
      customerId: order.customerId,
      totalAmount: order.totalAmount,
    });

    return order;
  }
}
```

## Message Queue Patterns

### Kafka Producer/Consumer

```python
# Python - Kafka with aiokafka
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json

class KafkaEventBus:
    """Kafka 기반 이벤트 버스 - 고성능, 대용량 처리용"""

    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None

    async def connect_producer(self) -> None:
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks='all',  # Wait for all replicas
            enable_idempotence=True,  # Exactly-once semantics
        )
        await self.producer.start()

    async def close_producer(self) -> None:
        if self.producer:
            await self.producer.stop()

    async def publish(
        self,
        topic: str,
        data: dict,
        key: str = None,
        partition: int = None
    ) -> None:
        """메시지 발행"""
        await self.producer.send_and_wait(
            topic,
            value=data,
            key=key,
            partition=partition
        )

    @staticmethod
    async def consume(
        topics: list[str],
        group_id: str,
        handler,
        bootstrap_servers: str = "localhost:9092"
    ) -> None:
        """메시지 소비"""
        consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=False,  # Manual commit for reliability
        )

        await consumer.start()
        try:
            async for message in consumer:
                try:
                    await handler(message.value)
                    await consumer.commit()
                except Exception as e:
                    print(f"Handler error: {e}")
                    # Dead letter queue 로직
        finally:
            await consumer.stop()


# 사용 예시
async def order_event_handler(event: dict):
    print(f"Processing order event: {event}")
    # 주문 처리 로직

async def main():
    kafka = KafkaEventBus()
    await kafka.connect_producer()

    # 이벤트 발행
    await kafka.publish(
        "orders",
        {"order_id": "123", "status": "created"},
        key="123"  # Partition key for ordering
    )

    # 소비자 시작 (별도 프로세스)
    await KafkaEventBus.consume(
        topics=["orders"],
        group_id="order-processor",
        handler=order_event_handler
    )
```

### BullMQ Job Queue (Redis)

```typescript
// TypeScript - BullMQ for background jobs
import { Queue, Worker, Job } from 'bullmq';

interface EmailJobData {
  to: string;
  subject: string;
  template: string;
  data: Record<string, any>;
}

// Job Queue 설정
const connection = { host: 'localhost', port: 6379 };

const emailQueue = new Queue<EmailJobData>('email', { connection });

// Producer: 작업 추가
async function sendWelcomeEmail(userId: string, email: string): Promise<void> {
  await emailQueue.add(
    'welcome',
    {
      to: email,
      subject: 'Welcome to Our Platform',
      template: 'welcome',
      data: { userId },
    },
    {
      attempts: 3,
      backoff: {
        type: 'exponential',
        delay: 1000,
      },
      removeOnComplete: { count: 1000 },
      removeOnFail: { count: 5000 },
    }
  );
}

// Consumer: 작업 처리
const emailWorker = new Worker<EmailJobData>(
  'email',
  async (job: Job<EmailJobData>) => {
    const { to, subject, template, data } = job.data;

    console.log(`Processing email job ${job.id}: ${subject} to ${to}`);

    // 실제 이메일 발송 로직
    await sendEmail(to, subject, template, data);

    return { sent: true, timestamp: new Date().toISOString() };
  },
  {
    connection,
    concurrency: 5,  // 동시 처리 수
    limiter: {
      max: 100,      // 최대 100개
      duration: 60000, // 분당
    },
  }
);

// 이벤트 핸들링
emailWorker.on('completed', (job, result) => {
  console.log(`Job ${job.id} completed:`, result);
});

emailWorker.on('failed', (job, err) => {
  console.error(`Job ${job?.id} failed:`, err);
});

emailWorker.on('stalled', (jobId) => {
  console.warn(`Job ${jobId} stalled`);
});
```

## Circuit Breaker Pattern

### Opossum Circuit Breaker

```typescript
// TypeScript - Circuit Breaker with Opossum
import CircuitBreaker from 'opossum';

interface CircuitBreakerOptions {
  timeout?: number;
  errorThresholdPercentage?: number;
  resetTimeout?: number;
  volumeThreshold?: number;
}

function createCircuitBreaker<T>(
  asyncFn: (...args: any[]) => Promise<T>,
  options: CircuitBreakerOptions = {},
  fallback?: (...args: any[]) => T
): CircuitBreaker<T> {
  const breaker = new CircuitBreaker(asyncFn, {
    timeout: options.timeout ?? 3000,           // 3초 타임아웃
    errorThresholdPercentage: options.errorThresholdPercentage ?? 50, // 50% 실패시 open
    resetTimeout: options.resetTimeout ?? 30000, // 30초 후 half-open
    volumeThreshold: options.volumeThreshold ?? 5, // 최소 5회 호출 후 평가
  });

  if (fallback) {
    breaker.fallback(fallback);
  }

  // 모니터링
  breaker.on('success', (result) => {
    console.log('Circuit breaker: success');
  });

  breaker.on('timeout', () => {
    console.warn('Circuit breaker: timeout');
  });

  breaker.on('reject', () => {
    console.warn('Circuit breaker: rejected (circuit open)');
  });

  breaker.on('open', () => {
    console.warn('Circuit breaker: OPENED');
  });

  breaker.on('halfOpen', () => {
    console.info('Circuit breaker: half-open, testing...');
  });

  breaker.on('close', () => {
    console.info('Circuit breaker: CLOSED');
  });

  return breaker;
}

// 사용 예시
class PaymentService {
  private circuitBreaker: CircuitBreaker<PaymentResult>;

  constructor(private stripeClient: StripeClient) {
    this.circuitBreaker = createCircuitBreaker(
      (amount: number, customerId: string) =>
        this.stripeClient.charge(amount, customerId),
      { timeout: 5000, errorThresholdPercentage: 30 },
      () => ({ success: false, error: 'Payment service unavailable' })
    );
  }

  async processPayment(amount: number, customerId: string): Promise<PaymentResult> {
    return this.circuitBreaker.fire(amount, customerId);
  }

  getHealthStatus(): CircuitBreakerStats {
    return {
      state: this.circuitBreaker.opened ? 'open' :
             this.circuitBreaker.halfOpen ? 'half-open' : 'closed',
      stats: this.circuitBreaker.stats,
    };
  }
}
```

### Python Circuit Breaker

```python
# Python - Circuit Breaker with pybreaker
import pybreaker
from functools import wraps

class CircuitBreakerFactory:
    """Circuit Breaker 팩토리"""

    @staticmethod
    def create(
        name: str,
        fail_max: int = 5,
        reset_timeout: int = 30,
        exclude_exceptions: list = None
    ) -> pybreaker.CircuitBreaker:
        """Circuit Breaker 생성"""

        class CircuitListener(pybreaker.CircuitBreakerListener):
            def state_change(self, cb, old_state, new_state):
                print(f"Circuit '{cb.name}': {old_state.name} -> {new_state.name}")

            def failure(self, cb, exc):
                print(f"Circuit '{cb.name}': failure - {exc}")

        return pybreaker.CircuitBreaker(
            name=name,
            fail_max=fail_max,
            reset_timeout=reset_timeout,
            exclude=exclude_exceptions or [],
            listeners=[CircuitListener()]
        )


# 사용 예시
payment_breaker = CircuitBreakerFactory.create(
    name="payment-service",
    fail_max=3,
    reset_timeout=60
)

@payment_breaker
async def charge_payment(amount: float, customer_id: str) -> dict:
    """결제 처리 (Circuit Breaker 적용)"""
    response = await http_client.post(
        "https://payment-api.example.com/charge",
        json={"amount": amount, "customer_id": customer_id}
    )
    response.raise_for_status()
    return response.json()


# Fallback 패턴
async def process_payment_with_fallback(amount: float, customer_id: str) -> dict:
    try:
        return await charge_payment(amount, customer_id)
    except pybreaker.CircuitBreakerError:
        # Circuit이 open 상태일 때
        return {
            "status": "pending",
            "message": "Payment queued for processing",
            "retry_after": 60
        }
```

## Saga Pattern (Distributed Transactions)

```typescript
// TypeScript - Saga Orchestrator
interface SagaStep<T = any> {
  name: string;
  execute: (context: T) => Promise<void>;
  compensate: (context: T) => Promise<void>;
}

class SagaOrchestrator<T> {
  private steps: SagaStep<T>[] = [];
  private executedSteps: SagaStep<T>[] = [];

  addStep(step: SagaStep<T>): this {
    this.steps.push(step);
    return this;
  }

  async execute(context: T): Promise<void> {
    this.executedSteps = [];

    for (const step of this.steps) {
      try {
        console.log(`Executing step: ${step.name}`);
        await step.execute(context);
        this.executedSteps.push(step);
      } catch (error) {
        console.error(`Step ${step.name} failed:`, error);
        await this.compensate(context);
        throw new SagaError(`Saga failed at step: ${step.name}`, error);
      }
    }
  }

  private async compensate(context: T): Promise<void> {
    console.log('Starting compensation...');

    // Reverse order compensation
    for (const step of [...this.executedSteps].reverse()) {
      try {
        console.log(`Compensating step: ${step.name}`);
        await step.compensate(context);
      } catch (error) {
        console.error(`Compensation failed for ${step.name}:`, error);
        // Log for manual intervention
      }
    }
  }
}

// 사용 예시: 주문 처리 Saga
interface OrderContext {
  orderId: string;
  customerId: string;
  items: OrderItem[];
  totalAmount: number;
  paymentId?: string;
  reservationId?: string;
}

const orderSaga = new SagaOrchestrator<OrderContext>()
  .addStep({
    name: 'reserve-inventory',
    execute: async (ctx) => {
      ctx.reservationId = await inventoryService.reserve(ctx.items);
    },
    compensate: async (ctx) => {
      if (ctx.reservationId) {
        await inventoryService.cancelReservation(ctx.reservationId);
      }
    },
  })
  .addStep({
    name: 'process-payment',
    execute: async (ctx) => {
      ctx.paymentId = await paymentService.charge(ctx.customerId, ctx.totalAmount);
    },
    compensate: async (ctx) => {
      if (ctx.paymentId) {
        await paymentService.refund(ctx.paymentId);
      }
    },
  })
  .addStep({
    name: 'confirm-order',
    execute: async (ctx) => {
      await orderService.confirm(ctx.orderId);
    },
    compensate: async (ctx) => {
      await orderService.cancel(ctx.orderId);
    },
  });

// 실행
async function createOrder(orderData: CreateOrderDto): Promise<Order> {
  const context: OrderContext = {
    orderId: uuid(),
    customerId: orderData.customerId,
    items: orderData.items,
    totalAmount: calculateTotal(orderData.items),
  };

  await orderSaga.execute(context);
  return orderService.getById(context.orderId);
}
```

## API Gateway Pattern

```typescript
// TypeScript - Simple API Gateway with Express
import express from 'express';
import httpProxy from 'http-proxy-middleware';
import rateLimit from 'express-rate-limit';

const app = express();

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
});
app.use(limiter);

// Service routing
const serviceRoutes: Record<string, string> = {
  '/api/users': 'http://user-service:3001',
  '/api/orders': 'http://order-service:3002',
  '/api/products': 'http://product-service:3003',
  '/api/payments': 'http://payment-service:3004',
};

// Dynamic proxy setup
for (const [path, target] of Object.entries(serviceRoutes)) {
  app.use(
    path,
    httpProxy.createProxyMiddleware({
      target,
      changeOrigin: true,
      pathRewrite: { [`^${path}`]: '' },
      onError: (err, req, res) => {
        console.error(`Proxy error for ${path}:`, err);
        res.status(503).json({ error: 'Service unavailable' });
      },
    })
  );
}

// Health check aggregation
app.get('/health', async (req, res) => {
  const healthChecks = await Promise.allSettled(
    Object.entries(serviceRoutes).map(async ([path, target]) => {
      const response = await fetch(`${target}/health`);
      return { service: path, healthy: response.ok };
    })
  );

  const status = healthChecks.every(
    (r) => r.status === 'fulfilled' && r.value.healthy
  );

  res.status(status ? 200 : 503).json({
    status: status ? 'healthy' : 'degraded',
    services: healthChecks.map((r) =>
      r.status === 'fulfilled' ? r.value : { service: 'unknown', healthy: false }
    ),
  });
});

app.listen(3000);
```

## Sidecar Pattern (Service Mesh)

```yaml
# Kubernetes - Envoy Sidecar Configuration
apiVersion: v1
kind: Pod
metadata:
  name: user-service
  labels:
    app: user-service
spec:
  containers:
    - name: user-service
      image: user-service:latest
      ports:
        - containerPort: 8080

    - name: envoy-sidecar
      image: envoyproxy/envoy:v1.28.0
      ports:
        - containerPort: 9901  # Admin
        - containerPort: 10000 # Inbound
        - containerPort: 10001 # Outbound
      volumeMounts:
        - name: envoy-config
          mountPath: /etc/envoy

  volumes:
    - name: envoy-config
      configMap:
        name: envoy-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: envoy-config
data:
  envoy.yaml: |
    static_resources:
      listeners:
        - name: inbound
          address:
            socket_address: { address: 0.0.0.0, port_value: 10000 }
          filter_chains:
            - filters:
                - name: envoy.filters.network.http_connection_manager
                  typed_config:
                    "@type": type.googleapis.com/envoy.extensions.filters.network.http_connection_manager.v3.HttpConnectionManager
                    stat_prefix: inbound
                    route_config:
                      virtual_hosts:
                        - name: local_service
                          domains: ["*"]
                          routes:
                            - match: { prefix: "/" }
                              route: { cluster: local_service }
                    http_filters:
                      - name: envoy.filters.http.router
      clusters:
        - name: local_service
          connect_timeout: 1s
          type: STATIC
          load_assignment:
            cluster_name: local_service
            endpoints:
              - lb_endpoints:
                  - endpoint:
                      address:
                        socket_address: { address: 127.0.0.1, port_value: 8080 }
```

## Best Practices Checklist

### Service Discovery
- [ ] Health check endpoint 구현 (`/health`)
- [ ] Graceful shutdown으로 서비스 해제
- [ ] Service discovery 캐싱 (너무 잦은 조회 방지)
- [ ] Multiple instances 지원

### Event-Driven
- [ ] Idempotent event handlers (중복 처리 방지)
- [ ] Dead letter queue 설정
- [ ] Event versioning 전략
- [ ] Correlation ID 전파

### Circuit Breaker
- [ ] 적절한 threshold 설정 (너무 민감하지 않게)
- [ ] Fallback 전략 구현
- [ ] 모니터링 및 알림
- [ ] Half-open 테스트 로직

### Saga Pattern
- [ ] 모든 step에 compensate 구현
- [ ] Compensation 실패 시 수동 처리 방안
- [ ] Saga 상태 영속화 (재시작 시 복구)
- [ ] Timeout 설정

## Resources

- Microservices Patterns: https://microservices.io/patterns/
- Event-Driven Architecture: https://martinfowler.com/articles/201701-event-driven.html
- Saga Pattern: https://microservices.io/patterns/data/saga.html
- Circuit Breaker: https://martinfowler.com/bliki/CircuitBreaker.html
