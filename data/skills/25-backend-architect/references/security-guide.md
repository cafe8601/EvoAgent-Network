# Security Guide

Backend security best practices and OWASP Top 10 (2025) mitigation strategies.

## OWASP Top 10 (2025)

### 1. Broken Access Control (28% of vulnerabilities)

**Risk:** Users access unauthorized resources

**Mitigation:**
```typescript
// Deny by default, explicitly allow
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('admin')
async deleteUser(@Param('id') id: string) {
  // Additional resource-level check
  const user = await this.usersService.findById(id);
  if (user.organizationId !== req.user.organizationId) {
    throw new ForbiddenException();
  }
  return this.usersService.delete(id);
}
```

**Checklist:**
- [ ] Deny by default
- [ ] RBAC implemented
- [ ] Resource-level authorization
- [ ] Access control failures logged
- [ ] Rate limit on auth endpoints

### 2. Cryptographic Failures

**Risk:** Sensitive data exposure, weak encryption

**Password Hashing (Argon2id - 2025 Standard):**
```typescript
import { hash, verify } from 'argon2';

// Hash password
const hashedPassword = await hash(password, {
  type: argon2id,
  memoryCost: 65536,  // 64 MB
  timeCost: 3,
  parallelism: 4,
});

// Verify password
const isValid = await verify(hashedPassword, inputPassword);
```

**Why Argon2id over bcrypt:**
- Memory-hard (resistant to GPU attacks)
- Winner of Password Hashing Competition
- Recommended by OWASP 2025

**Data Encryption:**
```typescript
import { createCipheriv, randomBytes } from 'crypto';

// AES-256-GCM for sensitive data
function encrypt(data: string, key: Buffer): EncryptedData {
  const iv = randomBytes(16);
  const cipher = createCipheriv('aes-256-gcm', key, iv);
  const encrypted = Buffer.concat([
    cipher.update(data, 'utf8'),
    cipher.final(),
  ]);
  return {
    encrypted: encrypted.toString('base64'),
    iv: iv.toString('base64'),
    authTag: cipher.getAuthTag().toString('base64'),
  };
}
```

### 3. Injection Attacks (6x increase 2020-2024)

**98% vulnerability reduction with parameterized queries:**

```typescript
// ❌ VULNERABLE: String concatenation
const query = `SELECT * FROM users WHERE email = '${email}'`;

// ✅ SAFE: Parameterized query
const query = 'SELECT * FROM users WHERE email = $1';
const result = await db.query(query, [email]);

// ✅ SAFE: ORM (Prisma)
const user = await prisma.user.findUnique({
  where: { email },
});
```

**NoSQL Injection Prevention:**
```typescript
// ❌ VULNERABLE
const user = await User.findOne({ email: req.body.email });

// ✅ SAFE: Type validation
const schema = z.object({ email: z.string().email() });
const { email } = schema.parse(req.body);
const user = await User.findOne({ email });
```

### 4. Insecure Design

**Threat Modeling (STRIDE):**
- **S**poofing: Can users impersonate others?
- **T**ampering: Can data be modified?
- **R**epudiation: Can actions be denied?
- **I**nformation Disclosure: Is sensitive data exposed?
- **D**enial of Service: Can the system be overwhelmed?
- **E**levation of Privilege: Can users gain higher access?

**Defense in Depth:**
```
Layer 1: Network Security (WAF, TLS)
Layer 2: Authentication (OAuth, JWT)
Layer 3: Authorization (RBAC)
Layer 4: Input Validation (Zod)
Layer 5: Data Encryption (AES-256)
Layer 6: Monitoring (Audit logs)
```

### 5. Security Misconfiguration

**Security Headers (Helmet.js):**
```typescript
import helmet from 'helmet';

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true,
  },
  referrerPolicy: { policy: 'strict-origin-when-cross-origin' },
}));
```

**Environment Security:**
```typescript
// Never expose in responses
const sensitiveKeys = ['DATABASE_URL', 'JWT_SECRET', 'API_KEYS'];

// Validate all env vars at startup
const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']),
  DATABASE_URL: z.string().url(),
  JWT_SECRET: z.string().min(32),
});
```

### 6. Vulnerable Components

**Dependency Scanning:**
```bash
# npm audit
npm audit --production

# Snyk (recommended)
npx snyk test

# GitHub Dependabot (automatic PRs)
# Configure in .github/dependabot.yml
```

**Lock File Integrity:**
```bash
# Always use lock files
npm ci  # Not npm install in CI/CD
```

### 7. Authentication Failures

**OAuth 2.1 + PKCE (Recommended):**
```typescript
import { OAuth2Client } from 'google-auth-library';

// Generate PKCE challenge
function generatePKCE() {
  const verifier = crypto.randomBytes(32).toString('base64url');
  const challenge = crypto
    .createHash('sha256')
    .update(verifier)
    .digest('base64url');
  return { verifier, challenge };
}

// Token validation
async function validateToken(token: string) {
  const client = new OAuth2Client(CLIENT_ID);
  const ticket = await client.verifyIdToken({
    idToken: token,
    audience: CLIENT_ID,
  });
  return ticket.getPayload();
}
```

