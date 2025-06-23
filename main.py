import logging
from dotenv import load_dotenv
import time
import os

from utils import extract, transform, load

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main_pipeline():
    """Runs the complete ETL pipeline."""
    start_time = time.time()
    logging.info("ETL Pipeline Started.")

    load_dotenv()
    logging.info("Environment variables loaded.")

    logging.info("--- Starting Extraction Phase ---")
    try:
        max_pages = int(os.getenv("MAX_PAGES", 1))
        raw_data_df = extract.extract_data(total_pages=max_pages)
        if raw_data_df.empty:
            logging.error("Extraction resulted in empty data. Stopping pipeline.")
            return
        logging.info(f"Extraction successful. Shape: {raw_data_df.shape}")
    except Exception as e:
        logging.error(f"Extraction failed: {e}")
        return

    logging.info("--- Starting Transformation Phase ---")
    try:
        cleaned_data_df = transform.transform_data(raw_data_df)
        if cleaned_data_df.empty:
             logging.warning("Transformation resulted in empty data after cleaning/dropping. No data to load.")
             return
        logging.info(f"Transformation successful. Shape: {cleaned_data_df.shape}")
    except Exception as e:
        logging.error(f"Transformation failed: {e}")
        return


    logging.info("--- Starting Loading Phase ---")
    load_success_count = 0

    try:
        if load.load_to_csv(cleaned_data_df):
            logging.info("Successfully loaded data to CSV.")
            load_success_count += 1
        else:
             logging.error("Failed to load data to CSV.")
    except Exception as e:
        logging.error(f"Error during CSV loading step: {e}")

    try:
        if load.load_to_google_sheets(cleaned_data_df):
            logging.info("Successfully loaded data to Google Sheets.")
            load_success_count += 1
        else:
            logging.warning("Failed or skipped loading data to Google Sheets.")
    except Exception as e:
        logging.error(f"Error during Google Sheets loading step: {e}")

    try:
        if load.load_to_postgres(cleaned_data_df):
            logging.info("Successfully loaded data to PostgreSQL.")
            load_success_count += 1
        else:
            logging.warning("Failed or skipped loading data to PostgreSQL.")
    except Exception as e:
        logging.error(f"Error during PostgreSQL loading step: {e}")


    if load_success_count > 0:
        logging.info(f"Loading phase completed. Data loaded successfully to {load_success_count} destination(s).")
    else:
        logging.error("Loading phase completed but data failed to load to any destination.")


    end_time = time.time()
    logging.info(f"ETL Pipeline Finished in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main_pipeline()