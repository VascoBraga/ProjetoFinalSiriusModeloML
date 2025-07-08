"""
Enriquecedor de dados SINDEC usando API DataJud do CNJ
"""

import requests
import pandas as pd
import numpy as np
import time
from typing import Dict, List, Optional
from config import DATAJUD_BASE_URL, DATAJUD_DEFAULT_TRIBUNAL, PROCESSOS_POR_TERMO


class DataJudEnricher:
    """
    Enriquecedor de dados SINDEC usando API DataJud do CNJ
    Busca valores reais de processos do TJSP
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = DATAJUD_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'APIKey {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (DataAnalysis/1.0)'
        })

        # Mapeamento de assuntos SINDEC para termos jurídicos
        self.mapeamento_assuntos = self._criar_mapeamento_assuntos()

        # Cache de buscas para evitar requisições repetidas
        self.cache_buscas = {}

        print(f"✅ DataJudEnricher inicializado com API Key")
        print(f"🌐 Base URL: {self.base_url}")

    def _criar_mapeamento_assuntos(self) -> Dict[str, List[str]]:
        """
        Mapeia assuntos do SINDEC para termos de busca na API DataJud
        """
        return {
            # Telecomunicações
            'telefon': ['telefonia', 'serviço telefônico', 'linha telefônica', 'celular', 'serviços de telecomunicações'],
            'internet': ['internet', 'banda larga', 'provedor', 'conexão', 'serviço de dados'],

            # Serviços Financeiros
            'banco': ['banco', 'instituição financeira', 'conta bancária', 'conta corrente', 'poupança'],
            'cartão': ['cartão de crédito', 'cartão débito', 'anuidade', 'fatura'],
            'empréstimo': ['empréstimo', 'financiamento', 'crédito', 'CDC'],
            'financiamento': ['financiamento imobiliário', 'casa própria', 'FGTS'],

            # Comércio/Varejo
            'comércio': ['comércio eletrônico', 'venda', 'produto', 'mercadoria'],
            'produto': ['produto defeituoso', 'vício', 'garantia', 'assistência técnica'],
            'entrega': ['entrega', 'prazo', 'correios', 'transportadora'],

            # Energia
            'energia': ['energia elétrica', 'conta de luz', 'distribuidora', 'tarifa'],

            # Seguros
            'seguro': ['seguro', 'seguradora', 'sinistro', 'indenização', 'apólice'],

            # Planos de Saúde
            'saúde': ['plano de saúde', 'convênio médico', 'seguro saúde', 'ANS'],

            # Transporte
            'aéreo': ['transporte aéreo', 'companhia aérea', 'voo', 'ANAC'],
            'terrestre': ['transporte terrestre', 'ônibus', 'rodoviário'],

            # Educação
            'educação': ['ensino', 'educação', 'escola', 'universidade', 'curso'],

            # Outros
            'consumidor': ['direito do consumidor', 'relação de consumo', 'CDC']
        }

    def testar_conexao(self) -> bool:
        """
        Testa se a conexão com a API está funcionando
        """
        print("🔍 TESTANDO CONEXÃO COM API DATAJUD...")

        try:
            endpoint = f"{self.base_url}/api_publica_{DATAJUD_DEFAULT_TRIBUNAL}/_search"

            query_teste = {
                "query": {"match_all": {}},
                "size": 1
            }

            response = self.session.post(endpoint, json=query_teste, timeout=10)

            if response.status_code == 200:
                data = response.json()
                total_docs = data.get('hits', {}).get('total', {})

                if isinstance(total_docs, dict):
                    total = total_docs.get('value', 0)
                else:
                    total = total_docs

                print(f"✅ Conexão OK! Total de documentos disponíveis: {total:,}")
                return True

            else:
                print(f"❌ Erro na conexão. Status: {response.status_code}")
                print(f"Resposta: {response.text[:200]}")
                return False

        except Exception as e:
            print(f"❌ Erro na conexão: {e}")
            return False

    def buscar_processos_por_termo(self, termo: str, tribunal: str = DATAJUD_DEFAULT_TRIBUNAL,
                                  limite: int = PROCESSOS_POR_TERMO, incluir_sem_valor: bool = False) -> List[Dict]:
        """
        Busca processos na API DataJud por termo específico
        """
        # Verifica cache
        cache_key = f"{termo}_{tribunal}_{limite}_{incluir_sem_valor}"
        if cache_key in self.cache_buscas:
            return self.cache_buscas[cache_key]

        try:
            endpoint = f"{self.base_url}/api_publica_{tribunal}/_search"

            # Query Elasticsearch
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": termo,
                                    "fields": ["assunto", "classe", "orgaoJulgador"],
                                    "fuzziness": "AUTO",
                                    "minimum_should_match": "70%"
                                }
                            }
                        ]
                    }
                },
                "size": limite,
                "sort": [
                    {"dataAtualizacao": {"order": "desc"}}
                ],
                "_source": [
                    "numeroProcesso", "valorCausa", "assunto", "classe",
                    "dataAjuizamento", "orgaoJulgador", "dataAtualizacao",
                    "grau", "situacao"
                ]
            }

            # Filtro para processos com valor de causa (se solicitado)
            if not incluir_sem_valor:
                query["query"]["bool"]["filter"] = [
                    {
                        "exists": {"field": "valorCausa"}
                    },
                    {
                        "range": {"valorCausa": {"gt": 0}}
                    }
                ]

            response = self.session.post(endpoint, json=query, timeout=15)

            if response.status_code == 200:
                data = response.json()
                processos = []

                hits = data.get('hits', {}).get('hits', [])

                for hit in hits:
                    source = hit.get('_source', {})

                    processo = {
                        'numero': source.get('numeroProcesso', ''),
                        'valor_causa': source.get('valorCausa', 0),
                        'assunto': source.get('assunto', ''),
                        'classe': source.get('classe', ''),
                        'data_ajuizamento': source.get('dataAjuizamento', ''),
                        'orgao': source.get('orgaoJulgador', ''),
                        'grau': source.get('grau', ''),
                        'situacao': source.get('situacao', ''),
                        'termo_busca': termo
                    }

                    processos.append(processo)

                # Salva no cache
                self.cache_buscas[cache_key] = processos

                print(f"🔍 '{termo}': {len(processos)} processos encontrados")
                return processos

            else:
                print(f"❌ Erro na busca para '{termo}'. Status: {response.status_code}")
                return []

        except Exception as e:
            print(f"❌ Erro na busca para '{termo}': {e}")
            return []

    def mapear_assunto_sindec_para_termos(self, assunto_sindec: str) -> List[str]:
        """
        Mapeia um assunto do SINDEC para termos de busca jurídicos
        """
        assunto_lower = assunto_sindec.lower()
        termos_encontrados = []

        # Busca por palavras-chave no mapeamento
        for categoria, termos in self.mapeamento_assuntos.items():
            if categoria in assunto_lower:
                termos_encontrados.extend(termos)

        # Se não encontrou, usa palavras do próprio assunto
        if not termos_encontrados:
            # Extrai palavras principais (remove conectivos)
            palavras_principais = []
            palavras_ignorar = ['de', 'da', 'do', 'em', 'com', 'por', 'para', 'e', 'ou', '-', '/', '(', ')']

            for palavra in assunto_sindec.split():
                palavra_limpa = palavra.lower().strip('(),/')
                if len(palavra_limpa) > 2 and palavra_limpa not in palavras_ignorar:
                    palavras_principais.append(palavra_limpa)

            termos_encontrados = palavras_principais[:3]  # Máximo 3 termos

        return list(set(termos_encontrados))[:3]  # Remove duplicatas, máximo 3

    def extrair_valores_por_assunto_sindec(self, df_sindec: pd.DataFrame,
                                         max_assuntos: int = 20) -> Dict[str, Dict]:
        """
        Extrai valores de causa do DataJud para os principais assuntos do SINDEC
        """
        print("="*80)
        print("🔍 EXTRAINDO VALORES DE CAUSA POR ASSUNTO SINDEC")
        print("="*80)

        # Principais assuntos do SINDEC
        principais_assuntos = df_sindec['DescricaoAssunto'].value_counts().head(max_assuntos)

        print(f"📊 Processando {len(principais_assuntos)} principais assuntos...")

        valores_por_assunto = {}

        for i, (assunto, count) in enumerate(principais_assuntos.items(), 1):

            print(f"\n{i:2d}/{len(principais_assuntos)} 📋 {assunto[:60]}...")
            print(f"      Ocorrências no SINDEC: {count:,}")

            # Mapeia para termos jurídicos
            termos_busca = self.mapear_assunto_sindec_para_termos(assunto)
            print(f"      Termos de busca: {termos_busca}")

            valores_encontrados = []
            processos_detalhes = []

            # Busca por cada termo
            for termo in termos_busca:
                processos = self.buscar_processos_por_termo(termo)

                for proc in processos:
                    if proc['valor_causa'] and proc['valor_causa'] > 0:
                        valores_encontrados.append(proc['valor_causa'])
                        processos_detalhes.append(proc)

                # Pausa para não sobrecarregar API
                time.sleep(0.5)

            if valores_encontrados:
                # Calcula estatísticas
                valores_array = np.array(valores_encontrados)

                estatisticas = {
                    'valores_encontrados': valores_encontrados,
                    'processos': processos_detalhes,
                    'count': len(valores_encontrados),
                    'mean': np.mean(valores_array),
                    'median': np.median(valores_array),
                    'std': np.std(valores_array),
                    'min': np.min(valores_array),
                    'max': np.max(valores_array),
                    'q25': np.percentile(valores_array, 25),
                    'q75': np.percentile(valores_array, 75),
                    'termos_busca': termos_busca
                }

                valores_por_assunto[assunto] = estatisticas

                print(f"      ✅ {len(valores_encontrados)} valores encontrados")
                print(f"      💰 Valor médio: R$ {estatisticas['mean']:,.2f}")
                print(f"      📊 Mediana: R$ {estatisticas['median']:,.2f}")

            else:
                print(f"      ❌ Nenhum valor encontrado")

            # Pausa entre assuntos
            time.sleep(1)

        print(f"\n✅ Processamento concluído!")
        print(f"📊 Assuntos com valores encontrados: {len(valores_por_assunto)}/{len(principais_assuntos)}")

        return valores_por_assunto

    def aplicar_valores_reais_ao_sindec(self, df_sindec: pd.DataFrame,
                                       valores_por_assunto: Dict) -> pd.DataFrame:
        """
        Aplica os valores reais extraídos do DataJud ao DataFrame SINDEC
        """
        print("\n" + "="*80)
        print("💰 APLICANDO VALORES REAIS AO SINDEC")
        print("="*80)

        df_resultado = df_sindec.copy()

        # Novas colunas para valores reais
        df_resultado['ValorCausaReal'] = np.nan
        df_resultado['ValorCausaReal_Fonte'] = 'Não encontrado'
        df_resultado['ValorCausaReal_Confianca'] = 0.0
        df_resultado['ValorCausaReal_Count'] = 0

        for assunto, stats in valores_por_assunto.items():

            # Encontra registros deste assunto
            mask = df_resultado['DescricaoAssunto'] == assunto
            count_registros = mask.sum()

            if count_registros > 0:
                # Aplica valor médio (ou mediana, dependendo da estratégia)
                valor_aplicar = stats['median']  # Usa mediana para ser mais conservador
                confianca = min(stats['count'] / 20, 1.0)  # Confiança baseada na quantidade

                df_resultado.loc[mask, 'ValorCausaReal'] = valor_aplicar
                df_resultado.loc[mask, 'ValorCausaReal_Fonte'] = 'API DataJud'
                df_resultado.loc[mask, 'ValorCausaReal_Confianca'] = confianca
                df_resultado.loc[mask, 'ValorCausaReal_Count'] = stats['count']

                print(f"✅ {assunto[:50]}...")
                print(f"   📊 Aplicado a {count_registros:,} registros")
                print(f"   💰 Valor: R$ {valor_aplicar:,.2f}")
                print(f"   🎯 Confiança: {confianca:.2f}")

        # Estatísticas finais
        valores_aplicados = df_resultado['ValorCausaReal'].notna().sum()
        total_registros = len(df_resultado)

        print(f"\n📊 RESULTADO FINAL:")
        print(f"   Total de registros: {total_registros:,}")
        print(f"   Com valores reais: {valores_aplicados:,} ({valores_aplicados/total_registros*100:.1f}%)")

        if valores_aplicados > 0:
            print(f"   Valor médio aplicado: R$ {df_resultado['ValorCausaReal'].mean():,.2f}")
            print(f"   Valor total estimado: R$ {df_resultado['ValorCausaReal'].sum():,.2f}")

        return df_resultado

    def executar_enriquecimento_completo(self, df_sindec: pd.DataFrame,
                                        max_assuntos: int = 15) -> pd.DataFrame:
        """
        Executa o enriquecimento completo dos dados SINDEC
        """
        print("🚀 INICIANDO ENRIQUECIMENTO COMPLETO COM API DATAJUD")
        print("="*80)

        # 1. Testa conexão
        if not self.testar_conexao():
            print("❌ Falha na conexão. Enriquecimento cancelado.")
            return df_sindec

        # 2. Extrai valores por assunto
        valores_por_assunto = self.extrair_valores_por_assunto_sindec(
            df_sindec,
            max_assuntos=max_assuntos
        )

        if not valores_por_assunto:
            print("❌ Nenhum valor extraído. Enriquecimento cancelado.")
            return df_sindec

        # 3. Aplica valores ao DataFrame
        df_enriquecido = self.aplicar_valores_reais_ao_sindec(df_sindec, valores_por_assunto)

        print(f"\n✅ ENRIQUECIMENTO COMPLETO CONCLUÍDO!")
        return df_enriquecido


def enriquecer_sindec_com_datajud(df_sindec: pd.DataFrame, api_key: str,
                                 max_assuntos: int = 15) -> pd.DataFrame:
    """
    Função principal para enriquecer dados SINDEC com API DataJud
    
    Args:
        df_sindec: DataFrame com dados SINDEC
        api_key: Chave da API DataJud
        max_assuntos: Máximo de assuntos para processar
        
    Returns:
        DataFrame enriquecido com valores reais
    """
    print("🎯 ENRIQUECIMENTO SINDEC COM API DATAJUD")
    print("="*50)

    # Inicializa enriquecedor
    enricher = DataJudEnricher(api_key)

    # Executa enriquecimento
    df_enriquecido = enricher.executar_enriquecimento_completo(df_sindec, max_assuntos)

    return df_enriquecido