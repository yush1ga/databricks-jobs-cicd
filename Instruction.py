# Databricks notebook source
dbutils.widgets.text("DEV_JOB_ID", "")
dbutils.widgets.text("PROD_JOB_ID", "")

# COMMAND ----------

# MAGIC %md
# MAGIC # ファイル構成
# MAGIC - job01.py ... タスクその1、標準出力にコマンドライン引数をプリントするだけ
# MAGIC - job02.py ... タスクその2、その1の後続タスク、標準出力にコマンドライン引数をプリントするだけ
# MAGIC - Instruction ... このノートブック
# MAGIC - conf/
# MAGIC   - job_settings.json ... 環境共通の設定ファイル
# MAGIC   - dev_parameters.json ... Dev用の設定 (ジョブパラメータ、gitブランチ) が記載されたファイル
# MAGIC   - prod_parameters.json ... Prod用の設定 (ジョブパラメータ、gitブランチ) が記載されたファイル

# COMMAND ----------

# MAGIC %md
# MAGIC # サンプルジョブのデプロイ
# MAGIC dev と prod にパラメーターだけ変更した同一のジョブをデプロイします。

# COMMAND ----------

# MAGIC %md
# MAGIC ## ワークスペース情報の取得

# COMMAND ----------

API_ROOT = (
    dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiUrl().get()
)
API_TOKEN = (
    dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()
)
WORKSPACE_ROOT = f"https://{dbutils.notebook.entry_point.getDbutils().notebook().getContext().browserHostName().get()}"

# COMMAND ----------

# MAGIC %md
# MAGIC ## デプロイ用の関数を定義する
# MAGIC 実運用時は GitHub Actions などで実行する

# COMMAND ----------

import requests
import json

# API Docs: https://docs.databricks.com/api/workspace/jobs/update
def deploy(job_id, settings_path, parameters_path):
    params = {
        "job_id": job_id,
    }
    with open(settings_path) as f:
        params["new_settings"] = json.load(f)
    with open(parameters_path) as f:
        for k, v in json.load(f).items():
            params["new_settings"][k] = v
    print(requests.post(
        f"{API_ROOT}/api/2.1/jobs/update",
        json=params,
        headers={"Context-Type": "text/json", "Authorization": f"Bearer {API_TOKEN}"},
    ).json())

# COMMAND ----------

# MAGIC %md
# MAGIC ## Dev のジョブをデプロイ
# MAGIC 適当なジョブ (内容は空で良い) を作成し、`DEV_JOB_ID` にIDを入力する。  

# COMMAND ----------

DEV_JOB_ID = dbutils.widgets.get("DEV_JOB_ID")
deploy(DEV_JOB_ID, "./conf/dev_parameters.json", "./conf/job_settings.json")
print(f"Access: {WORKSPACE_ROOT}/jobs/{DEV_JOB_ID}/tasks")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Prod のジョブをデプロイ
# MAGIC 適当なジョブ (内容は空で良い) を作成し、`PROD_JOB_ID` にIDを入力する。  
# MAGIC 実運用では別のワークスペースにデプロイすることが望ましい。

# COMMAND ----------

PROD_JOB_ID =  dbutils.widgets.get("PROD_JOB_ID")
deploy(PROD_JOB_ID, "./conf/prod_parameters.json", "./conf/job_settings.json")
print(f"Access: {WORKSPACE_ROOT}/jobs/{PROD_JOB_ID}/tasks")

# COMMAND ----------

# MAGIC %md
# MAGIC # ジョブの更新手順 (案)
# MAGIC * Devのジョブ、あるいは新たに作ったFeatureのジョブをGUIで編集する
# MAGIC * 実行ボタン左の […] ボタンより JSON を出力
# MAGIC * `settings` の内容をコピー (下記参照)* `dev/prod_parameters.json` に記載の内容 (※) を除いて　`job_settings.json` に貼り付け
# MAGIC   * ※ 本サンプルでは `git_source`, `parameters`
# MAGIC   * 実運用では `job_clusters` 等も対象になると思われる
# MAGIC * (必要なとき) `dev/prod_parameters.json` を更新する
# MAGIC * `deploy` 関数を実行する
# MAGIC
# MAGIC ```json
# MAGIC {
# MAGIC   "job_id": xxxx,
# MAGIC   "creator_user_name": "xxxxx",
# MAGIC   "run_as_user_name": "xxxxx",
# MAGIC   "run_as_owner": true,
# MAGIC   "settings": /*ここから*/{
# MAGIC     ....
# MAGIC   }/*ここまでコピー*/,
# MAGIC   "created_time": 1718293725780
# MAGIC }
# MAGIC ```

# COMMAND ----------


