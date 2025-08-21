from pyspark.sql import SparkSession
from pyspark.sql.functions import to_date, col, date_format
from pyspark.sql.types import StringType
from pyspark.sql import functions as F

def convert_to_date(df, input_col, output_col="converted_date"):
    """
    Converte coluna string no formato 'MM-dd-yyyy HH:mm' para 'yyyy-MM-dd'.
    
    Args:
        df (DataFrame): DataFrame de entrada.
        input_col (str): Nome da coluna string.
        output_col (date): Nome da nova coluna com data convertida.
    
    Returns:
        DataFrame: com nova coluna de data formatada.
    """
    return df.withColumn(output_col,F.regexp_replace(F.col(input_col), r" (\d):", r" 0\1:"))\
         .withColumn(output_col,F.date_format(F.to_timestamp(output_col, "MM-dd-yyyy HH:mm"),"yyyy-MM-dd"))\
         .withColumn(output_col,F.to_date(output_col))


def remove_accents(df, column_name, new_column_name="cleaned"):
    """
    Remove acentos e caracteres especiais de uma coluna string
    e converte para maiúsculo usando translate.
    
    Exemplo:
    Entrada: "Alimentação" -> Saída: "ALIMENTACAO"
    """
    accents = "ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇáàâãäéèêëíìîïóòôõöúùûüç"
    replacements = "AAAAAEEEEIIIIOOOOOUUUUCaaaaaeeeeiiiiooooouuuuc"
    
    return df.withColumn(
        new_column_name,
        F.upper(F.translate(F.col(column_name), accents, replacements))
    )
 