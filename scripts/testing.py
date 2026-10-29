from databricks.connect import DatabricksSession

spark = DatabricksSession.builder.serverless().getOrCreate()

print(spark.range(5).collect())

spark.stop()