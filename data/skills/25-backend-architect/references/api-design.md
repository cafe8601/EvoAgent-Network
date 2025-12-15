# API Design Guide

Comprehensive API design patterns for RESTful, GraphQL, and gRPC APIs (2025).

## API Style Selection

| Scenario | Style | Reason |
|----------|-------|--------|
| Public APIs | REST | Universal compatibility, caching |
| Complex queries | GraphQL | Flexible data fetching, reduce round trips |
| Internal services | gRPC | Performance, type safety, streaming |
| Real-time updates | WebSocket | Bidirectional communication |
| File uploads | REST + Multipart | Standard handling |

## RESTful API Design

### Resource Naming

```
# ✅ Good: Nouns, plural, hierarchical
GET    /users
GET    /users/{id}
GET    /users/{id}/orders
POST   /users
PUT    /users/{id}
DELETE /users/{id}

# ❌ Bad: Verbs, actions in URL
GET    /getUsers
POST   /createUser
GET    /getUserOrders
```

### HTTP Methods

| Method | Usage | Idempotent | Safe |
|--------|-------|------------|------|
| GET | Read resources | Yes | Yes |
| POST | Create resources | No | No |
| PUT | Replace resources | Yes | No |
| PATCH | Partial update | No | No |
| DELETE | Remove resources | Yes | No |

### Status Codes

```typescript
// Success
200 OK           // GET, PUT, PATCH success
201 Created      // POST success (with Location header)
204 No Content   // DELETE success

// Client Errors
400 Bad Request      // Malformed request
401 Unauthorized     // Authentication required
403 Forbidden        // Permission denied
404 Not Found        // Resource doesn't exist
409 Conflict         // Resource conflict
422 Unprocessable    // Validation error

// Server Errors
500 Internal Error   // Server failure
502 Bad Gateway      // Upstream failure
503 Service Unavail  // Temporary unavailability
```

### Response Format

```typescript
// Success Response
{
  "data": {
    "id": "123",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z"
  }
}

// Error Response
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email is invalid",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address"
      }
    ]
  }
}

// Collection Response with Pagination
{
  "data": [...],
  "meta": {
    "total": 100,
    "page": 1,
    "limit": 20,
    "hasMore": true
  },
  "links": {
    "self": "/users?page=1&limit=20",
    "next": "/users?page=2&limit=20",
    "prev": null
  }
}
```

### Pagination Patterns

```typescript
// Offset-based (simple, allows jumping)
GET /users?page=1&limit=20
GET /users?offset=0&limit=20

// Cursor-based (performant, consistent)
GET /users?cursor=eyJpZCI6MTAwfQ&limit=20

// Implementation
interface PaginationParams {
  cursor?: string;
  limit: number;
}

interface PaginatedResponse<T> {
  data: T[];
  nextCursor: string | null;
  hasMore: boolean;
}

async function paginate<T>(
  query: QueryBuilder,
  params: PaginationParams
): Promise<PaginatedResponse<T>> {
  const { cursor, limit } = params;

  if (cursor) {
    const decoded = JSON.parse(Buffer.from(cursor, 'base64').toString());
    query.where('id', '>', decoded.id);
  }

  const items = await query.limit(limit + 1).execute();
  const hasMore = items.length > limit;
  const data = hasMore ? items.slice(0, -1) : items;

  const nextCursor = hasMore
    ? Buffer.from(JSON.stringify({ id: data[data.length - 1].id })).toString('base64')
    : null;

  return { data, nextCursor, hasMore };
}
```

### Filtering & Sorting

```typescript
// URL Query Parameters
GET /users?status=active&role=admin&sort=-createdAt,name

// Implementation
function parseQueryParams(query: Record<string, string>) {
  const filters: Record<string, any> = {};
  const sort: { field: string; order: 'asc' | 'desc' }[] = [];

  // Parse filters
  const allowedFilters = ['status', 'role', 'createdAfter'];
  for (const key of allowedFilters) {
    if (query[key]) {
      filters[key] = query[key];
    }
  }

  // Parse sort (- prefix for descending)
  if (query.sort) {
    for (const field of query.sort.split(',')) {
      const order = field.startsWith('-') ? 'desc' : 'asc';
      sort.push({ field: field.replace('-', ''), order });
    }
  }

  return { filters, sort };
}
```

