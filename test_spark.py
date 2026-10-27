import os
import sys

os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("WeatherBigDataProject")
    .master("local[*]")
    .getOrCreate()
)

data = [
    ("Mumbai", 32, 78),
    ("Pune", 29, 65),
    ("Delhi", 35, 55),
    ("Chennai", 33, 80),
]

columns = ["City", "Temperature", "Humidity"]

df = spark.createDataFrame(data, columns)

print("WEATHER BIG DATA ANALYTICS")
df.show()

print("Average Temperature:")
df.selectExpr("avg(Temperature) as Average_Temperature").show()

spark.stop()
