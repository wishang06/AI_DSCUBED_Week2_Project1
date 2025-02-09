import openai
import time
import psutil
import os
from memory_profiler import profile


def get_process_memory():
    """Get current process memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


@profile
def create_multiple_clients(n=100):
    """Create multiple OpenAI clients"""
    clients = []
    start_mem = get_process_memory()
    start_time = time.time()

    for _ in range(n):
        client = openai.OpenAI(api_key="dummy-key")
        clients.append(client)

    end_time = time.time()
    end_mem = get_process_memory()

    return {
        "time_taken": end_time - start_time,
        "memory_per_client": (end_mem - start_mem) / n,
        "total_memory": end_mem - start_mem
    }


@profile
def reuse_single_client(n=100):
    """Simulate reusing a single client for multiple operations"""
    start_mem = get_process_memory()
    start_time = time.time()

    client = openai.OpenAI(api_key="dummy-key")
    # Simulate n operations using the same client
    for _ in range(n):
        _ = client.base_url  # Simple property access to simulate usage

    end_time = time.time()
    end_mem = get_process_memory()

    return {
        "time_taken": end_time - start_time,
        "memory_total": end_mem - start_mem
    }


# Run benchmarks
multi_client_results = create_multiple_clients(100)
single_client_results = reuse_single_client(100)

print("Multiple Clients Benchmark:")
print(f"Time taken: {multi_client_results['time_taken']:.4f} seconds")
print(f"Memory per client: {multi_client_results['memory_per_client']:.2f} MB")
print(f"Total memory: {multi_client_results['total_memory']:.2f} MB")

print("\nSingle Client Benchmark:")
print(f"Time taken: {single_client_results['time_taken']:.4f} seconds")
print(f"Total memory: {single_client_results['memory_total']:.2f} MB")