### Versioning Strategies

```typescript
// URL Path Versioning (Recommended)
GET /api/v1/users
GET /api/v2/users

// Header Versioning
GET /api/users
Accept: application/vnd.api+json; version=1

// Implementation (NestJS)
@Controller({ path: 'users', version: '1' })
export class UsersV1Controller {}

@Controller({ path: 'users', version: '2' })
export class UsersV2Controller {}

// app.module.ts
app.enableVersioning({
  type: VersioningType.URI,
  defaultVersion: '1',
});
```

### HATEOAS (Hypermedia Links)

```typescript
// Response with links
{
  "data": {
    "id": "123",
    "name": "John Doe",
    "status": "pending"
  },
  "links": {
    "self": "/users/123",
    "approve": "/users/123/approve",
    "orders": "/users/123/orders",
    "avatar": "/users/123/avatar"
  },
  "actions": {
    "approve": {
      "method": "POST",
      "href": "/users/123/approve"
    },
    "delete": {
      "method": "DELETE",
      "href": "/users/123"
    }
  }
}
```

## GraphQL Design

### Schema Design

```graphql
# types/User.graphql
type User {
  id: ID!
  email: String!
  name: String!
  role: Role!
  orders(first: Int, after: String): OrderConnection!
  createdAt: DateTime!
}

enum Role {
  USER
  ADMIN
  MODERATOR
}

type OrderConnection {
  edges: [OrderEdge!]!
  pageInfo: PageInfo!
}

type OrderEdge {
  node: Order!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

# queries.graphql
type Query {
  user(id: ID!): User
  users(first: Int, after: String, filter: UserFilter): UserConnection!
  me: User
}

input UserFilter {
  role: Role
  status: UserStatus
  search: String
}

# mutations.graphql
type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
  updateUser(id: ID!, input: UpdateUserInput!): UpdateUserPayload!
  deleteUser(id: ID!): DeleteUserPayload!
}

input CreateUserInput {
  email: String!
  name: String!
  password: String!
}

type CreateUserPayload {
  user: User
  errors: [Error!]
}

type Error {
  field: String
  message: String!
}
```

### Resolver Patterns

```typescript
// resolvers/UserResolver.ts
@Resolver(() => User)
export class UserResolver {
  constructor(
    private userService: UserService,
    private orderService: OrderService
  ) {}

  @Query(() => User, { nullable: true })
  async user(@Args('id') id: string): Promise<User | null> {
    return this.userService.findById(id);
  }

  @Query(() => UserConnection)
  async users(
    @Args() args: ConnectionArgs,
    @Args('filter', { nullable: true }) filter?: UserFilter
  ): Promise<UserConnection> {
    return this.userService.findAll(args, filter);
  }

  @ResolveField(() => OrderConnection)
  async orders(
    @Parent() user: User,
    @Args() args: ConnectionArgs
  ): Promise<OrderConnection> {
    return this.orderService.findByUserId(user.id, args);
  }

  @Mutation(() => CreateUserPayload)
  async createUser(
    @Args('input') input: CreateUserInput
  ): Promise<CreateUserPayload> {
    try {
      const user = await this.userService.create(input);
      return { user, errors: [] };
    } catch (error) {
      return { user: null, errors: [{ message: error.message }] };
    }
  }
}
```

### DataLoader (N+1 Prevention)

```typescript
// loaders/UserLoader.ts
import DataLoader from 'dataloader';

export const createUserLoader = (userService: UserService) =>
  new DataLoader<string, User>(async (ids) => {
    const users = await userService.findByIds(ids);
    const userMap = new Map(users.map(u => [u.id, u]));
    return ids.map(id => userMap.get(id) || null);
  });

// In resolver
@ResolveField(() => User)
async author(
  @Parent() post: Post,
  @Context() { loaders }: GraphQLContext
): Promise<User> {
  return loaders.user.load(post.authorId);
}
```

