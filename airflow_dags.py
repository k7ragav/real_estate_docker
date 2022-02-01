from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from pendulum import timezone

default_args = {
    "owner": "real_estate_docker",
    "depends_on_past": False,
    "email": ["k7ragav@gmail.com"],
    "email_on_failure": True,
    "email_on_success": True,
    "retries": 1,
    "retry_delay": timedelta(minutes=15),
    "catchup": True,
}
intervals = {
    "daily_at_8am": "0 8 */1 * *",
    "daily_at_7am": "0 7 */1 * *",
    "every_3_days": "0 0 */3 * *",
    "every_hour": "0 */1 * * *",
}
bash_command = "docker exec real_estate_docker python {{ task.task_id }}.py "

with DAG(
        "pararius",
        description="pararius apeldoorn",
        default_args=default_args,
        schedule_interval=intervals["every_hour"],
        start_date=datetime(2022, 1, 9, tzinfo=timezone("Europe/Amsterdam")),
) as pararius_dag:
    pararius_task = BashOperator(
        task_id="pararius",
        bash_command=bash_command,
    )

with DAG(
        "funda_apeldoorn",
        description="funda apeldoorn",
        default_args=default_args,
        schedule_interval=intervals["every_hour"],
        start_date=datetime(2022, 2, 1, tzinfo=timezone("Europe/Amsterdam")),
) as funda_apeldoorn_dag:
    funda_apeldoorn_task = BashOperator(
        task_id="funda_apeldoorn",
        bash_command=bash_command,
    )