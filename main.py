"""
Main script for Smart-J Data Collector.
"""
import argparse
import logging
from src.utils.logger import setup_logging
from src.database.schema import create_database
from src.parsers.auth import login
from src.parsers.lesson_parser import collect_all_data
from src.database.operations import save_lessons_to_db
from src.web.app import run_web_interface

def collect_data():
    """Collect data from Smart-J website."""
    logger = setup_logging(level=logging.DEBUG)
    logger.info("Starting data collection...")
    
    # Create database schema
    create_database()
    
    # Login to website
    session = login()
    if not session:
        logger.error("Failed to login. Exiting.")
        return False
    
    # Collect data from all modules
    all_lessons_data = collect_all_data(session)
    
    # Save data to database
    if all_lessons_data:
        new_lessons, existing_lessons = save_lessons_to_db(all_lessons_data)
        logger.info(f"Data collection complete. Added {new_lessons} new lessons, {existing_lessons} already existed.")
        return True
    else:
        logger.error("No data collected.")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Smart-J Data Collector")
    parser.add_argument("--collect", action="store_true", help="Collect data from Smart-J website")
    parser.add_argument("--web", action="store_true", help="Run web interface")
    parser.add_argument("--all", action="store_true", help="Collect data and run web interface")
    
    args = parser.parse_args()
    
    if args.collect:
        collect_data()
    elif args.web:
        run_web_interface()
    elif args.all:
        if collect_data():
            run_web_interface()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
