"""
Configurações e constantes do sistema
"""

# Configurações do modelo
MODEL_FILE = 'modelo_viabilidade_final.pkl'

# Mapeamentos de dados
UF_OPTIONS = {
    "Sudeste": ["SP", "RJ", "MG", "ES"],
    "Sul": ["RS", "SC", "PR"],
    "Centro-oeste": ["GO", "MT", "MS", "DF"],
    "Nordeste": ["BA", "PE", "CE", "MA", "PB", "RN", "AL", "SE", "PI"],
    "Norte": ["PA", "AM", "RO", "AC", "RR", "AP", "TO"]
}

FAIXA_ETARIA_MAP = {
    "Até 20 anos": 1,
    "21 a 30 anos": 2,
    "31 a 40 anos": 3,
    "41 a 50 anos": 4,
    "51 a 60 anos": 5,
    "61 a 70 anos": 6,
    "Mais de 70 anos": 7
}

ASSUNTO_MAPPING = {
    'Telefonia/Internet': [1, 2, 3],
    'Bancos/Financeiro': [4, 5, 6],
    'Energia Elétrica': [7],
    'Comércio/Produto': [8, 9, 10],
    'Plano de Saúde': [11],
    'Transporte Aéreo': [12],
    'Outros': [99]
}

# Opções de interface
TIPOS_ASSUNTO = [
    "Telefonia/Internet", "Bancos/Financeiro", "Energia Elétrica",
    "Comércio/Produto", "Plano de Saúde", "Transporte Aéreo", "Outros"
]

PROBLEMAS_PRINCIPAIS = [
    "Cobrança Indevida", "Produto Defeituoso", "Serviço Não Prestado",
    "Dano Moral", "Negativação Indevida", "Cancelamento Unilateral", "Outros"
]

REGIOES = ["Sudeste", "Sul", "Centro-oeste", "Nordeste", "Norte"]

SEXOS = ["M", "F"]

ANOS_DISPONIVEIS = [2024, 2023, 2022, 2021, 2020]

# Faixas de valor para classificação
VALOR_BAIXO_MAX = 2000
VALOR_MEDIO_MAX = 4000

# Configurações de interface
APP_TITLE = "⚖️ Analisador de Viabilidade Jurídica"
APP_ICON = "⚖️"
LAYOUT = "wide"
SIDEBAR_STATE = "expanded"