**JWT Best Practices:**
```typescript
import jwt from 'jsonwebtoken';

// Sign with RS256 (asymmetric)
const token = jwt.sign(
  { userId, role },
  privateKey,
  {
    algorithm: 'RS256',
    expiresIn: '15m',  // Short-lived access tokens
    issuer: 'your-app',
    audience: 'your-api',
  }
);

// Verify with public key
const decoded = jwt.verify(token, publicKey, {
  algorithms: ['RS256'],
  issuer: 'your-app',
  audience: 'your-api',
});
```

**Refresh Token Rotation:**
```typescript
async function rotateRefreshToken(oldToken: string) {
  // Invalidate old token
  await redis.del(`refresh:${oldToken}`);

  // Generate new tokens
  const accessToken = generateAccessToken(userId);
  const refreshToken = crypto.randomBytes(32).toString('hex');

  // Store new refresh token
  await redis.set(`refresh:${refreshToken}`, userId, 'EX', 7 * 24 * 60 * 60);

  return { accessToken, refreshToken };
}
```

### 8. Data Integrity Failures

**Integrity Verification:**
```typescript
import { createHmac } from 'crypto';

// Sign data
function signData(data: object, secret: string): string {
  const hmac = createHmac('sha256', secret);
  return hmac.update(JSON.stringify(data)).digest('hex');
}

// Verify signature
function verifySignature(data: object, signature: string, secret: string): boolean {
  const expected = signData(data, secret);
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expected)
  );
}
```

### 9. Logging & Monitoring Failures

**Structured Logging:**
```typescript
import winston from 'winston';

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  defaultMeta: { service: 'api' },
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
});

// Security event logging
logger.warn('Authentication failure', {
  ip: req.ip,
  email: req.body.email,
  userAgent: req.headers['user-agent'],
  timestamp: new Date().toISOString(),
});
```

**Audit Trail:**
```typescript
interface AuditLog {
  action: string;
  userId: string;
  resourceType: string;
  resourceId: string;
  changes: object;
  ip: string;
  timestamp: Date;
}

async function logAudit(log: AuditLog) {
  await prisma.auditLog.create({ data: log });
}
```

### 10. Server-Side Request Forgery (SSRF)

**Prevention:**
```typescript
import { URL } from 'url';

function isValidUrl(urlString: string): boolean {
  try {
    const url = new URL(urlString);

    // Block private IPs
    const blockedPatterns = [
      /^127\./,
      /^10\./,
      /^172\.(1[6-9]|2[0-9]|3[0-1])\./,
      /^192\.168\./,
      /^localhost$/i,
    ];

    if (blockedPatterns.some(p => p.test(url.hostname))) {
      return false;
    }

    // Allow only HTTPS
    return url.protocol === 'https:';
  } catch {
    return false;
  }
}
```

## Rate Limiting

```typescript
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';

// General API rate limit
const apiLimiter = rateLimit({
  store: new RedisStore({ client: redisClient }),
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // 100 requests per window
  standardHeaders: true,
  legacyHeaders: false,
});

// Strict auth endpoint limit
const authLimiter = rateLimit({
  store: new RedisStore({ client: redisClient }),
  windowMs: 15 * 60 * 1000,
  max: 5, // 5 attempts per 15 minutes
  skipSuccessfulRequests: true,
});

app.use('/api/', apiLimiter);
app.use('/api/auth/', authLimiter);
```

## Input Validation

```typescript
import { z } from 'zod';

const createUserSchema = z.object({
  email: z.string().email().max(255),
  password: z.string().min(12).max(128),
  name: z.string().min(1).max(100).regex(/^[a-zA-Z\s]+$/),
  age: z.number().int().min(13).max(120).optional(),
});

// Middleware
function validate(schema: z.ZodSchema) {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      req.body = schema.parse(req.body);
      next();
    } catch (error) {
      res.status(422).json({ errors: error.errors });
    }
  };
}
```

## Security Checklist

### Authentication
- [ ] Argon2id for password hashing
- [ ] OAuth 2.1 + PKCE for social login
- [ ] JWT with RS256 algorithm
- [ ] Short-lived access tokens (15min)
- [ ] Refresh token rotation
- [ ] MFA available for sensitive operations

### Authorization
- [ ] RBAC implemented
- [ ] Resource-level permissions
- [ ] Deny by default
- [ ] Least privilege principle

### Data Protection
- [ ] TLS 1.3 for all connections
- [ ] Sensitive data encrypted at rest
- [ ] PII handling compliant with GDPR
- [ ] Secure session management

### API Security
- [ ] Rate limiting configured
- [ ] Input validation on all endpoints
- [ ] Security headers enabled
- [ ] CORS properly configured
- [ ] API versioning implemented

### Monitoring
- [ ] Security events logged
- [ ] Audit trail for sensitive operations
- [ ] Anomaly detection configured
- [ ] Incident response plan ready

## Resources

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- OWASP Cheat Sheets: https://cheatsheetseries.owasp.org/
- OAuth 2.1: https://oauth.net/2.1/
- Argon2: https://github.com/P-H-C/phc-winner-argon2
