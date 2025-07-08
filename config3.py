"""
Configurações e constantes para o algoritmo de classificação SINDEC
"""

# Features proibidas (usadas para criar o target - causam data leakage)
FEATURES_PROIBIDAS = [
    # Scores usados para criar target
    'Score_Valor', 'Score_Sucesso', 'Score_Potencial',
    'Score_Confianca', 'Score_Volume', 'Score_Total',
    
    # Variáveis target e derivadas
    'Viavel', 'Viavel_Label', 'Viabilidade_Detalhada',
    
    # Features que "entregam" o target
    'Taxa_Sucesso', 'Potencial_Financeiro', 'Quantidade',
    
    # Texto original (processar de forma independente)
    'DescricaoAssunto', 'DescricaoProblema',
    
    # Outras variáveis problemáticas
    'DataArquivamento', 'DataAbertura'  # Vazamento temporal
]

# Features permitidas - apenas dados primários
FEATURES_PERMITIDAS = [
    # Informações básicas (disponíveis no momento da decisão)
    'AnoCalendario', 'CodigoRegiao', 'UF', 'Regiao',
    
    # Informações da empresa (disponíveis publicamente)
    'Tipo', 'CNAEPrincipal',
    
    # Informações do consumidor
    'SexoConsumidor', 'FaixaEtariaConsumidor',
    
    # Valor estimado (nossa estimativa, não o resultado)
    'ValorCausa', 'ValorCausaConfianca',
    
    # Códigos de classificação
    'CodigoAssunto', 'CodigoProblema'
]

# Features numéricas relevantes para balanceamento
NUMERIC_FEATURES = [
    'ValorCausa', 'ValorCausaConfianca', 'Taxa_Sucesso', 'Potencial_Financeiro',
    'Score_Valor', 'Score_Sucesso', 'Score_Potencial', 'Score_Confianca',
    'Score_Volume', 'Score_Total', 'AnoCalendario'
]

# Estratégias de balanceamento disponíveis
BALANCING_STRATEGIES = [
    'random_oversample',
    'smote',
    'borderline_smote',
    'smote_tomek',
    'hybrid_custom'
]

# Mapeamento de faixa etária
FAIXA_ETARIA_MAP = {
    'até 20 anos': 1,
    'entre 21 a 30 anos': 2,
    'entre 31 a 40 anos': 3,
    'entre 41 a 50 anos': 4,
    'entre 51 a 60 anos': 5,
    'entre 61 a 70 anos': 6,
    'mais de 70 anos': 7
}

# Configurações padrão
DEFAULT_CONFIG = {
    'random_state': 42,
    'test_size': 0.3,
    'n_estimators': 100,
    'max_iter': 1000,
    'top_ufs': 10,
    'top_assuntos': 20,
    'variance_threshold': 0.01
}