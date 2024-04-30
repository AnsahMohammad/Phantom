import argparse
import time
from phantom_engine import Phantom

def main(num_threads, urls, show_logs, print_logs, sleep):
    print("Starting Phantom engine")
    print("num_threads: ", num_threads)
    print("urls: ", urls)
    print("show_logs: ", show_logs)
    print("print_logs: ", print_logs)
    print("sleep: ", sleep)
    phantom = Phantom(num_threads=num_threads, urls=urls, show_logs=show_logs, print_logs=print_logs, burnout=sleep)
    phantom.run()
    if sleep is not None:
        time.sleep(sleep)
    phantom.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the Phantom engine.')
    parser.add_argument('--num_threads', type=int, default=8, help='Number of threads.')
    parser.add_argument('--urls', type=str, nargs='+', help='List of URLs.')
    parser.add_argument('--show_logs', type=bool, default=True, help='Whether to show logs.')
    parser.add_argument('--print_logs', type=bool, default=True, help='Whether to print logs.')
    parser.add_argument('--sleep', type=int, default=300, help='Sleep time in seconds.')

    args = parser.parse_args()

    main(args.num_threads, args.urls, args.show_logs, args.print_logs, args.sleep)