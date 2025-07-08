"""
Sistema de Classificação de Viabilidade de Causas Jurídicas

Este pacote implementa um pipeline completo de machine learning para classificar
a viabilidade financeira de causas jurídicas baseado em dados do SINDEC.

Módulos principais:
- data_preprocessing: Limpeza e preprocessamento dos dados
- exploratory_analysis: Análise exploratória dos dados
- target_creation: Criação da variável target de viabilidade
- feature_engineering: Engenharia de features para ML
- data_balancing: Balanceamento de classes
- utils: Funções utilitárias
- main: Pipeline principal de execução

Exemplo de uso:
    python main.py dados_sindec.csv --strategy moderate
"""

__version__ = "1.0.0"
__author__ = "Sistema de Classificação de Viabilidade Jurídica"
__description__ = "ML Pipeline para classificação de viabilidade de causas jurídicas"

# Imports principais para facilitar o uso
from .main import ViabilidadeClassificationPipeline
from .data_preprocessing import preprocessar_dados
from .exploratory_analysis import ViabilidadeCausasAnalyzer, executar_etapa_1
from .target_creation import TargetCreator, executar_etapa_2
from .feature_engineering import ViabilidadeFeatureEngineer, executar_feature_engineering
from .data_balancing import DataBalancer, balancear_dados_viabilidade
from .utils import debug_dataframe, verificar_colunas_necessarias, plotar_distribuicao_target

__all__ = [
    # Classes principais
    'ViabilidadeClassificationPipeline',
    'ViabilidadeCausasAnalyzer',
    'TargetCreator', 
    'ViabilidadeFeatureEngineer',
    'DataBalancer',
    
    # Funções principais
    'preprocessar_dados',
    'executar_etapa_1',
    'executar_etapa_2', 
    'executar_feature_engineering',
    'balancear_dados_viabilidade',
    
    # Utilitários
    'debug_dataframe',
    'verificar_colunas_necessarias',
    'plotar_distribuicao_target'
]