### Query Complexity

```typescript
// Limit query depth and complexity
import {
  createComplexityRule,
  simpleEstimator
} from 'graphql-query-complexity';

const complexityRule = createComplexityRule({
  maximumComplexity: 1000,
  estimators: [
    simpleEstimator({ defaultComplexity: 1 })
  ],
  onComplete: (complexity) => {
    console.log('Query Complexity:', complexity);
  },
});

// Apply to server
const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [complexityRule],
});
```

## gRPC Design

### Protocol Buffers

```protobuf
// user.proto
syntax = "proto3";

package user.v1;

service UserService {
  rpc GetUser(GetUserRequest) returns (GetUserResponse);
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
  rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
  rpc UpdateUser(UpdateUserRequest) returns (UpdateUserResponse);
  rpc DeleteUser(DeleteUserRequest) returns (DeleteUserResponse);

  // Server streaming
  rpc WatchUsers(WatchUsersRequest) returns (stream UserEvent);

  // Client streaming
  rpc BatchCreateUsers(stream CreateUserRequest) returns (BatchCreateResponse);

  // Bidirectional streaming
  rpc Chat(stream ChatMessage) returns (stream ChatMessage);
}

message User {
  string id = 1;
  string email = 2;
  string name = 3;
  Role role = 4;
  google.protobuf.Timestamp created_at = 5;
}

enum Role {
  ROLE_UNSPECIFIED = 0;
  ROLE_USER = 1;
  ROLE_ADMIN = 2;
}

message GetUserRequest {
  string id = 1;
}

message GetUserResponse {
  User user = 1;
}

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
  UserFilter filter = 3;
}

message ListUsersResponse {
  repeated User users = 1;
  string next_page_token = 2;
}

message UserFilter {
  optional Role role = 1;
  optional string search = 2;
}
```

### gRPC Server (Node.js)

```typescript
// server.ts
import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';

const packageDefinition = protoLoader.loadSync('user.proto', {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});

const proto = grpc.loadPackageDefinition(packageDefinition);

const userService: grpc.UntypedServiceImplementation = {
  getUser: async (call, callback) => {
    const { id } = call.request;
    const user = await userRepo.findById(id);
    callback(null, { user });
  },

  listUsers: async (call, callback) => {
    const { page_size, page_token, filter } = call.request;
    const { users, nextToken } = await userRepo.list({
      limit: page_size,
      cursor: page_token,
      filter,
    });
    callback(null, { users, next_page_token: nextToken });
  },

  watchUsers: (call) => {
    // Server streaming
    const subscription = userEvents.subscribe((event) => {
      call.write(event);
    });

    call.on('cancelled', () => {
      subscription.unsubscribe();
    });
  },
};

const server = new grpc.Server();
server.addService(proto.user.v1.UserService.service, userService);
server.bindAsync(
  '0.0.0.0:50051',
  grpc.ServerCredentials.createInsecure(),
  () => server.start()
);
```

### gRPC Client

```typescript
// client.ts
const client = new proto.user.v1.UserService(
  'localhost:50051',
  grpc.credentials.createInsecure()
);

// Unary call
const user = await new Promise((resolve, reject) => {
  client.getUser({ id: '123' }, (err, response) => {
    if (err) reject(err);
    else resolve(response.user);
  });
});

// Server streaming
const stream = client.watchUsers({});
stream.on('data', (event) => {
  console.log('User event:', event);
});
stream.on('end', () => {
  console.log('Stream ended');
});
```

## API Security

### Authentication Patterns

```typescript
// JWT Bearer Token
@UseGuards(JwtAuthGuard)
@Get('profile')
getProfile(@Request() req) {
  return req.user;
}

// API Key
@UseGuards(ApiKeyGuard)
@Get('data')
getData() {
  return this.dataService.getAll();
}

// OAuth 2.0 Scopes
@UseGuards(OAuth2Guard)
@RequiredScopes(['read:users', 'write:users'])
@Post('users')
createUser(@Body() dto: CreateUserDto) {
  return this.userService.create(dto);
}
```

