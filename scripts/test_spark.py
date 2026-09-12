from pyspark.sql import SparkSession

# Crear una sesión local de Spark
spark = SparkSession.builder \
    .appName("PruebaInicial") \
    .getOrCreate()

# Crear un DataFrame simple de prueba
datos = [("Irais", 1), ("Spark", 2), ("Ubuntu", 3)]
df = spark.createDataFrame(datos, ["Nombre", "ID"])

print("\n--- RESULTADO DE PRUEBA PYSPARK ---")
df.show()

spark.stop()