import subprocess
import re
import os
from pathlib import Path
import matplotlib.pyplot as plt


class ApacheBenchmark:
    def __init__(self, url: str, post_data_file: Path | str = None):
        self.url = url
        self.post_data_file = post_data_file

    @staticmethod
    def parse_output(output: str) -> float:
        pattern = r"Time per request:.*?(\d+\.\d+)"
        result = re.search(pattern, output)
        if result:
            time_per_request = float(result.group(1))
            return time_per_request
        else:
            raise Exception(
                f"Benchmark failed. Time per request not found. Output: {output}"
            )

    def run(
        self, concurrency: int, number_of_requests: int = 1000, timeout: int = 20
    ) -> float:
        """
        Returns time per request in ms
        """
        command = f"ab -n {number_of_requests} -c {concurrency} -s {timeout}"

        if self.post_data_file:
            command += f" -p {self.post_data_file} -T application/json"

        command += f" {self.url}"
        command = list(command.split(" "))
        output = subprocess.check_output(command, text=False).decode("utf-8")
        time_per_request = self.parse_output(output)
        return time_per_request


def benchmark_make_reservation():
    benchmark = ApacheBenchmark(
        url="http://127.0.0.1:8000/make-reservation/2",
        post_data_file="data/reservation.json",
    )
    concurrency_values = [1, 5, 10, 25, 50, 100, 150]
    time_per_request_output_list = []

    for concurrency in concurrency_values:
        os.system(
            "docker exec -i pupilove_percona_mysql "
            "mysql -upupilove_admin -p12345 "
            '-e "DELETE FROM pupilove.reservations;" '
            "> /dev/null 2>&1"
        )
        print(
            f"Started benchmark: Make reservation endpoint. Concurrency: {concurrency}."
        )
        time_per_request_output_list.append(benchmark.run(concurrency=concurrency))
    return concurrency_values, time_per_request_output_list


def benchmark_search_listings():
    benchmark = ApacheBenchmark(
        url="http://127.0.0.1:8000/search-listings",
        post_data_file="data/search.json",
    )
    concurrency_values = [1, 5, 10, 25, 50, 100, 150]
    time_per_request_output_list = []

    for concurrency in concurrency_values:
        print(
            f"Started benchmark: Search listings endpoint. Concurrency: {concurrency}."
        )
        time_per_request_output_list.append(benchmark.run(concurrency=concurrency))
    return concurrency_values, time_per_request_output_list


def create_chart(
    x: list,
    y: list,
    title: str,
    xlabel: str = "Number of multiple requests made at a time",
    ylabel: str = "Time per request [ms]",
):
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, marker="o", linestyle="-", color="b")
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.xticks(x)
    plt.tight_layout()

    filename = title.lower().replace(" ", "_") + ".png"
    plt.savefig(filename)
    print(f"Chart saved as {filename}")

    plt.close()


if __name__ == "__main__":
    x_mr, y_mr = benchmark_make_reservation()
    x_sl, y_sl = benchmark_search_listings()

    create_chart(x_mr, y_mr, title="Make reservation endpoint benchmark")
    create_chart(x_sl, y_sl, title="Search listings endpoint benchmark")
