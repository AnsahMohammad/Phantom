import argparse
import time
from phantom_engine import Phantom

def main(num_threads, urls, show_logs, print_logs):
    phantom = Phantom(num_threads=num_threads, urls=urls, show_logs=show_logs, print_logs=print_logs)
    phantom.run()
    time.sleep(30)
    phantom.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the Phantom engine.')
    parser.add_argument('--num_threads', type=int, default=8, help='Number of threads.')
    parser.add_argument('--urls', type=str, nargs='+', help='List of URLs.')
    parser.add_argument('--show_logs', type=bool, default=True, help='Whether to show logs.')
    parser.add_argument('--print_logs', type=bool, default=True, help='Whether to print logs.')

    args = parser.parse_args()

    main(args.num_threads, args.urls, args.show_logs, args.print_logs)