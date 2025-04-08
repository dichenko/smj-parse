#!/usr/bin/env python
"""
Main script for Smart-J Data Collector.
Provides backward compatibility with both data collection and web interface
functionality, but delegates to specialized scripts.
"""
import argparse
import sys
import logging
from collect_data import collect_data
from run_web import start_web_server


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Smart-J Data Collector")
    parser.add_argument("--collect", action="store_true", help="Collect data from Smart-J website")
    parser.add_argument("--web", action="store_true", help="Run web interface")
    parser.add_argument("--all", action="store_true", help="Collect data and run web interface")
    
    args = parser.parse_args()
    
    if args.collect:
        sys.exit(0 if collect_data() else 1)
    elif args.web:
        start_web_server()
    elif args.all:
        if collect_data():
            start_web_server()
        else:
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
