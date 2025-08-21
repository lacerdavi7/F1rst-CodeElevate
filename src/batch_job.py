import os
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StringType, FloatType, TimestampType
from pyspark.sql.functions import to_date
import functions

PG_USER = "sparkuser"
PG_PWD = "sparkpass"
PG_URL = "jdbc:postgresql://postgres:5432/sparkdb"
PG_TABLE = "info_corridas_do_dia"


jdbc_props = {
    "driver": "org.postgresql.Driver",
    "user": "sparkuser",
    "password": "sparkpass",
    "stringtype": "unspecified" 
}


INPUT_PATH = os.getenv("INPUT_PATH", "/data/info_transportes.csv")

schema = StructType() \
    .add("data_inicio", StringType()) \
    .add("data_fim", StringType())\
    .add("categoria", StringType())\
    .add("local_incio", StringType())\
    .add("local_fim", StringType())\
    .add("distancia",FloatType())\
    .add("proposito", StringType())

if __name__ == "__main__":
    spark = (SparkSession.builder
             .appName("CSVToPostgresBatch")
             .getOrCreate())

    df = (spark.read
            .options(delimiter=";", header=True, timestampFormat="MM-dd-yyyy HH:mm")
            .schema(schema)
            .csv(INPUT_PATH))
    
    # dd-MM-yyyy
    # Ajusta campos para dd-MM-yyyy    
    df = functions.convert_to_date(df, 'data_inicio', 'dt_refe')
    df = functions.remove_accents(df, 'categoria', 'trat_categoria')
    df = functions.remove_accents(df, 'proposito', 'trat_proposito')
    df.createOrReplaceTempView('corridas')
    

    agg_df = spark.sql(f"""
                       SELECT DT_REFE
                        ,COUNT(*) AS QT_CORR
                        ,SUM(CASE WHEN trat_categoria = "NEGOCIO" THEN 1 ELSE 0 END) AS QT_CORR_NEG
                        ,SUM(CASE WHEN trat_categoria = "PESSOAL" THEN 1 ELSE 0 END) AS QT_CORR_PESS
                        ,ROUND(MAX(DISTANCIA),2) AS VL_MAX_DIST
                        ,ROUND(MIN(DISTANCIA),2) AS VL_MIN_DIST
                        ,ROUND(AVG(DISTANCIA),2) AS VL_AVG_DIST
                        ,SUM(CASE WHEN trat_proposito = "REUNICAO" THEN 1 ELSE 0 END) AS QT_CORR_REUNI
                        ,SUM(CASE WHEN trat_proposito != "REUNICAO" THEN 1 ELSE 0 END) AS QT_CORR_NAO_REUNI
                        FROM corridas GROUP BY DT_REFE
                       """)
                       
    agg_df.printSchema()
   
    (agg_df.write
       .format("jdbc")
       .option("url", PG_URL)
       .option("dbtable", PG_TABLE)
       .option("user", PG_USER)
       .option("password", PG_PWD)
       .option("driver", "org.postgresql.Driver")
       .mode("overwrite")
       .save())

    spark.stop()
