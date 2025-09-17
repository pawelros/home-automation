# Kubernetes Monitoring with Grafana K8s Monitoring Helm Chart

This component replaces the individual monitoring components (Promtail) with the comprehensive [Grafana Kubernetes Monitoring Helm chart](https://grafana.com/docs/grafana-cloud/monitor-infrastructure/kubernetes-monitoring/configuration/helm-chart-config/helm-chart/).

## Features

The Kubernetes Monitoring Helm chart provides:

### 📊 **Metrics Collection**
- **Node Exporter**: Hardware and OS metrics from Kubernetes nodes
- **kube-state-metrics**: Kubernetes object state metrics
- **cAdvisor**: Container resource usage and performance metrics
- **Kubelet**: Kubernetes node and pod metrics
- **API Server**: Kubernetes API server metrics
- **OpenCost**: Cost monitoring for Kubernetes workloads

### 📝 **Logs Collection**
- **Pod Logs**: Automatic collection from all pods across all namespaces
- **Cluster Events**: Kubernetes event logs
- **Rich Labeling**: Automatic enrichment with namespace, pod, container, node labels

### 🔄 **Integration**
- **Grafana Alloy**: Modern telemetry collector (replaces Promtail)
- **Multiple Instances**: Separate collectors for different data types (logs, metrics, traces)
- **ServiceMonitor**: Automatic Prometheus-compatible service discovery

## Configuration

### External Services

The chart is configured to send data to your existing services:

```python
"externalServices": {
    "loki": {
        "host": "http://loki-gateway.loki.svc.cluster.local/loki/api/v1/push",
    },
    "prometheus": {
        "host": "http://mimir-nginx.mimir.svc.cluster.local/prometheus",
    },
}
```

### Enabled Components

- ✅ **Metrics**: Node Exporter, kube-state-metrics, cAdvisor, Kubelet, API Server
- ✅ **Logs**: Pod logs, cluster events
- ✅ **Cost Monitoring**: OpenCost integration
- ❌ **Traces**: Disabled (can be enabled later)
- ❌ **Profiles**: Disabled (can be enabled later)

## Benefits over Individual Components

### 🚀 **Simplified Management**
- Single Helm chart instead of multiple components
- Unified configuration and lifecycle management
- Consistent labeling and metadata across all telemetry

### 📈 **Enhanced Features**
- Better resource utilization with purpose-built Alloy instances
- Advanced log processing and enrichment
- Built-in cost monitoring with OpenCost
- Automatic service discovery

### 🔧 **Scalability**
- DaemonSet for logs (one per node)
- StatefulSet for metrics (scalable)
- Singleton for cluster-wide metrics

### 🏷️ **Rich Metadata**
Automatic labeling includes:
- `cluster`: Cluster identifier
- `namespace`: Kubernetes namespace
- `pod`: Pod name
- `container`: Container name
- `node`: Node name
- `job`: Job/workload type

## Migration from Individual Components

This replaces:
- ❌ `promtail.promtail.Promtail` → ✅ K8s Monitoring (Alloy-based log collection)
- ➕ Adds comprehensive metrics collection
- ➕ Adds cost monitoring
- ➕ Adds cluster event collection

Your existing Loki and Mimir deployments remain unchanged and will receive data from the new monitoring stack.

## Deployment

The component is deployed in the `monitoring` namespace and includes:

1. **Alloy Operator**: Manages Alloy collector instances
2. **Alloy Instances**: 
   - `alloy-logs`: DaemonSet for log collection
   - `alloy-metrics`: StatefulSet for metrics collection
   - `alloy-singleton`: Deployment for cluster-wide metrics
3. **Supporting Components**:
   - Node Exporter (DaemonSet)
   - kube-state-metrics (Deployment)
   - OpenCost (Deployment)

## Next Steps

After deployment, you can:

1. **Import Kubernetes Dashboards**: Use Grafana's built-in Kubernetes dashboards
2. **Enable Traces**: Add trace collection if needed
3. **Enable Profiles**: Add continuous profiling if needed
4. **Customize Collection**: Fine-tune which logs and metrics to collect
5. **Add Alerting**: Configure alerts based on the collected metrics

## References

- [Grafana Kubernetes Monitoring Documentation](https://grafana.com/docs/grafana-cloud/monitor-infrastructure/kubernetes-monitoring/configuration/helm-chart-config/helm-chart/)
- [Grafana k8s-monitoring Helm Chart Repository](https://github.com/grafana/k8s-monitoring-helm)
- [Grafana Alloy Documentation](https://grafana.com/docs/alloy/latest/)
