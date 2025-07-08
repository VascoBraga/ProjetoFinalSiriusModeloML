"""
Arquivo de configuração para o sistema de classificação de viabilidade jurídica.
"""

# Configurações gerais
RANDOM_STATE = 42
TEST_SIZE = 0.3

# Colunas principais do dataset
COLUNAS_VALOR_CAUSA = [
    'ValorCausa',
    'ValorCausaMinimo', 
    'ValorCausaMaximo',
    'ValorCausaCategoria',
    'ValorCausaDescricao',
    'ValorCausaFonte',
    'ValorCausaConfianca',
    'ValorCausaMetodo'
]

# Colunas para remover na preparação para ML
COLUNAS_REMOVER_ML = [
    'DescricaoAssunto', 'DescricaoProblema', 'DataAbertura', 'DataArquivamento',
    'RazaoSocial', 'NomeFantasia', 'ValorCausaDescricao', 'ValorCausaFonte',
    'ValorCausaMetodo', 'Viavel_Label', 'Viabilidade_Detalhada'
]

# Colunas problemáticas para balanceamento
COLUNAS_PROBLEMATICAS = ['DataAbertura', 'DataArquivamento', 'NumeroCNPJ']

# Configurações de TF-IDF
MAX_FEATURES_TFIDF = 100
MIN_DF = 5
MAX_DF = 0.8

# Stopwords em português
STOPWORDS_PORTUGUES = [
    'de', 'da', 'do', 'dos', 'das', 'e', 'o', 'a', 'os', 'as', 'em', 'na', 'no',
    'nas', 'nos', 'por', 'para', 'com', 'sem', 'um', 'uma', 'uns', 'umas',
    'que', 'se', 'não', 'mais', 'como', 'sobre', 'entre', 'até', 'após',
    'ser', 'ter', 'estar', 'fazer', 'dizer', 'ir', 'ver', 'dar', 'saber',
    'muito', 'bem', 'onde', 'quando', 'porque', 'ainda', 'também', 'só',
    'já', 'mesmo', 'sempre', 'nunca', 'vez', 'vezes', 'cada', 'todo',
    'toda', 'todos', 'todas', 'outro', 'outra', 'outros', 'outras'
]

# Dicionário jurídico
PALAVRAS_JURIDICAS = {
    'alta_viabilidade': [
        'dano moral', 'constrangimento', 'humilhação', 'exposição', 'vexame',
        'cobrança indevida', 'serviço não prestado', 'produto defeituoso',
        'propaganda enganosa', 'venda casada', 'cláusula abusiva',
        'descumprimento', 'negativa', 'recusa', 'cancelamento unilateral',
        'interrupção', 'suspensão', 'bloqueio', 'corte'
    ],
    'gravidade_alta': [
        'emergência', 'urgente', 'grave', 'risco', 'perigo', 'saúde',
        'vida', 'segurança', 'acidente', 'lesão', 'prejuízo',
        'discriminação', 'preconceito', 'assédio'
    ],
    'complexidade_alta': [
        'contrato', 'financiamento', 'empréstimo', 'seguro', 'plano',
        'multiple', 'recorrente', 'sistemático', 'repetitivo',
        'judicial', 'extrajudicial', 'acordo', 'indenização'
    ],
    'baixa_viabilidade': [
        'informação', 'esclarecimento', 'dúvida', 'orientação',
        'consulta', 'pergunta', 'sugestão', 'reclamação simples'
    ],
    'setores_viaveis': [
        'banco', 'cartão', 'financeira', 'seguro', 'plano de saúde',
        'telefonia', 'internet', 'energia elétrica', 'companhia aérea'
    ],
    'jurisprudencia_consolidada': [
        'anuidade', 'tarifa', 'juros', 'multa', 'vencimento',
        'atraso', 'cancelamento', 'negativação', 'spc', 'serasa'
    ]
}