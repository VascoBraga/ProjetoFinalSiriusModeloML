"""
Configurações do sistema de análise de viabilidade jurídica
"""

# API DataJud
DATAJUD_BASE_URL = "https://api-publica.datajud.cnj.jus.br"
DATAJUD_DEFAULT_TRIBUNAL = "tjsp"

# Configurações de processamento
DEFAULT_BATCH_SIZE = 1000
MAX_ASSUNTOS_ENRIQUECIMENTO = 15
PROCESSOS_POR_TERMO = 50

# Arquivos de saída
OUTPUT_FILE_COMPLETO = "SINDEC_com_valores_causa.csv"
OUTPUT_FILE_RESUMO = "SINDEC_resumo_por_assunto.csv"

# Encoding
FILE_ENCODING_INPUT = "windows-1252"
FILE_ENCODING_OUTPUT = "utf-8"

# Separadores CSV
CSV_SEPARATOR_INPUT = ";"
CSV_SEPARATOR_OUTPUT = ","