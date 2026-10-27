
import os
import sys
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.functions import avg, max, min, sum

# Configure Python for Spark
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

# Project paths
PROJECT_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_DIR / "data" / "weather_data.csv"

# Start Spark
spark = (
    SparkSession.builder
    .appName("WeatherDataAnalytics")
    .master("local[*]")
    .config("spark.pyspark.python", sys.executable)
    .getOrCreate()
)

spark.sparkContext.setLogLevel("ERROR")

# Read weather dataset
df = (
    spark.read
    .option("header", True)
    .option("inferSchema", True)
    .csv(str(CSV_PATH))
)

print("\n========== WEATHER DATA ==========")
df.show()

print("\n========== DATASET INFORMATION ==========")
df.printSchema()

print("\n========== CITY-WISE ANALYSIS ==========")

city_summary = (
    df.groupBy("City")
    .agg(
        avg("Temperature").alias("Avg_Temperature"),
        avg("Humidity").alias("Avg_Humidity"),
        sum("Rainfall").alias("Total_Rainfall"),
        max("Temperature").alias("Max_Temperature"),
        min("Temperature").alias("Min_Temperature")
    )
    .orderBy("City")
)

city_summary.show(truncate=False)

print("\n========== OVERALL STATISTICS ==========")
df.select(
    avg("Temperature").alias("Overall_Avg_Temperature"),
    avg("Humidity").alias("Overall_Avg_Humidity"),
    sum("Rainfall").alias("Overall_Total_Rainfall")
).show()

spark.stop()
