"""
Sistema de estimativa de valores de causa para dados SINDEC
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional


class ValorCausaEstimatorBackup:
    """
    Sistema alternativo para estimar valores de causa quando a API DataJud não estiver disponível.
    Baseia-se em dados históricos, estudos do setor e análise de padrões.
    """

    def __init__(self):
        self.valores_base = self._criar_valores_base_historicos()
        self.multiplicadores_regionais = self._criar_multiplicadores_regionais()
        self.multiplicadores_temporais = self._criar_multiplicadores_temporais()

    def _criar_valores_base_historicos(self) -> Dict[str, Dict]:
        """
        Cria base de valores típicos por categoria baseado em dados históricos
        e estudos do setor de defesa do consumidor
        """
        return {
            # === TELECOMUNICAÇÕES ===
            'telefonia_cobranca': {
                'base': 2500.00,
                'min': 500.00,
                'max': 15000.00,
                'descricao': 'Cobrança indevida telefonia',
                'fonte': 'Análise ANATEL + TJSP'
            },
            'telefonia_interrupcao': {
                'base': 3000.00,
                'min': 800.00,
                'max': 20000.00,
                'descricao': 'Interrupção serviço telefônico',
                'fonte': 'Histórico TJSP'
            },
            'internet_velocidade': {
                'base': 2000.00,
                'min': 400.00,
                'max': 12000.00,
                'descricao': 'Problema velocidade internet',
                'fonte': 'Decisões TJSP'
            },
            'internet_interrupcao': {
                'base': 3500.00,
                'min': 700.00,
                'max': 18000.00,
                'descricao': 'Interrupção internet',
                'fonte': 'Análise histórica'
            },

            # === SERVIÇOS FINANCEIROS ===
            'banco_conta': {
                'base': 4000.00,
                'min': 800.00,
                'max': 25000.00,
                'descricao': 'Problemas conta bancária',
                'fonte': 'BACEN + TJSP'
            },
            'cartao_credito_cobranca': {
                'base': 3500.00,
                'min': 700.00,
                'max': 30000.00,
                'descricao': 'Cobrança indevida cartão',
                'fonte': 'Histórico bancário'
            },
            'cartao_credito_anuidade': {
                'base': 1500.00,
                'min': 300.00,
                'max': 8000.00,
                'descricao': 'Anuidade cartão indevida',
                'fonte': 'Decisões TJSP'
            },
            'emprestimo_juros': {
                'base': 8000.00,
                'min': 2000.00,
                'max': 50000.00,
                'descricao': 'Juros abusivos empréstimo',
                'fonte': 'STJ + TJSP'
            },
            'financiamento_imovel': {
                'base': 15000.00,
                'min': 5000.00,
                'max': 100000.00,
                'descricao': 'Financiamento imobiliário',
                'fonte': 'Análise CEF + bancos'
            },

            # === VAREJO/COMÉRCIO ELETRÔNICO ===
            'ecommerce_entrega': {
                'base': 1800.00,
                'min': 300.00,
                'max': 10000.00,
                'descricao': 'Problema entrega e-commerce',
                'fonte': 'PROCON + TJSP'
            },
            'produto_defeituoso': {
                'base': 2200.00,
                'min': 400.00,
                'max': 15000.00,
                'descricao': 'Produto com defeito',
                'fonte': 'CDC + jurisprudência'
            },
            'garantia_assistencia': {
                'base': 2800.00,
                'min': 500.00,
                'max': 20000.00,
                'descricao': 'Problema assistência técnica',
                'fonte': 'Análise SENACON'
            },
            'propaganda_enganosa': {
                'base': 4500.00,
                'min': 1000.00,
                'max': 25000.00,
                'descricao': 'Propaganda enganosa',
                'fonte': 'CDC Art. 37'
            },

            # === ENERGIA ELÉTRICA ===
            'energia_conta_alta': {
                'base': 3200.00,
                'min': 600.00,
                'max': 20000.00,
                'descricao': 'Conta energia elevada',
                'fonte': 'ANEEL + TJSP'
            },
            'energia_corte_indevido': {
                'base': 4000.00,
                'min': 800.00,
                'max': 25000.00,
                'descricao': 'Corte indevido energia',
                'fonte': 'Res. ANEEL 414'
            },
            'energia_medidor': {
                'base': 2500.00,
                'min': 500.00,
                'max': 15000.00,
                'descricao': 'Problema medidor energia',
                'fonte': 'Histórico distribuidoras'
            },

            # === PLANOS DE SAÚDE ===
            'plano_saude_negativa': {
                'base': 8000.00,
                'min': 2000.00,
                'max': 50000.00,
                'descricao': 'Negativa cobertura plano saúde',
                'fonte': 'ANS + STJ'
            },
            'plano_saude_reembolso': {
                'base': 4500.00,
                'min': 800.00,
                'max': 30000.00,
                'descricao': 'Reembolso plano saúde',
                'fonte': 'Lei 9656/98'
            },
            'plano_saude_carencia': {
                'base': 3500.00,
                'min': 700.00,
                'max': 20000.00,
                'descricao': 'Carência abusiva',
                'fonte': 'ANS + TJSP'
            },

            # === SEGUROS ===
            'seguro_negativa': {
                'base': 12000.00,
                'min': 3000.00,
                'max': 80000.00,
                'descricao': 'Negativa indenização seguro',
                'fonte': 'SUSEP + STJ'
            },
            'seguro_atraso': {
                'base': 6000.00,
                'min': 1500.00,
                'max': 40000.00,
                'descricao': 'Atraso pagamento seguro',
                'fonte': 'Histórico SUSEP'
            },

            # === TRANSPORTE AÉREO ===
            'voo_cancelado': {
                'base': 5000.00,
                'min': 1000.00,
                'max': 30000.00,
                'descricao': 'Voo cancelado',
                'fonte': 'Res. ANAC 400'
            },
            'bagagem_extraviada': {
                'base': 3500.00,
                'min': 700.00,
                'max': 20000.00,
                'descricao': 'Bagagem extraviada',
                'fonte': 'Convenção Montreal'
            },
            'overbooking': {
                'base': 4500.00,
                'min': 900.00,
                'max': 25000.00,
                'descricao': 'Preterição embarque',
                'fonte': 'ANAC + TJSP'
            },

            # === EDUCAÇÃO ===
            'mensalidade_abusiva': {
                'base': 3000.00,
                'min': 600.00,
                'max': 20000.00,
                'descricao': 'Mensalidade abusiva',
                'fonte': 'Lei 9870/99'
            },
            'transferencia_escolar': {
                'base': 2500.00,
                'min': 500.00,
                'max': 15000.00,
                'descricao': 'Problema transferência',
                'fonte': 'LDB + TJSP'
            },

            # === OUTROS ===
            'dano_moral_consumidor': {
                'base': 5000.00,
                'min': 1000.00,
                'max': 50000.00,
                'descricao': 'Dano moral relação consumo',
                'fonte': 'STJ Súmula 385'
            }
        }

    def _criar_multiplicadores_regionais(self) -> Dict[str, float]:
        """
        Multiplicadores por região/UF baseados no custo de vida e jurisprudência local
        """
        return {
            'SP': 1.0,    # Base São Paulo
            'RJ': 0.95,   # Rio de Janeiro
            'MG': 0.85,   # Minas Gerais
            'RS': 0.90,   # Rio Grande do Sul
            'PR': 0.88,   # Paraná
            'SC': 0.92,   # Santa Catarina
            'GO': 0.80,   # Goiás
            'DF': 1.05,   # Distrito Federal
            'ES': 0.85,   # Espírito Santo
            'BA': 0.75,   # Bahia
            'PE': 0.70,   # Pernambuco
            'CE': 0.65,   # Ceará
            'PA': 0.60,   # Pará
            'MA': 0.55,   # Maranhão
            'PB': 0.60,   # Paraíba
            'RN': 0.60,   # Rio Grande do Norte
            'AL': 0.55,   # Alagoas
            'SE': 0.60,   # Sergipe
            'MT': 0.75,   # Mato Grosso
            'MS': 0.75,   # Mato Grosso do Sul
            'RO': 0.65,   # Rondônia
            'AC': 0.65,   # Acre
            'AM': 0.70,   # Amazonas
            'RR': 0.70,   # Roraima
            'AP': 0.65,   # Amapá
            'TO': 0.60,   # Tocantins
            'PI': 0.55    # Piauí
        }

    def _criar_multiplicadores_temporais(self) -> Dict[int, float]:
        """
        Ajuste temporal baseado na inflação e mudanças jurisprudenciais
        """
        return {
            2018: 0.85,
            2019: 0.90,
            2020: 0.95,
            2021: 1.00,
            2022: 1.08,
            2023: 1.15,
            2024: 1.22,
            2025: 1.25
        }

    def classificar_reclamacao(self, descricao_assunto: str,
                              descricao_problema: str = "") -> str:
        """
        Classifica a reclamação em uma categoria conhecida
        """
        texto_completo = f"{descricao_assunto} {descricao_problema}".lower()

        # Dicionário de palavras-chave para classificação
        classificadores = {
            'telefonia_cobranca': ['telefon', 'celular', 'cobrança', 'fatura', 'conta telefone'],
            'telefonia_interrupcao': ['telefon', 'celular', 'interrup', 'sem sinal', 'linha'],
            'internet_velocidade': ['internet', 'banda larga', 'velocidade', 'lent'],
            'internet_interrupcao': ['internet', 'banda larga', 'interrup', 'sem internet'],

            'banco_conta': ['banco', 'conta corrente', 'conta bancária', 'poupança'],
            'cartao_credito_cobranca': ['cartão', 'crédito', 'cobrança', 'fatura cartão'],
            'cartao_credito_anuidade': ['cartão', 'anuidade', 'taxa anual'],
            'emprestimo_juros': ['empréstimo', 'financiamento', 'juros', 'abusivo'],
            'financiamento_imovel': ['financiamento', 'imóvel', 'casa própria', 'apartamento'],

            'ecommerce_entrega': ['entrega', 'correios', 'prazo', 'compra online'],
            'produto_defeituoso': ['defeito', 'vício', 'quebrado', 'não funciona'],
            'garantia_assistencia': ['garantia', 'assistência técnica', 'conserto'],
            'propaganda_enganosa': ['propaganda', 'enganosa', 'publicidade falsa'],

            'energia_conta_alta': ['energia', 'luz', 'conta alta', 'tarifa'],
            'energia_corte_indevido': ['energia', 'luz', 'corte', 'suspensão'],
            'energia_medidor': ['energia', 'medidor', 'relógio'],

            'plano_saude_negativa': ['plano saúde', 'convênio', 'negativa', 'autorização'],
            'plano_saude_reembolso': ['plano saúde', 'reembolso', 'ressarcimento'],
            'plano_saude_carencia': ['plano saúde', 'carência', 'prazo'],

            'seguro_negativa': ['seguro', 'indenização', 'negativa', 'sinistro'],
            'seguro_atraso': ['seguro', 'atraso', 'pagamento', 'demora'],

            'voo_cancelado': ['voo', 'cancelado', 'aéreo', 'companhia aérea'],
            'bagagem_extraviada': ['bagagem', 'extraviada', 'perdida', 'mala'],
            'overbooking': ['overbooking', 'preterição', 'embarque negado'],

            'mensalidade_abusiva': ['escola', 'faculdade', 'mensalidade', 'educação'],
            'transferencia_escolar': ['transferência', 'escola', 'histórico'],

            'dano_moral_consumidor': ['dano moral', 'constrangimento', 'humilhação']
        }

        # Pontua cada categoria
        pontuacoes = {}
        for categoria, palavras_chave in classificadores.items():
            pontos = 0
            for palavra in palavras_chave:
                if palavra in texto_completo:
                    pontos += 1
            if pontos > 0:
                pontuacoes[categoria] = pontos

        # Retorna a categoria com maior pontuação
        if pontuacoes:
            return max(pontuacoes, key=pontuacoes.get)

        # Categoria padrão se não conseguir classificar
        return 'dano_moral_consumidor'

    def estimar_valor_causa(self, descricao_assunto: str,
                           descricao_problema: str = "",
                           uf: str = "SP",
                           ano: int = 2020,
                           ajuste_complexidade: float = 1.0) -> Dict:
        """
        Estima o valor da causa baseado nos parâmetros fornecidos
        """

        # Classifica a reclamação
        categoria = self.classificar_reclamacao(descricao_assunto, descricao_problema)

        # Obtém valores base
        if categoria not in self.valores_base:
            categoria = 'dano_moral_consumidor'  # Fallback

        valores = self.valores_base[categoria]
        valor_base = valores['base']
        valor_min = valores['min']
        valor_max = valores['max']

        # Aplica multiplicadores
        mult_regional = self.multiplicadores_regionais.get(uf, 0.75)
        mult_temporal = self.multiplicadores_temporais.get(ano, 1.0)

        # Calcula valores finais
        valor_estimado = valor_base * mult_regional * mult_temporal * ajuste_complexidade
        valor_min_final = valor_min * mult_regional * mult_temporal
        valor_max_final = valor_max * mult_regional * mult_temporal

        # Garante que está dentro dos limites
        valor_estimado = max(valor_min_final, min(valor_estimado, valor_max_final))

        return {
            'valor_estimado': round(valor_estimado, 2),
            'valor_minimo': round(valor_min_final, 2),
            'valor_maximo': round(valor_max_final, 2),
            'categoria': categoria,
            'descricao_categoria': valores['descricao'],
            'fonte_dados': valores['fonte'],
            'multiplicador_regional': mult_regional,
            'multiplicador_temporal': mult_temporal,
            'ajuste_complexidade': ajuste_complexidade,
            'confianca': self._calcular_confianca(categoria, uf, ano)
        }

    def _calcular_confianca(self, categoria: str, uf: str, ano: int) -> float:
        """
        Calcula a confiança da estimativa baseada em vários fatores
        """
        confianca = 0.7  # Base

        # Ajustes por categoria (algumas têm dados mais sólidos)
        categorias_alta_confianca = [
            'plano_saude_negativa', 'voo_cancelado', 'energia_corte_indevido',
            'cartao_credito_cobranca', 'emprestimo_juros'
        ]

        if categoria in categorias_alta_confianca:
            confianca += 0.2

        # Ajuste por região (SP tem mais dados históricos)
        if uf in ['SP', 'RJ', 'MG', 'RS']:
            confianca += 0.1
        elif uf in ['PR', 'SC', 'GO', 'DF']:
            confianca += 0.05
        else:
            confianca -= 0.1

        # Ajuste temporal (dados mais recentes são mais confiáveis)
        if ano >= 2022:
            confianca += 0.1
        elif ano >= 2020:
            confianca += 0.05
        else:
            confianca -= 0.15

        return max(0.3, min(1.0, confianca))

    def processar_dataframe_sindec(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Processa todo o DataFrame do SINDEC adicionando estimativas de valor
        """

        df_resultado = df.copy()

        # Colunas para adicionar
        colunas_novas = [
            'ValorCausa',
            'ValorCausaMinimo',
            'ValorCausaMaximo',
            'ValorCausaCategoria',
            'ValorCausaDescricao',
            'ValorCausaFonte',
            'ValorCausaConfianca',
            'ValorCausaMetodo'
        ]

        for col in colunas_novas:
            df_resultado[col] = np.nan

        df_resultado['ValorCausaMetodo'] = 'Estimativa histórica'

        print(f"Processando {len(df)} registros...")

        for index, row in df_resultado.reset_index(drop=True).iterrows():

            # Parâmetros da estimativa
            descricao_assunto = str(row.get('DescricaoAssunto', ''))
            descricao_problema = str(row.get('DescricaoProblema', ''))
            uf = str(row.get('UF', 'SP'))

            # Extrai ano da data de abertura ou usa padrão
            ano = 2020
            if 'DataAbertura' in row and pd.notna(row['DataAbertura']):
                try:
                    if isinstance(row['DataAbertura'], str):
                        ano = int(row['DataAbertura'][:4])
                    else:
                        ano = row['DataAbertura'].year
                except:
                    ano = 2020
            elif 'AnoCalendario' in row and pd.notna(row['AnoCalendario']):
                ano = int(row['AnoCalendario'])

            # Faz a estimativa
            estimativa = self.estimar_valor_causa(
                descricao_assunto=descricao_assunto,
                descricao_problema=descricao_problema,
                uf=uf,
                ano=ano
            )

            # Preenche as colunas
            df_resultado.loc[index, 'ValorCausa'] = estimativa['valor_estimado']
            df_resultado.loc[index, 'ValorCausaMinimo'] = estimativa['valor_minimo']
            df_resultado.loc[index, 'ValorCausaMaximo'] = estimativa['valor_maximo']
            df_resultado.loc[index, 'ValorCausaCategoria'] = estimativa['categoria']
            df_resultado.loc[index, 'ValorCausaDescricao'] = estimativa['descricao_categoria']
            df_resultado.loc[index, 'ValorCausaFonte'] = estimativa['fonte_dados']
            df_resultado.loc[index, 'ValorCausaConfianca'] = estimativa['confianca']

            # Progress indicator
            if (index + 1) % 1000 == 0:
                print(f"Processados {index + 1:,} registros...")

        print("✅ Processamento concluído!")

        # Estatísticas finais
        self._imprimir_estatisticas(df_resultado)

        return df_resultado

    def _imprimir_estatisticas(self, df: pd.DataFrame):
        """
        Imprime estatísticas do processamento
        """
        print("\n" + "="*60)
        print("📊 ESTATÍSTICAS DAS ESTIMATIVAS")
        print("="*60)

        total = len(df)
        print(f"Total de registros: {total:,}")

        valores = df['ValorCausa'].dropna()
        print(f"Registros com valor: {len(valores):,}")

        if len(valores) > 0:
            print(f"\n💰 VALORES:")
            print(f"Soma total: R$ {valores.sum():,.2f}")
            print(f"Valor médio: R$ {valores.mean():,.2f}")
            print(f"Valor mediano: R$ {valores.median():,.2f}")
            print(f"Menor valor: R$ {valores.min():,.2f}")
            print(f"Maior valor: R$ {valores.max():,.2f}")

            print(f"\n🎯 CONFIANÇA:")
            confianca_media = df['ValorCausaConfianca'].mean()
            print(f"Confiança média: {confianca_media:.3f}")

            print(f"\n📋 TOP 5 CATEGORIAS:")
            top_categorias = df['ValorCausaCategoria'].value_counts().head()
            for categoria, count in top_categorias.items():
                valor_medio = df[df['ValorCausaCategoria'] == categoria]['ValorCausa'].mean()
                print(f"{categoria}: {count:,} casos (R$ {valor_medio:,.2f} médio)")