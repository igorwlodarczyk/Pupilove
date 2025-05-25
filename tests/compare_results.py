import csv
import sys
import matplotlib.pyplot as plt
from collections import defaultdict


def load_csv_data(filepath):
    data = defaultdict(list)
    with open(filepath, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            test_name = row["Test Name"]
            concurrency = int(row["Concurrency"])
            time_per_request = float(row["Time Per Request (ms)"])
            data[test_name].append((concurrency, time_per_request))
    return data


def plot_comparison(data1, data2, label1, label2):
    all_tests = set(data1.keys()) | set(data2.keys())

    for test_name in all_tests:
        plt.figure(figsize=(10, 6))

        if test_name in data1:
            x1, y1 = zip(*sorted(data1[test_name]))
            plt.plot(x1, y1, marker="o", linestyle="-", label=label1)

        if test_name in data2:
            x2, y2 = zip(*sorted(data2[test_name]))
            plt.plot(x2, y2, marker="s", linestyle="--", label=label2)

        plt.title(f"Benchmark Comparison: {test_name}")
        plt.xlabel("Concurrency")
        plt.ylabel("Time per Request (ms)")
        plt.grid(True)
        plt.legend()
        plt.xticks(
            sorted(
                set(x1 if test_name in data1 else [])
                | set(x2 if test_name in data2 else [])
            )
        )
        plt.tight_layout()

        filename = f"{test_name.lower().replace(' ', '_')}_comparison.png"
        plt.savefig(filename)
        print(f"Saved comparison chart as {filename}")
        plt.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compare_benchmarks.py <file1.csv> <file2.csv>")
        sys.exit(1)

    file1, file2 = sys.argv[1], sys.argv[2]
    data1 = load_csv_data(file1)
    data2 = load_csv_data(file2)

    label1 = file1.split("/")[-1]
    label2 = file2.split("/")[-1]

    plot_comparison(data1, data2, label1, label2)
