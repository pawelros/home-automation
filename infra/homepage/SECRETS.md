# Homepage Secrets Configuration

## Overview

All sensitive credentials (API keys, passwords) are managed through **Pulumi secrets**, not hardcoded in configuration files. This ensures:

- ✅ Secrets are encrypted at rest
- ✅ Secrets are not committed to Git
- ✅ Secrets are stored securely in Pulumi state
- ✅ Configuration files can be safely shared

## Setting Up Secrets

### Required Secrets

Homepage requires the following secrets for service widgets to display live data:

```bash
# Navigate to infra directory
cd /Users/pawelrosinski/x/home-automation/infra

# Set each secret using Pulumi
pulumi config set --secret homepage:jellyseerr_api_key "your-jellyseerr-api-key"
pulumi config set --secret homepage:bazarr_api_key "your-bazarr-api-key"
pulumi config set --secret homepage:prowlarr_api_key "your-prowlarr-api-key"
pulumi config set --secret homepage:sonarr_api_key "your-sonarr-api-key"
pulumi config set --secret homepage:radarr_api_key "your-radarr-api-key"
pulumi config set --secret homepage:lidarr_api_key "your-lidarr-api-key"
pulumi config set --secret homepage:qbittorrent_username "your-username"
pulumi config set --secret homepage:qbittorrent_password "your-password"
pulumi config set --secret homepage:unifi_username "your-unifi-username"
pulumi config set --secret homepage:unifi_api_key "your-unifi-api-key"
pulumi config set --secret homepage:proxmox_username "root@pam"
pulumi config set --secret homepage:proxmox_api_token "your-proxmox-api-token"
```

### How to Get API Keys

#### *arr Services (Sonarr, Radarr, Lidarr, Prowlarr, Bazarr)

1. Open the service web interface
2. Navigate to: **Settings** → **General** → **Security**
3. Copy the **API Key**

#### Jellyseerr

1. Open Jellyseerr
2. Go to: **Settings** → **General**
3. Copy the **API Key**

#### qBittorrent

- Use your qBittorrent web UI username and password

#### UniFi Controller

**Important**: UniFi API key is recommended, especially if you have MFA enabled.

To create a UniFi API key:

