"""
Módulo para análise exploratória dos dados de viabilidade de causas.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuração para visualizações
plt.style.use('default')
sns.set_palette("husl")


class ViabilidadeCausasAnalyzer:
    """
    Analisador de viabilidade de causas para escritórios de advocacia
    Etapa 1: Análise exploratória e definição do problema
    """

    def __init__(self, df_sindec_com_valores):
        self.df = df_sindec_com_valores.copy()
        self.criterios_viabilidade = {}

    def definir_problema(self):
        """
        Define claramente o problema de machine learning
        """
        print("=" * 80)
        print("🎯 DEFINIÇÃO DO PROBLEMA DE MACHINE LEARNING")
        print("=" * 80)

        problema = """
        📋 PROBLEMA: Classificação de Viabilidade de Causas

        🎯 OBJETIVO:
        Criar um modelo que, dado DescricaoAssunto e DescricaoProblema de uma nova causa,
        classifique se ela é VIÁVEL ou NÃO VIÁVEL financeiramente para o escritório.

        📊 INPUTS (Features):
        - DescricaoAssunto (texto)
        - DescricaoProblema (texto)
        - Possivelmente: UF, Regiao, FaixaEtariaConsumidor, etc.

        🎯 OUTPUT (Target):
        - VIÁVEL: Vale a pena aceitar a causa
        - NÃO VIÁVEL: Não vale a pena aceitar a causa

        💡 CRITÉRIOS DE VIABILIDADE (a serem definidos):
        - Valor da causa (ValorCausa)
        - Taxa de sucesso histórica (Atendida = 'S')
        - Complexidade da causa
        - Tempo de resolução
        - Região/UF (alguns locais podem ser mais favoráveis)

        📈 TIPO: Problema de Classificação Binária
        📚 ALGORITMOS: Random Forest, XGBoost, SVM, Neural Networks
        """

        print(problema)
        return problema

    def análise_exploratória_básica(self):
        """
        Realiza análise exploratória dos dados
        """
        print("\n" + "=" * 80)
        print("📊 ANÁLISE EXPLORATÓRIA DOS DADOS")
        print("=" * 80)

        # Informações básicas
        print(f"📋 INFORMAÇÕES BÁSICAS:")
        print(f"Total de registros: {len(self.df):,}")
        print(f"Total de colunas: {self.df.shape[1]}")
        print(f"Período: {self.df['AnoCalendario'].unique()}")

        # Campos principais
        print(f"\n🔍 CAMPOS PRINCIPAIS:")
        print(f"Assuntos únicos: {self.df['DescricaoAssunto'].nunique()}")
        print(f"Problemas únicos: {self.df['DescricaoProblema'].nunique()}")
        print(f"UFs: {self.df['UF'].nunique()}")
        print(f"Regiões: {self.df['Regiao'].nunique()}")

        # Distribuição da variável "Atendida" (proxy para sucesso)
        print(f"\n📈 DISTRIBUIÇÃO DE ATENDIMENTO:")
        atendidas = self.df['Atendida'].value_counts()
        print(atendidas)
        print(f"Taxa de sucesso: {atendidas.get('S', 0) / len(self.df) * 100:.1f}%")

        # Estatísticas dos valores
        print(f"\n💰 ESTATÍSTICAS DOS VALORES:")
        valores_stats = self.df['ValorCausa'].describe()
        print(valores_stats)

        return {
            'total_registros': len(self.df),
            'assuntos_unicos': self.df['DescricaoAssunto'].nunique(),
            'problemas_unicos': self.df['DescricaoProblema'].nunique(),
            'taxa_sucesso': atendidas.get('S', 0) / len(self.df),
            'valor_medio': self.df['ValorCausa'].mean(),
            'valor_mediano': self.df['ValorCausa'].median()
        }

    def analisar_padrões_por_assunto(self, top_n=15):
        """
        Analisa padrões por tipo de assunto
        """
        print("\n" + "=" * 80)
        print("🔍 ANÁLISE POR TIPO DE ASSUNTO")
        print("=" * 80)

        # Agrupamento por assunto
        analise_assunto = self.df.groupby('DescricaoAssunto').agg({
            'ValorCausa': ['count', 'mean', 'median'],
            'Atendida': lambda x: (x == 'S').sum(),  # Casos resolvidos
            'ValorCausaConfianca': 'mean'
        }).round(2)

        # Flatten column names
        analise_assunto.columns = ['Quantidade', 'Valor_Medio', 'Valor_Mediano',
                                  'Casos_Resolvidos', 'Confianca_Media']

        # Calcula taxa de sucesso
        analise_assunto['Taxa_Sucesso'] = (
            analise_assunto['Casos_Resolvidos'] / analise_assunto['Quantidade'] * 100
        ).round(1)

        # Calcula potencial financeiro (valor médio * taxa sucesso)
        analise_assunto['Potencial_Financeiro'] = (
            analise_assunto['Valor_Medio'] * analise_assunto['Taxa_Sucesso'] / 100
        ).round(2)

        # Filtra apenas assuntos com volume razoável
        analise_assunto = analise_assunto[analise_assunto['Quantidade'] >= 10]

        # Ordena por potencial financeiro
        analise_assunto = analise_assunto.sort_values('Potencial_Financeiro', ascending=False)

        print(f"🏆 TOP {top_n} ASSUNTOS POR POTENCIAL FINANCEIRO:")
        print("-" * 120)

        for i, (assunto, dados) in enumerate(analise_assunto.head(top_n).iterrows(), 1):
            print(f"\n{i:2d}. {assunto[:60]}...")
            print(f"    📊 Quantidade: {dados['Quantidade']:,}")
            print(f"    💰 Valor médio: R$ {dados['Valor_Medio']:,.2f}")
            print(f"    ✅ Taxa sucesso: {dados['Taxa_Sucesso']:.1f}%")
            print(f"    🎯 Potencial: R$ {dados['Potencial_Financeiro']:,.2f}")
            print(f"    🔒 Confiança: {dados['Confianca_Media']:.2f}")

        return analise_assunto

    def analisar_padrões_por_problema(self, top_n=15):
        """
        Analisa padrões por tipo de problema
        """
        print("\n" + "=" * 80)
        print("🔍 ANÁLISE POR TIPO DE PROBLEMA")
        print("=" * 80)

        # Agrupamento por problema
        analise_problema = self.df.groupby('DescricaoProblema').agg({
            'ValorCausa': ['count', 'mean', 'median'],
            'Atendida': lambda x: (x == 'S').sum(),
            'ValorCausaConfianca': 'mean'
        }).round(2)

        analise_problema.columns = ['Quantidade', 'Valor_Medio', 'Valor_Mediano',
                                   'Casos_Resolvidos', 'Confianca_Media']

        analise_problema['Taxa_Sucesso'] = (
            analise_problema['Casos_Resolvidos'] / analise_problema['Quantidade'] * 100
        ).round(1)

        analise_problema['Potencial_Financeiro'] = (
            analise_problema['Valor_Medio'] * analise_problema['Taxa_Sucesso'] / 100
        ).round(2)

        # Filtra problemas com volume razoável
        analise_problema = analise_problema[analise_problema['Quantidade'] >= 5]
        analise_problema = analise_problema.sort_values('Potencial_Financeiro', ascending=False)

        print(f"🏆 TOP {top_n} PROBLEMAS POR POTENCIAL FINANCEIRO:")
        print("-" * 120)

        for i, (problema, dados) in enumerate(analise_problema.head(top_n).iterrows(), 1):
            print(f"\n{i:2d}. {problema[:70]}...")
            print(f"    📊 Quantidade: {dados['Quantidade']:,}")
            print(f"    💰 Valor médio: R$ {dados['Valor_Medio']:,.2f}")
            print(f"    ✅ Taxa sucesso: {dados['Taxa_Sucesso']:.1f}%")
            print(f"    🎯 Potencial: R$ {dados['Potencial_Financeiro']:,.2f}")

        return analise_problema

    def analisar_distribuições(self):
        """
        Analisa distribuições das variáveis principais
        """
        print("\n" + "=" * 80)
        print("📈 ANÁLISE DE DISTRIBUIÇÕES")
        print("=" * 80)

        # Distribuição de valores
        print("💰 DISTRIBUIÇÃO DOS VALORES DE CAUSA:")
        quartis = self.df['ValorCausa'].quantile([0.25, 0.5, 0.75, 0.9, 0.95, 0.99])
        print(f"Q1 (25%): R$ {quartis[0.25]:,.2f}")
        print(f"Mediana (50%): R$ {quartis[0.5]:,.2f}")
        print(f"Q3 (75%): R$ {quartis[0.75]:,.2f}")
        print(f"P90: R$ {quartis[0.9]:,.2f}")
        print(f"P95: R$ {quartis[0.95]:,.2f}")
        print(f"P99: R$ {quartis[0.99]:,.2f}")

        # Faixas de valor
        faixas_valor = pd.cut(self.df['ValorCausa'],
                             bins=[0, 1000, 3000, 5000, 10000, 20000, float('inf')],
                             labels=['Até R$ 1k', 'R$ 1k-3k', 'R$ 3k-5k',
                                   'R$ 5k-10k', 'R$ 10k-20k', 'Acima R$ 20k'])

        print(f"\n📊 DISTRIBUIÇÃO POR FAIXAS DE VALOR:")
        distribuicao_faixas = faixas_valor.value_counts().sort_index()
        for faixa, count in distribuicao_faixas.items():
            print(f"{faixa}: {count:,} ({count/len(self.df)*100:.1f}%)")

        # Distribuição regional
        print(f"\n🗺️ DISTRIBUIÇÃO POR REGIÃO:")
        dist_regional = self.df['Regiao'].value_counts()
        for regiao, count in dist_regional.items():
            print(f"{regiao}: {count:,} ({count/len(self.df)*100:.1f}%)")

        return {
            'quartis_valor': quartis,
            'distribuicao_faixas': distribuicao_faixas,
            'distribuicao_regional': dist_regional
        }

    def identificar_insights_preliminares(self):
        """
        Identifica insights preliminares para orientar a criação do target
        """
        print("\n" + "=" * 80)
        print("💡 INSIGHTS PRELIMINARES PARA CRIAÇÃO DO TARGET")
        print("=" * 80)

        insights = []

        # 1. Correlação valor vs taxa de sucesso
        analise_valor_sucesso = self.df.groupby(
            pd.cut(self.df['ValorCausa'], bins=10)
        )['Atendida'].apply(lambda x: (x == 'S').mean()).round(3)

        print("1️⃣ CORRELAÇÃO VALOR vs TAXA DE SUCESSO:")
        for faixa, taxa in analise_valor_sucesso.items():
            print(f"   {faixa}: {taxa:.1%}")

        # 2. Regiões mais promissoras
        sucesso_por_regiao = self.df.groupby('Regiao').agg({
            'Atendida': lambda x: (x == 'S').mean(),
            'ValorCausa': 'mean'
        }).round(2)

        print(f"\n2️⃣ PERFORMANCE POR REGIÃO:")
        for regiao, dados in sucesso_por_regiao.iterrows():
            print(f"   {regiao}: {dados['Atendida']:.1%} sucesso, R$ {dados['ValorCausa']:,.2f} médio")

        # 3. Identificar limites para classificação
        valor_medio = self.df['ValorCausa'].mean()
        taxa_sucesso_media = (self.df['Atendida'] == 'S').mean()

        print(f"\n3️⃣ MÉTRICAS DE REFERÊNCIA:")
        print(f"   Valor médio: R$ {valor_medio:,.2f}")
        print(f"   Taxa sucesso média: {taxa_sucesso_media:.1%}")

        # 4. Proposta inicial de critérios
        print(f"\n4️⃣ PROPOSTA INICIAL DE CRITÉRIOS DE VIABILIDADE:")
        print(f"   🎯 VIÁVEL se:")
        print(f"     - Valor > R$ {valor_medio*0.8:,.2f} (80% da média) E")
        print(f"     - Taxa sucesso do assunto > {taxa_sucesso_media*0.9:.1%} (90% da média)")
        print(f"   ❌ NÃO VIÁVEL caso contrário")

        insights.append({
            'valor_referencia': valor_medio * 0.8,
            'taxa_referencia': taxa_sucesso_media * 0.9,
            'valor_medio_geral': valor_medio,
            'taxa_media_geral': taxa_sucesso_media
        })

        return insights

    def executar_analise_completa(self):
        """
        Executa a análise exploratória completa
        """
        print("🚀 INICIANDO ANÁLISE EXPLORATÓRIA COMPLETA...")

        # 1. Definir problema
        self.definir_problema()

        # 2. Análise básica
        stats_basicas = self.análise_exploratória_básica()

        # 3. Análise por assunto
        analise_assuntos = self.analisar_padrões_por_assunto()

        # 4. Análise por problema
        analise_problemas = self.analisar_padrões_por_problema()

        # 5. Distribuições
        distribuicoes = self.analisar_distribuições()

        # 6. Insights
        insights = self.identificar_insights_preliminares()

        print("\n" + "=" * 80)
        print("✅ ANÁLISE EXPLORATÓRIA CONCLUÍDA!")
        print("=" * 80)

        print("🎯 PRÓXIMOS PASSOS:")
        print("1. Criar variável target (viabilidade) baseada nos insights")
        print("2. Preparar features (text processing, encoding)")
        print("3. Dividir dados em treino/teste")
        print("4. Treinar modelos de classificação")
        print("5. Avaliar performance e calibrar")

        return {
            'stats_basicas': stats_basicas,
            'analise_assuntos': analise_assuntos,
            'analise_problemas': analise_problemas,
            'distribuicoes': distribuicoes,
            'insights': insights
        }


def executar_etapa_1(df_sindec_com_valores):
    """
    Executa a Etapa 1 da análise
    """
    print("🎯 EXECUTANDO ETAPA 1: ANÁLISE EXPLORATÓRIA")
    print("=" * 80)

    # Inicializa analisador
    analyzer = ViabilidadeCausasAnalyzer(df_sindec_com_valores)

    # Executa análise completa
    resultados = analyzer.executar_analise_completa()

    return analyzer, resultados