### Rate Limiting

```typescript
// Express rate limiting
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';

// Tiered rate limits
const tierLimits = {
  free: { windowMs: 60000, max: 60 },      // 60/min
  basic: { windowMs: 60000, max: 300 },    // 300/min
  pro: { windowMs: 60000, max: 1000 },     // 1000/min
  enterprise: { windowMs: 60000, max: 5000 }, // 5000/min
};

const createRateLimiter = (tier: keyof typeof tierLimits) =>
  rateLimit({
    store: new RedisStore({ client: redisClient }),
    ...tierLimits[tier],
    keyGenerator: (req) => req.user?.id || req.ip,
    handler: (req, res) => {
      res.status(429).json({
        error: {
          code: 'RATE_LIMIT_EXCEEDED',
          message: 'Too many requests',
          retryAfter: Math.ceil(req.rateLimit.resetTime / 1000),
        },
      });
    },
  });
```

### Input Validation

```typescript
// Zod validation
import { z } from 'zod';

const createUserSchema = z.object({
  email: z.string().email().max(255),
  password: z.string()
    .min(12, 'Password must be at least 12 characters')
    .max(128)
    .regex(/[A-Z]/, 'Must contain uppercase')
    .regex(/[a-z]/, 'Must contain lowercase')
    .regex(/[0-9]/, 'Must contain number'),
  name: z.string().min(1).max(100),
});

// Validation middleware
function validate<T>(schema: z.ZodSchema<T>) {
  return (req: Request, res: Response, next: NextFunction) => {
    const result = schema.safeParse(req.body);
    if (!result.success) {
      return res.status(422).json({
        error: {
          code: 'VALIDATION_ERROR',
          details: result.error.issues.map(issue => ({
            field: issue.path.join('.'),
            message: issue.message,
          })),
        },
      });
    }
    req.body = result.data;
    next();
  };
}
```

## API Documentation

### OpenAPI/Swagger

```typescript
// NestJS Swagger setup
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';

const config = new DocumentBuilder()
  .setTitle('User API')
  .setDescription('User management API')
  .setVersion('1.0')
  .addBearerAuth()
  .addApiKey({ type: 'apiKey', name: 'X-API-Key', in: 'header' })
  .build();

const document = SwaggerModule.createDocument(app, config);
SwaggerModule.setup('api/docs', app, document);

// Controller decorators
@ApiTags('users')
@Controller('users')
export class UsersController {
  @ApiOperation({ summary: 'Create a new user' })
  @ApiResponse({ status: 201, description: 'User created', type: User })
  @ApiResponse({ status: 422, description: 'Validation error' })
  @ApiBearerAuth()
  @Post()
  create(@Body() dto: CreateUserDto): Promise<User> {
    return this.usersService.create(dto);
  }
}
```

## Best Practices Checklist

### REST API
- [ ] Resources are nouns (plural)
- [ ] Proper HTTP methods used
- [ ] Meaningful status codes returned
- [ ] Consistent response format
- [ ] Pagination implemented
- [ ] Filtering and sorting supported
- [ ] API versioning configured
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] OpenAPI documentation generated

### GraphQL API
- [ ] Schema follows conventions
- [ ] DataLoader prevents N+1
- [ ] Query complexity limited
- [ ] Error handling standardized
- [ ] Subscriptions secured
- [ ] Pagination via connections

### gRPC API
- [ ] Proto files versioned
- [ ] Error codes standardized
- [ ] Streaming patterns correct
- [ ] Health checks implemented
- [ ] Deadlines configured

## Resources

- REST: https://restfulapi.net/
- GraphQL: https://graphql.org/learn/best-practices/
- gRPC: https://grpc.io/docs/guides/
- OpenAPI: https://swagger.io/specification/