1. Log into your UniFi Controller (https://192.168.1.49)
2. Go to **Settings** → **Admins** (or **System** → **Admins**)
3. Click on your admin user
4. Scroll down to **API Access**
5. Click **Create New API Key** or **Generate API Token**
6. Copy the API key (you won't be able to see it again!)
7. For username, use your UniFi admin username

**Note**: The API key works even with MFA enabled, unlike username/password authentication.

#### Proxmox

To create a Proxmox API token:

1. Log into your Proxmox web interface (https://192.168.1.180:8006)
2. Go to **Datacenter** → **Permissions** → **API Tokens**
3. Click **Add**
4. Select user (typically `root@pam`)
5. Enter a Token ID (e.g., `homepage`)
6. **Uncheck** "Privilege Separation" (so token has same permissions as user)
7. Click **Add**
8. Copy the token secret (shown as `PVEAPIToken=USER@REALM!TOKENID=UUID`)
9. Use the full token string for `proxmox_api_token`
10. Username should be `root@pam` (or your Proxmox user)

**Format**: The API token should be in format: `root@pam!tokenid=<secret>`

## Verification

After setting secrets, verify they're stored:

```bash
# List all config values (secrets will show as [secret])
pulumi config

# Should show something like:
# KEY                                VALUE
# homepage:bazarr_api_key            [secret]
# homepage:jellyseerr_api_key        [secret]
# homepage:lidarr_api_key            [secret]
# homepage:prowlarr_api_key          [secret]
# homepage:qbittorrent_password      [secret]
# homepage:qbittorrent_username      [secret]
# homepage:radarr_api_key            [secret]
# homepage:sonarr_api_key            [secret]
# homepage:unifi_api_key             [secret]
# homepage:unifi_username            [secret]
```

## Deployment

Once secrets are configured, deploy Homepage:

```bash
pulumi up
```

The secrets will be:
1. Read from Pulumi config
2. Injected into the `services.yaml` configuration
3. Stored in the Kubernetes ConfigMap
4. Used by Homepage to fetch live data from services

## Updating Secrets

To update a secret:

```bash
pulumi config set --secret homepage:sonarr_api_key "new-api-key"
pulumi up
```

The deployment will update with the new secret value.

## Removing Secrets

To remove a secret:

```bash
pulumi config rm homepage:sonarr_api_key
pulumi up
```

The widget for that service will be disabled (empty key).

## Optional Secrets

All secrets are **optional**. If a secret is not set:

- The service will still appear on the dashboard
- The widget will be disabled (no live data)
- You can click through to access the service manually

This allows you to:
- Deploy Homepage immediately without any configuration
- Add API keys incrementally as you collect them
- Disable widgets for services you don't want to monitor

## Security Best Practices

### ✅ DO:

- Use `pulumi config set --secret` (with `--secret` flag)
- Keep your Pulumi state backup secure
- Use different secrets for different environments (dev/prod)
- Rotate API keys periodically

### ❌ DON'T:

- Hardcode secrets in YAML files
- Commit secrets to Git
- Share your Pulumi state file publicly
- Use the same API keys across multiple systems

## Backup and Recovery

Your secrets are stored in Pulumi state. To backup:

```bash
# Export current stack configuration
pulumi stack export > stack-backup.json

# Store securely (encrypted backup location)
```

To restore on a new machine:

```bash
# Import stack
pulumi stack import < stack-backup.json

# Secrets are restored
pulumi config
```

## Troubleshooting

### Widgets Not Working

1. **Verify secrets are set:**
   ```bash
   pulumi config
   ```

2. **Check API key is valid:**
   - Test the API key directly:
   ```bash
   curl -H "X-Api-Key: your-api-key" http://192.168.1.43/api/v3/system/status
   ```

3. **Check Homepage logs:**
   ```bash
   kubectl logs -n homepage deployment/homepage
   ```

### Secret Not Updating

After changing a secret, you must run `pulumi up` to deploy the changes:

```bash
pulumi config set --secret homepage:sonarr_api_key "new-key"
pulumi up  # This is required!
```

### Lost Secrets

If you lose your Pulumi state or secrets:

1. Retrieve API keys from each service (see "How to Get API Keys" above)
2. Reconfigure them:
   ```bash
   pulumi config set --secret homepage:sonarr_api_key "retrieved-key"
   ```
3. Redeploy:
   ```bash
   pulumi up
   ```

## Example: Complete Setup

Here's a complete example of setting up Homepage secrets:

```bash
#!/bin/bash
# setup-homepage-secrets.sh

cd /Users/pawelrosinski/x/home-automation/infra

# Media services
pulumi config set --secret homepage:jellyseerr_api_key "abc123..."
pulumi config set --secret homepage:bazarr_api_key "def456..."

# Indexers and downloaders
pulumi config set --secret homepage:prowlarr_api_key "ghi789..."
pulumi config set --secret homepage:sonarr_api_key "jkl012..."
pulumi config set --secret homepage:radarr_api_key "mno345..."
pulumi config set --secret homepage:lidarr_api_key "pqr678..."

# qBittorrent
pulumi config set --secret homepage:qbittorrent_username "admin"
pulumi config set --secret homepage:qbittorrent_password "securepassword"

# UniFi (use API key for MFA compatibility)
pulumi config set --secret homepage:unifi_username "admin"
pulumi config set --secret homepage:unifi_api_key "your-unifi-api-key"

# Verify
echo "Configured secrets:"
pulumi config

# Deploy
echo "Deploying Homepage with secrets..."
pulumi up
```

Save this as a script and run it (make sure to replace placeholder values with real ones):

```bash
chmod +x setup-homepage-secrets.sh
./setup-homepage-secrets.sh
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Pulumi Config/Secrets                    │
│  Encrypted storage in Pulumi state                          │
│                                                              │
│  • homepage:sonarr_api_key = [encrypted]                    │
│  • homepage:radarr_api_key = [encrypted]                    │
│  • ... other secrets ...                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ pulumi up (reads secrets)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    homepage.py (Pulumi)                      │
│  1. Reads secrets from config                               │
│  2. Reads services.yaml template                            │
│  3. Substitutes ${VAR} → actual values                      │
│  4. Creates ConfigMap with resolved values                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Creates/Updates
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Kubernetes ConfigMap (homepage)                 │
│  Contains services.yaml with actual API keys                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Mounted as files
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Homepage Container                          │
│  Uses API keys to fetch live data from services             │
└─────────────────────────────────────────────────────────────┘
```

## Migration from Old Setup

If you previously had hardcoded values in YAML:

1. **Extract current values** from `services.yaml`
2. **Set as Pulumi secrets** (commands above)
3. **Update services.yaml** to use `${VAR}` placeholders (already done)
4. **Deploy**: `pulumi up`

The old placeholders `{{HOMEPAGE_VAR_*}}` have been replaced with `${VAR}` format for Pulumi substitution.

## References

- [Pulumi Configuration and Secrets](https://www.pulumi.com/docs/concepts/secrets/)
- [Pulumi Config Command](https://www.pulumi.com/docs/cli/commands/pulumi_config/)
- [Homepage Service Widgets](https://gethomepage.dev/widgets/services/)

