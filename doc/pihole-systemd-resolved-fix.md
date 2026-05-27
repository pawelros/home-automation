# Pi-hole Post-Upgrade System Issues Fix Guide

## Issues
After upgrading Pi-hole, you may encounter:

1. **systemd-resolved.service** fails with:
   - `Failed to set up mount namespacing: /run/systemd/unit-root/proc: Permission denied`
   - Exit code 226/NAMESPACE

2. **NTP client** fails with:
   - `Failed to adjust time during NTP sync: Insufficient permissions`

## Impact
- This may affect DNS resolution on the Pi-hole host
- External-DNS should still work if Pi-hole web interface is accessible
- Pi-hole DNS functionality may be unaffected (uses dnsmasq, not systemd-resolved)

## Troubleshooting Steps

### Step 1: Check Pi-hole Status
SSH into your Pi-hole server (192.168.1.3) and check:

```bash
# Check if Pi-hole is running
sudo systemctl status pihole-FTL

# Check if Pi-hole web interface is accessible
curl -I http://localhost/admin

# Check DNS functionality
dig @127.0.0.1 google.com
```

### Step 2: Check systemd-resolved Status
```bash
# Check current status
sudo systemctl status systemd-resolved

# Check if it's actually needed (Pi-hole uses dnsmasq, not systemd-resolved)
systemctl is-enabled systemd-resolved
```

### Step 3: Fix Options

#### Option A: Disable systemd-resolved (Recommended for Pi-hole)
Since Pi-hole uses dnsmasq for DNS, systemd-resolved is typically not needed:

```bash
# Stop and disable systemd-resolved
sudo systemctl stop systemd-resolved
sudo systemctl disable systemd-resolved

# Verify it's disabled
systemctl is-enabled systemd-resolved  # Should show "disabled"
```

#### Option B: Fix systemd-resolved Permissions
If you need systemd-resolved for other services:

```bash
# Check /proc mount
mount | grep proc

# Check AppArmor status
sudo aa-status | grep systemd-resolved

# Reset systemd-resolved state
sudo systemctl reset-failed systemd-resolved
sudo rm -rf /run/systemd/unit-root
sudo systemctl daemon-reload
sudo systemctl restart systemd-resolved
```

#### Option C: Reinstall systemd-resolved
```bash
# Reinstall systemd (includes systemd-resolved)
sudo apt-get update
sudo apt-get install --reinstall systemd systemd-sysv
sudo systemctl daemon-reexec
sudo systemctl restart systemd-resolved
```

### Step 4: Verify External-DNS Still Works
From your Kubernetes cluster:

```bash
# Check external-dns logs
kubectl logs -n external-dns deployment/external-dns --tail=50

# Test DNS resolution for a service
nslookup prowlarr.local 192.168.1.3
```

### Step 5: Check Network Configuration
If systemd-resolved was managing DNS, ensure `/etc/resolv.conf` points to Pi-hole:

```bash
# On Pi-hole server, check resolv.conf
cat /etc/resolv.conf

# Should point to Pi-hole (127.0.0.1) or your router
# If systemd-resolved was managing it, you may need to:
sudo rm /etc/resolv.conf
sudo ln -s /run/systemd/resolve/resolv.conf /etc/resolv.conf
# OR manually set:
echo "nameserver 127.0.0.1" | sudo tee /etc/resolv.conf
```

## Recommended Solution
For a Pi-hole server, **Option A (disable systemd-resolved)** is recommended because:
- Pi-hole uses dnsmasq for DNS resolution
- systemd-resolved is redundant and can cause conflicts
- Simplifies DNS configuration

## Verification
After applying the fix:

1. **Pi-hole web interface**: http://192.168.1.3/admin should be accessible
2. **External-DNS**: Check logs for successful DNS record updates
3. **DNS resolution**: Test from a client device using Pi-hole as DNS server

## NTP Client Permission Fix

### Issue
NTP client fails with "Insufficient permissions" when trying to adjust system time.

### Solution

#### Step 1: Check NTP Service Status
```bash
# Check which NTP service is running
sudo systemctl status systemd-timesyncd
# OR
sudo systemctl status chronyd
```

#### Step 2: Fix systemd-timesyncd (Most Common)
If using `systemd-timesyncd`:

```bash
# Check current status
sudo systemctl status systemd-timesyncd

# Check if it has proper capabilities
systemctl show systemd-timesyncd | grep CapabilityBoundingSet

# Restart the service
sudo systemctl restart systemd-timesyncd

# Check logs for errors
sudo journalctl -u systemd-timesyncd -n 50
```

If restart doesn't work, check system capabilities:

```bash
# Verify systemd-timesyncd has CAP_SYS_TIME capability
systemctl show systemd-timesyncd | grep CapabilityBoundingSet
# Should include: CAP_SYS_TIME

# If missing, check the service file
cat /lib/systemd/system/systemd-timesyncd.service | grep CapabilityBoundingSet
```

#### Step 3: Alternative - Use chronyd
If `systemd-timesyncd` continues to have issues, switch to `chronyd`:

```bash
# Stop systemd-timesyncd
sudo systemctl stop systemd-timesyncd
sudo systemctl disable systemd-timesyncd

# Install chronyd (if not already installed)
sudo apt-get update
sudo apt-get install chrony

# Start and enable chronyd
sudo systemctl start chronyd
sudo systemctl enable chronyd

# Check status
sudo systemctl status chronyd
chronyc tracking  # Check sync status
```

#### Step 4: Verify Time Sync
```bash
# Check current time
date

# Check NTP sync status
timedatectl status

# Force sync (if using systemd-timesyncd)
sudo systemd-timesyncd --synchronize

# Or if using chronyd
sudo chronyd -q
```

#### Step 5: Check System Clock Permissions
If still having issues, verify the system allows time adjustments:

```bash
# Check if system is in sync mode
timedatectl set-ntp true

# Check current NTP status
timedatectl status

# If running in a container or restricted environment, you may need:
# For systemd-timesyncd: Ensure it has CAP_SYS_TIME in capabilities
# For chronyd: Ensure it's running with proper permissions
```

### Common Causes
1. **Missing capabilities**: Service lacks `CAP_SYS_TIME` capability
2. **Container restrictions**: Running in Docker/LXC without time sync permissions
3. **AppArmor/SELinux**: Security policies blocking time adjustments
4. **System clock too far off**: Large time drift requires manual adjustment first

### Manual Time Adjustment (if needed)
If the clock is too far off, adjust manually first:

```bash
# Check current time offset
sudo chronyd tracking  # If using chronyd
# OR
sudo systemd-timesyncd --synchronize  # If using systemd-timesyncd

# If time is way off, set it manually (use UTC)
sudo timedatectl set-time "2026-01-05 18:00:00"

# Then enable NTP sync
sudo timedatectl set-ntp true
```

## Additional Notes
- These errors don't necessarily break Pi-hole functionality
- The errors are in system services, not Pi-hole itself
- If Pi-hole is working, you can safely disable unused services
- Time sync is important for DNS TTL accuracy and log timestamps

