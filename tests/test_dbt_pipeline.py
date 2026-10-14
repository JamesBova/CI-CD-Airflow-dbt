from pathlib import Path

from airflow.models import DagBag


DAG_FOLDER = Path("/opt/airflow/dags")

dag_bag = DagBag(
    dag_folder=str(DAG_FOLDER),
)


def test_no_import_errors():
    assert dag_bag.import_errors == {}


def test_dag_loaded():
    dag = dag_bag.get_dag("dbt_ci_cd_pipeline")
    assert dag is not None


def test_task_count():
    dag = dag_bag.get_dag("dbt_ci_cd_pipeline")
    assert len(dag.tasks) == 3


def test_task_dependencies():
    dag = dag_bag.get_dag("dbt_ci_cd_pipeline")

    assert dag.get_task("dbt_debug").downstream_task_ids == {"dbt_test"}
    assert dag.get_task("dbt_test").downstream_task_ids == {"dbt_run"}
    assert dag.get_task("dbt_run").downstream_task_ids == set()