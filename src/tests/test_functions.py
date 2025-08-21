import pytest
from pyspark.sql import SparkSession
from src.functions import convert_to_date, remove_accents


@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local[1]").appName("PytestSpark").getOrCreate()


def test_convert_to_date(spark):
    data = [("01-30-2016 21:11",), ("01-15-2016 0:41",)]
    df = spark.createDataFrame(data, ["raw_date"])

    result = convert_to_date(df, "raw_date", "converted").collect()

    assert str(result[0]["converted"]) == "2016-01-30"
    assert str(result[1]["converted"]) == "2016-01-15"


def test_remove_accents(spark):
    data = [("Reunião",), ("Alimentação",), ("ação",)]
    df = spark.createDataFrame(data, ["raw_text"])

    result = remove_accents(df, "raw_text", "cleaned").collect()

    expected = ["REUNIAO", "ALIMENTACAO", "ACAO"]
    assert [row["cleaned"] for row in result] == expected
