# Keycloak Deployment - Lessons Learned

## Date: 2025-05-17
## Component: Keycloak (CORE-004)
## AI: Claude 3.7 Sonnet

### Context
During the deployment of Keycloak identity provider component (CORE-004), we encountered authentication issues related to the bootstrap admin user mechanism introduced in Keycloak 26.

### Problem
The initial deployment was failing because:
1. Keycloak 26 deprecated `KEYCLOAK_ADMIN` and `KEYCLOAK_ADMIN_PASSWORD` environment variables
2. The bootstrap admin account is temporary (expires in 2 hours) and uses the username "admin"
3. Our deployment attempted to create a permanent admin also named "admin", causing a username collision
4. Authentication tests were failing with "Invalid user credentials" errors

### Discovery Process
1. **Initial Symptoms**: Authentication failing despite successful deployment
2. **Log Analysis**: Found deprecation warnings for environment variables
3. **Documentation Research**: Discovered Keycloak 26 introduced new bootstrap admin mechanism
4. **Root Cause**: Username collision between temporary bootstrap admin and permanent admin

### Solution
1. **Updated Environment Variables**: Changed from deprecated `KEYCLOAK_ADMIN` to `KC_BOOTSTRAP_ADMIN_USERNAME`
2. **Avoided Username Collision**: Used different username for permanent admin (`tkadmin` vs bootstrap `admin`)
3. **Enhanced Deployment Logic**: 
   - Check if bootstrap admin exists and is valid
   - Fall back to permanent admin if bootstrap expired
   - Skip user creation if already using permanent admin
4. **Standardized Naming**: Used neutral `tkadmin` username suitable for cross-application use

### Key Takeaways
1. **Always Check for Deprecations**: When migrating to newer versions, check for deprecated features
2. **Understand Bootstrap Mechanisms**: Temporary bootstrap accounts have different lifecycle than permanent accounts
3. **Avoid Username Collisions**: Ensure unique usernames across different account types
4. **Neutral Naming for Shared Accounts**: Use application-neutral names for accounts used across multiple services

### Implementation Changes
```yaml
# Environment variable updates
- name: KEYCLOAK_ADMIN           → KC_BOOTSTRAP_ADMIN_USERNAME  
- name: KEYCLOAK_ADMIN_PASSWORD  → KC_BOOTSTRAP_ADMIN_PASSWORD

# Username strategy
- Bootstrap admin: "admin" (temporary, expires in 2 hours)
- Permanent admin: "tkadmin" (neutral, cross-application use)
```

### Testing Verification
All tests passed after implementing the solution:
- Deployment successful
- Authentication working with both bootstrap and permanent admin
- Kubernetes realm properly configured
- Cross-realm user access verified

### Future Considerations
1. Monitor Keycloak release notes for further changes to bootstrap mechanism
2. Consider automated rotation of bootstrap credentials
3. Document the two-tier admin structure for operations team
4. Implement monitoring for bootstrap admin expiration warnings

---
🤖 This lesson was documented based on AI-assisted troubleshooting and implementation