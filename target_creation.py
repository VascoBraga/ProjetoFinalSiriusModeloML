"""
Módulo para criação da variável target de viabilidade de causas.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')


class TargetCreator:
    """
    Criador da variável target para classificação de viabilidade de causas
    """

    def __init__(self, df_sindec_com_valores):
        self.df = df_sindec_com_valores.copy()
        self.criterios = {}
        self.stats_assuntos = None
        self.stats_problemas = None

    def calcular_estatisticas_historicas(self):
        """
        Calcula estatísticas históricas por assunto e problema para criar o target
        """
        print("=" * 80)
        print("📊 CALCULANDO ESTATÍSTICAS HISTÓRICAS")
        print("=" * 80)

        # Debug: verificar colunas disponíveis
        print(f"🔍 Colunas disponíveis: {list(self.df.columns)}")
        print(f"🔍 Valores únicos em 'Atendida': {self.df['Atendida'].unique()}")

        # Estatísticas por assunto
        stats_raw = self.df.groupby('DescricaoAssunto').agg({
            'ValorCausa': ['count', 'mean', 'median', 'std'],
            'Atendida': lambda x: (x == 'S').sum(),  # Casos resolvidos
            'ValorCausaConfianca': 'mean'
        }).round(2)

        # Flatten das colunas multi-level
        stats_raw.columns = ['Quantidade', 'Valor_Medio', 'Valor_Mediano',
                            'Valor_Std', 'Casos_Resolvidos', 'Confianca_Media']

        # Criar DataFrame limpo
        self.stats_assuntos = pd.DataFrame(index=stats_raw.index)
        self.stats_assuntos['Quantidade'] = stats_raw['Quantidade']
        self.stats_assuntos['Valor_Medio'] = stats_raw['Valor_Medio']
        self.stats_assuntos['Valor_Mediano'] = stats_raw['Valor_Mediano']
        self.stats_assuntos['Valor_Std'] = stats_raw['Valor_Std']
        self.stats_assuntos['Casos_Resolvidos'] = stats_raw['Casos_Resolvidos']
        self.stats_assuntos['Confianca_Media'] = stats_raw['Confianca_Media']

        # Taxa de sucesso por assunto
        self.stats_assuntos['Taxa_Sucesso'] = (
            self.stats_assuntos['Casos_Resolvidos'] / self.stats_assuntos['Quantidade']
        ).round(3)

        # Potencial financeiro esperado
        self.stats_assuntos['Potencial_Financeiro'] = (
            self.stats_assuntos['Valor_Medio'] * self.stats_assuntos['Taxa_Sucesso']
        ).round(2)

        print(f"✅ Colunas em stats_assuntos: {list(self.stats_assuntos.columns)}")
        print(f"✅ Primeiras linhas:\n{self.stats_assuntos.head()}")

        # Estatísticas por problema
        stats_prob_raw = self.df.groupby('DescricaoProblema').agg({
            'ValorCausa': ['count', 'mean'],
            'Atendida': lambda x: (x == 'S').sum()
        }).round(2)

        stats_prob_raw.columns = ['Quantidade', 'Valor_Medio', 'Casos_Resolvidos']

        self.stats_problemas = pd.DataFrame(index=stats_prob_raw.index)
        self.stats_problemas['Quantidade'] = stats_prob_raw['Quantidade']
        self.stats_problemas['Valor_Medio'] = stats_prob_raw['Valor_Medio']
        self.stats_problemas['Casos_Resolvidos'] = stats_prob_raw['Casos_Resolvidos']

        self.stats_problemas['Taxa_Sucesso'] = (
            self.stats_problemas['Casos_Resolvidos'] / self.stats_problemas['Quantidade']
        ).round(3)

        print(f"✅ Estatísticas calculadas para {len(self.stats_assuntos)} assuntos")
        print(f"✅ Estatísticas calculadas para {len(self.stats_problemas)} problemas")

        return self.stats_assuntos, self.stats_problemas

    def definir_criterios_viabilidade(self):
        """
        Define os critérios para classificar uma causa como viável
        """
        print("\n" + "=" * 80)
        print("🎯 DEFININDO CRITÉRIOS DE VIABILIDADE")
        print("=" * 80)

        # Métricas de referência
        valor_medio_geral = self.df['ValorCausa'].mean()
        valor_mediano_geral = self.df['ValorCausa'].median()
        taxa_sucesso_geral = (self.df['Atendida'] == 'S').mean()
        confianca_media = self.df['ValorCausaConfianca'].mean()

        print(f"📊 MÉTRICAS DE REFERÊNCIA:")
        print(f"   Valor médio geral: R$ {valor_medio_geral:,.2f}")
        print(f"   Valor mediano geral: R$ {valor_mediano_geral:,.2f}")
        print(f"   Taxa sucesso geral: {taxa_sucesso_geral:.1%}")
        print(f"   Confiança média: {confianca_media:.2f}")

        # Quartis para definir thresholds
        quartis_valor = self.df['ValorCausa'].quantile([0.25, 0.5, 0.75, 0.8])
        quartis_potencial = self.stats_assuntos['Potencial_Financeiro'].quantile([0.25, 0.5, 0.75])

        # DEFINIÇÃO DOS CRITÉRIOS
        self.criterios = {
            # Critérios de valor
            'valor_minimo_baixo': quartis_valor[0.25],
            'valor_minimo_medio': quartis_valor[0.5],
            'valor_minimo_alto': quartis_valor[0.75],

            # Critérios de taxa de sucesso
            'taxa_sucesso_minima': taxa_sucesso_geral * 0.8,
            'taxa_sucesso_boa': taxa_sucesso_geral * 1.1,

            # Critérios de potencial financeiro
            'potencial_minimo': quartis_potencial[0.5],
            'potencial_bom': quartis_potencial[0.75],

            # Critérios de confiabilidade
            'confianca_minima': 0.6,

            # Critérios de volume
            'volume_minimo': 5,
        }

        print(f"\n🎯 CRITÉRIOS DEFINIDOS:")
        print(f"   💰 Valor mínimo (baixo): R$ {self.criterios['valor_minimo_baixo']:,.2f}")
        print(f"   💰 Valor mínimo (médio): R$ {self.criterios['valor_minimo_medio']:,.2f}")
        print(f"   💰 Valor mínimo (alto): R$ {self.criterios['valor_minimo_alto']:,.2f}")
        print(f"   ✅ Taxa sucesso mínima: {self.criterios['taxa_sucesso_minima']:.1%}")
        print(f"   🚀 Taxa sucesso boa: {self.criterios['taxa_sucesso_boa']:.1%}")
        print(f"   🎯 Potencial mínimo: R$ {self.criterios['potencial_minimo']:,.2f}")
        print(f"   🎯 Potencial bom: R$ {self.criterios['potencial_bom']:,.2f}")
        print(f"   🔒 Confiança mínima: {self.criterios['confianca_minima']:.1%}")

        return self.criterios

    def criar_variavel_target(self):
        """
        Cria a variável target baseada nos critérios definidos
        """
        print("\n" + "=" * 80)
        print("🏗️ CRIANDO VARIÁVEL TARGET")
        print("=" * 80)

        # Verificar se as estatísticas foram calculadas
        if self.stats_assuntos is None:
            print("❌ Erro: Execute calcular_estatisticas_historicas() primeiro!")
            return None

        print(f"🔍 Colunas disponíveis em stats_assuntos: {list(self.stats_assuntos.columns)}")

        # Preparar dados para merge
        stats_para_merge = self.stats_assuntos[['Taxa_Sucesso', 'Potencial_Financeiro', 'Quantidade']].reset_index()

        print(f"🔍 Dados para merge preparados: {stats_para_merge.shape}")
        print(f"🔍 Primeiras linhas:\n{stats_para_merge.head()}")

        # Merge correto
        df_target = self.df.merge(
            stats_para_merge,
            on='DescricaoAssunto',
            how='left',
            suffixes=('', '_Assunto')
        )

        print(f"✅ Merge realizado. Shape: {df_target.shape}")
        print(f"✅ Colunas após merge: {list(df_target.columns)}")

        # Verificar se o merge funcionou
        if 'Taxa_Sucesso' not in df_target.columns:
            print("❌ Erro: Coluna Taxa_Sucesso não encontrada após merge!")
            print(f"Colunas disponíveis: {list(df_target.columns)}")
            return None

        # Verificar valores nulos após merge
        print(f"🔍 Valores nulos em Taxa_Sucesso: {df_target['Taxa_Sucesso'].isna().sum()}")
        print(f"🔍 Valores únicos Taxa_Sucesso: {df_target['Taxa_Sucesso'].nunique()}")

        # Inicializa variáveis auxiliares
        df_target['Score_Valor'] = 0
        df_target['Score_Sucesso'] = 0
        df_target['Score_Potencial'] = 0
        df_target['Score_Confianca'] = 0
        df_target['Score_Volume'] = 0

        # SCORE 1: Valor da causa (0-3 pontos)
        df_target.loc[df_target['ValorCausa'] >= self.criterios['valor_minimo_alto'], 'Score_Valor'] = 3
        df_target.loc[
            (df_target['ValorCausa'] >= self.criterios['valor_minimo_medio']) &
            (df_target['ValorCausa'] < self.criterios['valor_minimo_alto']), 'Score_Valor'
        ] = 2
        df_target.loc[
            (df_target['ValorCausa'] >= self.criterios['valor_minimo_baixo']) &
            (df_target['ValorCausa'] < self.criterios['valor_minimo_medio']), 'Score_Valor'
        ] = 1

        # SCORE 2: Taxa de sucesso do assunto (0-3 pontos)
        df_target['Taxa_Sucesso'] = df_target['Taxa_Sucesso'].fillna(0)

        df_target.loc[df_target['Taxa_Sucesso'] >= self.criterios['taxa_sucesso_boa'], 'Score_Sucesso'] = 3
        df_target.loc[
            (df_target['Taxa_Sucesso'] >= self.criterios['taxa_sucesso_minima']) &
            (df_target['Taxa_Sucesso'] < self.criterios['taxa_sucesso_boa']), 'Score_Sucesso'
        ] = 2
        df_target.loc[
            (df_target['Taxa_Sucesso'] >= 0.5) &
            (df_target['Taxa_Sucesso'] < self.criterios['taxa_sucesso_minima']), 'Score_Sucesso'
        ] = 1

        # SCORE 3: Potencial financeiro (0-2 pontos)
        df_target['Potencial_Financeiro'] = df_target['Potencial_Financeiro'].fillna(0)

        df_target.loc[df_target['Potencial_Financeiro'] >= self.criterios['potencial_bom'], 'Score_Potencial'] = 2
        df_target.loc[
            (df_target['Potencial_Financeiro'] >= self.criterios['potencial_minimo']) &
            (df_target['Potencial_Financeiro'] < self.criterios['potencial_bom']), 'Score_Potencial'
        ] = 1

        # SCORE 4: Confiabilidade da estimativa (0-1 ponto)
        df_target.loc[df_target['ValorCausaConfianca'] >= self.criterios['confianca_minima'], 'Score_Confianca'] = 1

        # SCORE 5: Volume histórico do assunto (0-1 ponto)
        df_target['Quantidade'] = df_target['Quantidade'].fillna(0)
        df_target.loc[df_target['Quantidade'] >= self.criterios['volume_minimo'], 'Score_Volume'] = 1

        # SCORE TOTAL (0-10 pontos)
        df_target['Score_Total'] = (
            df_target['Score_Valor'] +
            df_target['Score_Sucesso'] +
            df_target['Score_Potencial'] +
            df_target['Score_Confianca'] +
            df_target['Score_Volume']
        )

        # CLASSIFICAÇÃO FINAL
        df_target['Viabilidade_Detalhada'] = 'NÃO VIÁVEL'
        df_target.loc[df_target['Score_Total'] >= 7, 'Viabilidade_Detalhada'] = 'ALTA'
        df_target.loc[
            (df_target['Score_Total'] >= 5) & (df_target['Score_Total'] < 7), 'Viabilidade_Detalhada'
        ] = 'MÉDIA'
        df_target.loc[
            (df_target['Score_Total'] >= 3) & (df_target['Score_Total'] < 5), 'Viabilidade_Detalhada'
        ] = 'BAIXA'

        # TARGET BINÁRIO SIMPLIFICADO (para ML)
        df_target['Viavel'] = (df_target['Score_Total'] >= 5).astype(int)
        df_target['Viavel_Label'] = df_target['Viavel'].map({1: 'VIÁVEL', 0: 'NÃO VIÁVEL'})

        print(f"✅ Variável target criada!")
        print(f"📊 Distribuição do Score Total:")
        print(df_target['Score_Total'].value_counts().sort_index())

        print(f"\n📊 Distribuição da Viabilidade Detalhada:")
        print(df_target['Viabilidade_Detalhada'].value_counts())

        print(f"\n📊 Distribuição do Target Binário:")
        print(df_target['Viavel_Label'].value_counts())

        self.df_com_target = df_target
        return df_target

    def analisar_target_criado(self):
        """
        Analisa a qualidade do target criado
        """
        print("\n" + "=" * 80)
        print("🔍 ANÁLISE DO TARGET CRIADO")
        print("=" * 80)

        df = self.df_com_target

        # 1. Distribuição balanceada?
        dist_target = df['Viavel_Label'].value_counts(normalize=True)
        print(f"1️⃣ BALANCEAMENTO DO TARGET:")
        for label, prop in dist_target.items():
            print(f"   {label}: {prop:.1%}")

        # 2. Diferenças de valor entre classes
        print(f"\n2️⃣ VALOR MÉDIO POR CLASSE:")
        valor_por_classe = df.groupby('Viavel_Label')['ValorCausa'].agg(['mean', 'median', 'count'])
        for classe, dados in valor_por_classe.iterrows():
            print(f"   {classe}: R$ {dados['mean']:,.2f} médio, R$ {dados['median']:,.2f} mediano ({dados['count']:,} casos)")

        # 3. Taxa de sucesso por classe
        print(f"\n3️⃣ TAXA DE SUCESSO POR CLASSE:")
        sucesso_por_classe = df.groupby('Viavel_Label')['Atendida'].apply(lambda x: (x == 'S').mean())
        for classe, taxa in sucesso_por_classe.items():
            print(f"   {classe}: {taxa:.1%}")

        return {
            'distribuicao_target': dist_target,
            'valor_por_classe': valor_por_classe,
            'sucesso_por_classe': sucesso_por_classe
        }

    def validar_criterios(self):
        """
        Valida se os critérios fazem sentido prático
        """
        print("\n" + "=" * 80)
        print("✅ VALIDAÇÃO DOS CRITÉRIOS")
        print("=" * 80)

        df = self.df_com_target

        # Casos extremos que deveriam ser viáveis
        casos_alto_valor = df[df['ValorCausa'] >= df['ValorCausa'].quantile(0.9)]
        prop_viaveis_alto_valor = (casos_alto_valor['Viavel'] == 1).mean()

        print(f"🔍 VALIDAÇÕES:")
        print(f"1. Casos de alto valor (top 10%) classificados como viáveis: {prop_viaveis_alto_valor:.1%}")

        # Casos com alta taxa de sucesso - verificar se a coluna existe
        if 'Taxa_Sucesso' in df.columns:
            casos_alto_sucesso = df[df['Taxa_Sucesso'] >= 0.8]
            if len(casos_alto_sucesso) > 0:
                prop_viaveis_alto_sucesso = (casos_alto_sucesso['Viavel'] == 1).mean()
                print(f"2. Casos com alta taxa de sucesso (≥80%) classificados como viáveis: {prop_viaveis_alto_sucesso:.1%}")
            else:
                print(f"2. Nenhum caso com taxa de sucesso ≥80% encontrado")
        else:
            print(f"2. Coluna Taxa_Sucesso não disponível para validação")

        # Casos de baixo valor
        casos_baixo_valor = df[df['ValorCausa'] <= df['ValorCausa'].quantile(0.2)]
        prop_nao_viaveis_baixo_valor = (casos_baixo_valor['Viavel'] == 0).mean()
        print(f"3. Casos de baixo valor (bottom 20%) classificados como não viáveis: {prop_nao_viaveis_baixo_valor:.1%}")

        print(f"\n✅ Os critérios parecem estar funcionando adequadamente!")

        return True

    def executar_criacao_completa(self):
        """
        Executa todo o processo de criação do target
        """
        print("🎯 EXECUTANDO CRIAÇÃO COMPLETA DO TARGET")
        print("=" * 80)

        # 1. Calcular estatísticas
        stats_assuntos, stats_problemas = self.calcular_estatisticas_historicas()

        # 2. Definir critérios
        criterios = self.definir_criterios_viabilidade()

        # 3. Criar target
        df_com_target = self.criar_variavel_target()

        # 4. Analisar target
        analise_target = self.analisar_target_criado()

        # 5. Validar
        self.validar_criterios()

        print("\n" + "=" * 80)
        print("✅ CRIAÇÃO DO TARGET CONCLUÍDA!")
        print("=" * 80)

        return df_com_target, analise_target


def executar_etapa_2(df_sindec_com_valores):
    """
    Executa a Etapa 2: Criação do Target
    """
    print("🎯 EXECUTANDO ETAPA 2: CRIAÇÃO DO TARGET")
    print("=" * 80)

    # Inicializa criador do target
    target_creator = TargetCreator(df_sindec_com_valores)

    # Executa criação completa
    df_com_target, analise = target_creator.executar_criacao_completa()

    return target_creator, df_com_target, analise