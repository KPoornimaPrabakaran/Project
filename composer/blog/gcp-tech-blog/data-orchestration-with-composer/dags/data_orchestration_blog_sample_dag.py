# Copyright 2021 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from airflow import models

from airflow.hooks.base import BaseHook
from airflow.providers.google.cloud.operators.bigquery import BigQueryCheckOperator
from airflow.providers.google.cloud.operators.dataflow import DataflowTemplatedJobStartOperator
from airflow.providers.google.cloud.sensors.gcs import GCSObjectExistenceSensor
from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator

from airflow.utils.dates import days_ago
from airflow.utils.state import State

# Sample data
BUCKET_NAME = "gs://cloud-samples-data/composer/data-orchestration-blog-example"
DATA_FILE_NAME = "bike_station_data.csv"

# Assumes existence of the following Airflow Variables
PROJECT_ID = models.Variable.get("gcp_project")
DATASET = models.Variable.get("bigquery_dataset")
TABLE = models.Variable.get("bigquery_table")


# Slack error notification example taken from Kaxil Naik's blog on Slack Integration:
# https://medium.com/datareply/integrating-slack-alerts-in-airflow-c9dcd155105
def on_failure_callback(context):
    ti = context.get("task_instance")
    slack_msg = """
            :red_circle: Task Failed.
            *Task*: {task}
            *Dag*: {dag}
            *Execution Time*: {exec_date}
            *Log Url*: {log_url}
            """.format(
        task=ti.task_id,
        dag=ti.dag_id,
        log_url=ti.log_url,
        exec_date=context.get("execution_date"),
    )
    slack_webhook_token = BaseHook.get_connection("slack_connection").password
    slack_error = SlackWebhookOperator(
        task_id="post_slack_error",
        http_conn_id="slack_connection",
        channel="#airflow-alerts",
        webhook_token=slack_webhook_token,
        message=slack_msg,
    )
    slack_error.execute(context)


with models.DAG(
    "dataflow_to_bq_workflow",
    schedule_interval=None,
    start_date=days_ago(1),
    default_args={"on_failure_callback": on_failure_callback},
) as dag:

    validate_file_exists = GCSObjectExistenceSensor(
        task_id="validate_file_exists", bucket=BUCKET_NAME, object=DATA_FILE_NAME
    )

    # See Launching Dataflow pipelines with Cloud Composer tutorial for further guidance
    # https://cloud.google.com/composer/docs/how-to/using/using-dataflow-template-operator
    start_dataflow_job = DataflowTemplatedJobStartOperator(
        task_id="start-dataflow-template-job",
        job_name="csv_to_bq_transform",
        template="gs://dataflow-templates/latest/GCS_Text_to_BigQuery",
        parameters={
            "javascriptTextTransformFunctionName": "transform",
            "javascriptTextTransformGcsPath": "gs://{bucket}/udf_transform.js".format(
                bucket=BUCKET_NAME
            ),
            "JSONPath": "gs://{bucket}/bq_schema.json".format(bucket=BUCKET_NAME),
            "inputFilePattern": "gs://{bucket}/{filename}".format(
                bucket=BUCKET_NAME, filename=DATA_FILE_NAME
            ),
            "bigQueryLoadingTemporaryDirectory": "gs://{bucket}/tmp/".format(
                bucket=BUCKET_NAME
            ),
            "outputTable": "{project_id}:{dataset}.{table}".format(
                project_id=PROJECT_ID, dataset=DATASET, table=TABLE
            ),
        },
    )

    execute_bigquery_sql = BigQueryCheckOperator(
        task_id="execute_bigquery_sql",
        sql="SELECT COUNT(*) FROM `{project_id}.{dataset}.{table}`".format(
            project_id=PROJECT_ID, dataset=DATASET, table=TABLE
        ),
        use_legacy_sql=False,
    )

    validate_file_exists >> start_dataflow_job >> execute_bigquery_sql


if __name__ == "__main__":
    dag.clear(dag_run_state=State.NONE)
    dag.run()
