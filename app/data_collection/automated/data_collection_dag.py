from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Define default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    'data_collection_pipeline',
    default_args=default_args,
    description='Data collection automation pipeline',
    schedule_interval='0 0 * * *',  # Run daily at midnight
    catchup=False,
    tags=['data_collection']
)

def extract_data(**context):
    """
    Extract data from source systems
    """
    try:
        logger.info("Starting data extraction process")
        # Add your data extraction logic here
        # Example:
        # data = source_system.get_data()
        # context['task_instance'].xcom_push(key='raw_data', value=data)
        logger.info("Data extraction completed successfully")
    except Exception as e:
        logger.error(f"Error in data extraction: {str(e)}")
        raise

def transform_data(**context):
    """
    Transform the extracted data
    """
    try:
        logger.info("Starting data transformation process")
        # Add your data transformation logic here
        # Example:
        # raw_data = context['task_instance'].xcom_pull(key='raw_data', task_ids='extract_data')
        # transformed_data = process_data(raw_data)
        # context['task_instance'].xcom_push(key='transformed_data', value=transformed_data)
        logger.info("Data transformation completed successfully")
    except Exception as e:
        logger.error(f"Error in data transformation: {str(e)}")
        raise

def load_data(**context):
    """
    Load transformed data to destination
    """
    try:
        logger.info("Starting data loading process")
        # Add your data loading logic here
        # Example:
        # transformed_data = context['task_instance'].xcom_pull(key='transformed_data', task_ids='transform_data')
        # destination_system.load_data(transformed_data)
        logger.info("Data loading completed successfully")
    except Exception as e:
        logger.error(f"Error in data loading: {str(e)}")
        raise

# Create task instances
extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    provide_context=True,
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    provide_context=True,
    dag=dag
)

load_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    provide_context=True,
    dag=dag
)

# Set task dependencies
extract_task >> transform_task >> load_task