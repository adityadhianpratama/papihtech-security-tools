
import ipaddress
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from threading import Event, Lock

from colorama import init, Fore, Style

init(autoreset=True)

# ==========================================
# PAPiH TECH - CONTROLLED HTTP SIMULATOR
# ==========================================

TARGET_IP = "192.168.64.3"
PORT = 80

DURATION = 30
WORKERS = 2
INTERVAL = 1.0

stop_event = Event()
stats_lock = Lock()

stats = {
    "success": 0,
    "failed": 0,
}


def banner():
    print(Fore.CYAN + Style.BRIGHT + "=" * 44)
    print(Fore.WHITE + Style.BRIGHT +
          "       PAPiH TECH | LAB SIMULATOR")
    print(Fore.CYAN + Style.BRIGHT + "=" * 44)

    print(f"{Fore.WHITE}Target   : "
          f"{Fore.YELLOW}{TARGET_IP}:{PORT}")
    print(f"{Fore.WHITE}Duration : "
          f"{Fore.YELLOW}{DURATION} seconds")
    print(f"{Fore.WHITE}Workers  : "
          f"{Fore.YELLOW}{WORKERS}")
    print(Fore.CYAN + "-" * 44)
    print(Fore.GREEN + "[INFO] Starting controlled HTTP test...\n")


def send_request():
    url = f"http://{TARGET_IP}:{PORT}/"

    while not stop_event.is_set():
        start = time.perf_counter()

        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "PapihTech-Lab/1.0"},
            )

            with urllib.request.urlopen(
                request, timeout=3
            ) as response:
                response.read(256)
                elapsed = (time.perf_counter() - start) * 1000

                with stats_lock:
                    stats["success"] += 1

                print(
                    f"{Fore.GREEN}[OK]{Style.RESET_ALL} "
                    f"{Fore.CYAN}HTTP {response.status}"
                    f"{Style.RESET_ALL} | "
                    f"{Fore.YELLOW}{elapsed:.0f} ms"
                )

        except Exception as exc:
            with stats_lock:
                stats["failed"] += 1

            print(
                f"{Fore.RED}[ERROR]{Style.RESET_ALL} "
                f"{Fore.WHITE}{type(exc).__name__}: {exc}"
            )

        stop_event.wait(INTERVAL)


def main():
    try:
        ip = ipaddress.ip_address(TARGET_IP)

        if ip.version != 4 or not ip.is_private:
            raise ValueError(
                "Target harus berupa IP private IPv4."
            )

        banner()
        start = time.monotonic()

        with ThreadPoolExecutor(
            max_workers=WORKERS
        ) as executor:
            futures = [
                executor.submit(send_request)
                for _ in range(WORKERS)
            ]

            try:
                time.sleep(DURATION)
            except KeyboardInterrupt:
                print(
                    f"\n{Fore.YELLOW}[INFO] "
                    "Stopping simulation..."
                )
            finally:
                stop_event.set()

        elapsed = time.monotonic() - start

        print("\n" + Fore.CYAN + "=" * 44)
        print(
            Fore.WHITE + Style.BRIGHT +
            "             LAB SUMMARY"
        )
        print(Fore.CYAN + "=" * 44)

        print(
            f"{Fore.GREEN}Successful requests : "
            f"{stats['success']}"
        )
        print(
            f"{Fore.RED}Failed requests     : "
            f"{stats['failed']}"
        )
        print(
            f"{Fore.YELLOW}Elapsed             : "
            f"{elapsed:.1f}s"
        )

        print(Fore.CYAN + "=" * 44)
        print(
            Fore.GREEN + "[INFO] Simulation finished."
        )

    except ValueError as exc:
        print(f"{Fore.RED}[CONFIG ERROR] {exc}")


if __name__ == "__main__":
    main()
