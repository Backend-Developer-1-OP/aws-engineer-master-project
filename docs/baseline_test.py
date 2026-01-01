import requests
import threading
import time
import statistics
import os

# ---------- Config ----------
ALB_URL = "http://app-alb-1292617256.eu-west-3.elb.amazonaws.com/items?count=10"
DURATION = 10 * 60  # steady test: 10 min
SPIKE_DURATION = 60  # spike test: 1 min
VUS_STEADY = 10
VUS_SPIKE = 50
REPORT_PATH = "docs/baseline_performance_report.md"

os.makedirs("docs", exist_ok=True)

# ---------- Load test function ----------
def run_load_test(duration, vus, test_name):
    print(f"Starting {test_name} ({vus} VUs for {duration} sec)...")
    results = []

    def worker():
        end_time = time.time() + duration
        while time.time() < end_time:
            start = time.time()
            try:
                r = requests.get(ALB_URL, timeout=5)
                latency = (time.time() - start) * 1000
                results.append((latency, r.status_code))
            except Exception:
                results.append((None, "error"))

    threads = [threading.Thread(target=worker) for _ in range(vus)]
    for t in threads: t.start()
    for t in threads: t.join()

    latencies = [r[0] for r in results if r[0] is not None]
    errors = sum(1 for r in results if r[1] != 200)
    total = len(results)
    error_rate = errors / total * 100 if total else 0
    p50 = statistics.median(latencies) if latencies else None
    p95 = statistics.quantiles(latencies, n=100)[94] if latencies else None

    print(f"{test_name} complete: {total} requests, {errors} errors, p50={p50:.2f}ms, p95={p95:.2f}ms")
    return {"total_requests": total, "errors": errors, "error_rate": error_rate, "p50": p50, "p95": p95}

# ---------- Run tests ----------
steady_results = run_load_test(DURATION, VUS_STEADY, "Steady Test")
spike_results = run_load_test(SPIKE_DURATION, VUS_SPIKE, "Spike Test")

# ---------- Write report ----------
with open(REPORT_PATH, "w") as f:
    f.write("# Baseline Performance Report\n\n")
    f.write("## Test Config\n")
    f.write(f"- ALB URL: {ALB_URL}\n")
    f.write(f"- Steady Test: {VUS_STEADY} VUs for {DURATION/60:.0f} min\n")
    f.write(f"- Spike Test: {VUS_SPIKE} VUs for {SPIKE_DURATION} sec\n\n")

    f.write("## Steady Test Results\n")
    f.write(f"- Total Requests: {steady_results['total_requests']}\n")
    f.write(f"- Errors: {steady_results['errors']}\n")
    f.write(f"- Error Rate: {steady_results['error_rate']:.2f}%\n")
    f.write(f"- p50 Latency: {steady_results['p50']:.2f} ms\n")
    f.write(f"- p95 Latency: {steady_results['p95']:.2f} ms\n\n")

    f.write("## Spike Test Results\n")
    f.write(f"- Total Requests: {spike_results['total_requests']}\n")
    f.write(f"- Errors: {spike_results['errors']}\n")
    f.write(f"- Error Rate: {spike_results['error_rate']:.2f}%\n")
    f.write(f"- p50 Latency: {spike_results['p50']:.2f} ms\n")
    f.write(f"- p95 Latency: {spike_results['p95']:.2f} ms\n\n")

    f.write("## Notes\n")
    f.write("- Attach CloudWatch screenshots manually for ASG behavior.\n")

print(f"Report saved: {REPORT_PATH}")
