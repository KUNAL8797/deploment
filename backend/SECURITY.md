# Security Configuration Guide

## Production Security Features

### 1. Security Headers

#### Implemented Headers

- **X-Content-Type-Options**: `nosniff` - Prevents MIME type sniffing
- **X-Frame-Options**: `DENY` - Prevents clickjacking attacks
- **X-XSS-Protection**: `1; mode=block` - Legacy XSS protection
- **Strict-Transport-Security**: `max-age=31536000; includeSubDomains; preload` - Forces HTTPS
- **Referrer-Policy**: `strict-origin-when-cross-origin` - Controls referrer information
- **Content-Security-Policy**: Comprehensive CSP policy
- **Permissions-Policy**: Restricts browser features

#### Content Security Policy (CSP)

```
default-src 'self';
script-src 'self';
style-src 'self' 'unsafe-inline';
img-src 'self' data: https:;
font-src 'self' data:;
connect-src 'self' https://generativelanguage.googleapis.com;
frame-ancestors 'none';
base-uri 'self';
form-action 'self'
```

### 2. CORS Configuration

#### Production CORS Settings

- **Origins**: Validated list from environment variables
- **Methods**: `GET, POST, PUT, DELETE, PATCH, OPTIONS`
- **Headers**: Restricted to necessary headers only
- **Credentials**: Enabled for authentication
- **Exposed Headers**: Rate limiting headers

#### CORS Origin Validation

- Automatic validation and sanitization
- Removes trailing slashes
- Validates URL format
- Logs invalid origins

### 3. Rate Limiting

#### Rate Limit Tiers

- **General API**: 100 requests per minute
- **Authentication**: 10 requests per minute
- **Documentation**: No limits (development only)

#### Rate Limit Headers

- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in window
- `X-RateLimit-Reset`: Unix timestamp when limit resets
- `Retry-After`: Seconds to wait before retrying

#### Rate Limit Response

```json
{
  "detail": "Rate limit exceeded for authentication requests",
  "retry_after": 45
}
```

### 4. Security Logging

#### Logged Events

- Authentication attempts (success/failure)
- Security-sensitive endpoint access
- Rate limit violations
- Slow requests (potential DoS)
- Failed requests with client IP

#### Log Format

```
2025-01-16 12:00:00 - security - WARNING - Failed auth attempt: 192.168.1.1 POST /auth/login - 401
2025-01-16 12:00:01 - security - WARNING - Rate limit exceeded for 192.168.1.1 on /auth/login (authentication)
```

### 5. Trusted Host Middleware

#### Production Configuration

- Restricts requests to trusted hosts only
- Allowed hosts: `*.onrender.com`, `localhost`, `127.0.0.1`
- Prevents Host header attacks

### 6. Cache Control

#### Sensitive Endpoints

Authentication and user endpoints have strict cache control:

- `Cache-Control: no-store, no-cache, must-revalidate, private`
- `Pragma: no-cache`
- `Expires: 0`

## Security Configuration

### Environment Variables

#### Required Security Variables

```bash
SECRET_KEY=your-secure-secret-key-here
CORS_ORIGINS=https://your-frontend.vercel.app
ENVIRONMENT=production
```

#### Optional Security Variables

```bash
LOG_LEVEL=INFO
RATE_LIMIT_ENABLED=true
SECURITY_HEADERS_ENABLED=true
```

### Security Middleware Order

Middleware is applied in this order (important for security):

1. Rate Limiting
2. Security Logging
3. CORS
4. Trusted Host (production only)
5. Security Headers

## Security Testing

### 1. Security Headers Test

```bash
# Test security headers
curl -I https://your-backend.onrender.com/

# Should include:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

### 2. CORS Test

```bash
# Test CORS preflight
curl -X OPTIONS https://your-backend.onrender.com/ \
  -H "Origin: https://your-frontend.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type,Authorization"
```

### 3. Rate Limiting Test

```bash
# Test rate limiting (run multiple times quickly)
for i in {1..15}; do
  curl -X POST https://your-backend.onrender.com/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"test","password":"test"}'
done
```

### 4. CSP Test

```bash
# Test Content Security Policy
curl -I https://your-backend.onrender.com/ | grep -i "content-security-policy"
```

## Security Monitoring

### 1. Log Monitoring

Monitor logs for:

- Repeated failed authentication attempts
- Rate limit violations
- Unusual request patterns
- Slow requests

### 2. Security Metrics

Track:

- Authentication success/failure rates
- Rate limit hit rates
- Geographic distribution of requests
- Common attack patterns

### 3. Alerting

Set up alerts for:

- High rate of failed authentications
- Rate limit violations from single IP
- Unusual traffic patterns
- Security header bypass attempts

## Security Best Practices

### 1. Regular Updates

- Keep dependencies updated
- Monitor security advisories
- Update security configurations
- Review and rotate secrets

### 2. Input Validation

- Validate all input data
- Sanitize user inputs
- Use parameterized queries
- Implement proper error handling

### 3. Authentication Security

- Use strong password policies
- Implement account lockout
- Use secure session management
- Enable two-factor authentication (future)

### 4. API Security

- Use HTTPS only
- Implement proper authorization
- Validate API inputs
- Rate limit API endpoints

## Security Incident Response

### 1. Detection

- Monitor security logs
- Set up automated alerts
- Regular security audits
- User reports

### 2. Response

- Isolate affected systems
- Analyze attack vectors
- Implement countermeasures
- Document incidents

### 3. Recovery

- Restore from backups if needed
- Update security measures
- Notify users if required
- Review and improve security

## Compliance and Standards

### 1. Security Standards

- OWASP Top 10 compliance
- Security headers best practices
- CORS security guidelines
- Rate limiting standards

### 2. Privacy

- Data minimization
- Secure data storage
- User consent management
- Data retention policies

## Security Checklist

### Pre-Deployment

- [ ] Security headers configured
- [ ] CORS properly restricted
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] Error handling secure
- [ ] Logging configured
- [ ] Secrets properly managed

### Post-Deployment

- [ ] Security headers verified
- [ ] CORS functionality tested
- [ ] Rate limiting working
- [ ] Monitoring enabled
- [ ] Alerts configured
- [ ] Incident response plan ready
- [ ] Regular security reviews scheduled

## Security Tools and Resources

### 1. Testing Tools

- **Security Headers**: [securityheaders.com](https://securityheaders.com)
- **SSL Test**: [ssllabs.com](https://www.ssllabs.com/ssltest/)
- **CORS Test**: Browser developer tools
- **Rate Limit Test**: Custom scripts or tools

### 2. Monitoring Tools

- Application logs
- Security information and event management (SIEM)
- Intrusion detection systems (IDS)
- Web application firewalls (WAF)

### 3. Resources

- **OWASP**: [owasp.org](https://owasp.org)
- **Security Headers**: [securityheaders.com](https://securityheaders.com)
- **CSP Guide**: [content-security-policy.com](https://content-security-policy.com)
- **CORS Guide**: [developer.mozilla.org](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
