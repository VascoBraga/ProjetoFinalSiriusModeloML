"""
Script principal para análise de viabilidade jurídica SINDEC
"""

import os
import sys
from typing import Optional
import pandas as pd

from data_processor import DataProcessor
from datajud_enricher import DataJudEnricher, enriquecer_sindec_com_datajud
from valor_estimator import ValorCausaEstimatorBackup
from analyzer import SindecAnalyzer, ViabilityChecker
from config import (
    OUTPUT_FILE_COMPLETO, 
    OUTPUT_FILE_RESUMO, 
    MAX_ASSUNTOS_ENRIQUECIMENTO
)


class SindecProcessor:
    """Classe principal para processamento completo dos dados SINDEC"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.data_processor = DataProcessor()
        self.valor_estimator = ValorCausaEstimatorBackup()
        self.analyzer = None
        self.viability_checker = ViabilityChecker()
        
        print("🚀 SISTEMA DE ANÁLISE DE VIABILIDADE JURÍDICA SINDEC")
        print("="*60)
    
    def carregar_e_limpar_dados(self, file_path: str) -> pd.DataFrame:
        """
        Carrega e limpa os dados SINDEC
        
        Args:
            file_path: Caminho para o arquivo CSV
            
        Returns:
            DataFrame limpo
        """
        print("\n📊 ETAPA 1: CARREGAMENTO E LIMPEZA DOS DADOS")
        print("-" * 50)
        
        # Carrega dados
        df = self.data_processor.load_sindec_data(file_path)
        
        # Limpa dados
        df_clean = self.data_processor.clean_data(df)
        
        # Remove registros vazios
        df_final = self.data_processor.remove_empty_records(df_clean)
        
        # Mostra informações
        self.data_processor.print_data_info(df_final, "DADOS APÓS LIMPEZA")
        
        return df_final
    
    def enriquecer_com_datajud(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tenta enriquecer dados com API DataJud
        
        Args:
            df: DataFrame para enriquecer
            
        Returns:
            DataFrame enriquecido (ou original se falhou)
        """
        print("\n🌐 ETAPA 2: ENRIQUECIMENTO COM API DATAJUD")
        print("-" * 50)
        
        if not self.api_key:
            print("⚠️ API Key não fornecida. Pulando enriquecimento DataJud.")
            return df
        
        try:
            df_enriquecido = enriquecer_sindec_com_datajud(
                df, 
                self.api_key, 
                max_assuntos=MAX_ASSUNTOS_ENRIQUECIMENTO
            )
            return df_enriquecido
            
        except Exception as e:
            print(f"❌ Erro no enriquecimento DataJud: {e}")
            print("🔄 Continuando sem enriquecimento...")
            return df
    
    def estimar_valores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Estima valores de causa usando sistema backup
        
        Args:
            df: DataFrame para processar
            
        Returns:
            DataFrame com valores estimados
        """
        print("\n💰 ETAPA 3: ESTIMATIVA DE VALORES DE CAUSA")
        print("-" * 50)
        
        # Verifica se já tem valores (do DataJud)
        if 'ValorCausaReal' in df.columns and df['ValorCausaReal'].notna().sum() > 0:
            print("✅ Valores reais encontrados do DataJud. Complementando com estimativas...")
            
        df_com_valores = self.valor_estimator.processar_dataframe_sindec(df)
        
        return df_com_valores
    
    def analisar_dados(self, df: pd.DataFrame) -> dict:
        """
        Executa análises completas dos dados
        
        Args:
            df: DataFrame processado
            
        Returns:
            Dicionário com relatórios de análise
        """
        print("\n📊 ETAPA 4: ANÁLISE COMPLETA DOS DADOS")
        print("-" * 50)
        
        self.analyzer = SindecAnalyzer(df)
        relatorio = self.analyzer.gerar_relatorio_completo()
        
        return relatorio
    
    def salvar_resultados(self, df: pd.DataFrame):
        """
        Salva os resultados em arquivos
        
        Args:
            df: DataFrame final para salvar
        """
        print("\n💾 ETAPA 5: SALVANDO RESULTADOS")
        print("-" * 50)
        
        # Salva arquivo completo
        self.data_processor.save_results(df, OUTPUT_FILE_COMPLETO)
        
        # Cria e salva resumo
        resumo = self.data_processor.create_summary_report(df)
        self.data_processor.save_results(resumo, OUTPUT_FILE_RESUMO)
        
        print(f"✅ Arquivos salvos:")
        print(f"   📄 Completo: {OUTPUT_FILE_COMPLETO}")
        print(f"   📊 Resumo: {OUTPUT_FILE_RESUMO}")
    
    def exemplo_analise_viabilidade(self, valor: float = 3000, 
                                  tipo_assunto: str = "Energia Elétrica",
                                  problema: str = "Cobrança Indevida",
                                  regiao: str = "Nordeste",
                                  uf: str = "AL") -> dict:
        """
        Executa exemplo de análise de viabilidade
        
        Args:
            valor: Valor da causa
            tipo_assunto: Tipo do assunto
            problema: Tipo do problema
            regiao: Região
            uf: UF
            
        Returns:
            Resultado da análise
        """
        print("\n🎯 EXEMPLO: ANÁLISE DE VIABILIDADE")
        print("-" * 50)
        
        resultado = self.viability_checker.analisar_viabilidade(
            valor=valor,
            tipo_assunto=tipo_assunto,
            problema=problema,
            regiao=regiao,
            uf=uf
        )
        
        # Exibe resultado
        print("⚠️ Modelo não encontrado. Usando análise por regras.")
        
        if resultado['status'] == 'VIÁVEL':
            print("✅ CAUSA VIÁVEL")
            print(f"Recomendação: {resultado['recomendacao']} esta causa")
        else:
            print(f"⚠️ CAUSA {resultado['status']}")
            print(f"Recomendação: {resultado['recomendacao']}")
        
        print(f"\n📊 Probabilidade VIÁVEL: {resultado['probabilidade_viavel']:.1%}")
        print(f"📊 Probabilidade NÃO VIÁVEL: {resultado['probabilidade_nao_viavel']:.1%}")
        print(f"📊 Score de Viabilidade: {resultado['score_viabilidade']}")
        
        print(f"\n🎯 FATORES INFLUENCIADORES:")
        print("="*50)
        for i, fator in enumerate(resultado['fatores_influenciadores'], 1):
            print(f" {i}. {fator}")
        
        print(f"\n📋 MÉTODO: {resultado['metodo']}")
        print(f"🎯 CONFIANÇA: {resultado['confianca']}")
        
        return resultado
    
    def processar_completo(self, file_path: str) -> pd.DataFrame:
        """
        Executa processamento completo
        
        Args:
            file_path: Caminho para o arquivo de dados
            
        Returns:
            DataFrame final processado
        """
        # Etapa 1: Carregar e limpar
        df = self.carregar_e_limpar_dados(file_path)
        
        # Etapa 2: Enriquecer com DataJud (se disponível)
        df = self.enriquecer_com_datajud(df)
        
        # Etapa 3: Estimar valores
        df = self.estimar_valores(df)
        
        # Etapa 4: Analisar
        relatorio = self.analisar_dados(df)
        
        # Etapa 5: Salvar
        self.salvar_resultados(df)
        
        # Exemplo de análise de viabilidade
        self.exemplo_analise_viabilidade()
        
        print(f"\n🎉 PROCESSAMENTO COMPLETO CONCLUÍDO!")
        print(f"📊 Total processado: {len(df):,} registros")
        
        if 'ValorCausa' in df.columns:
            valores = df['ValorCausa'].dropna()
            if len(valores) > 0:
                print(f"💰 Valor total estimado: R$ {valores.sum():,.2f}")
                print(f"📈 Valor médio por reclamação: R$ {valores.mean():,.2f}")
        
        return df


def main():
    """Função principal"""
    
    # Configurações
    DATA_FILE = "PROCON_2017_21.csv"  # Altere para o caminho do seu arquivo
    API_KEY = None  # Coloque sua chave da API DataJud aqui se tiver
    
    # Verifica se arquivo existe
    if not os.path.exists(DATA_FILE):
        print(f"❌ Arquivo não encontrado: {DATA_FILE}")
        print("📝 Certifique-se de que o arquivo de dados está no diretório correto.")
        return
    
    try:
        # Inicializa processador
        processor = SindecProcessor(api_key=API_KEY)
        
        # Executa processamento completo
        df_final = processor.processar_completo(DATA_FILE)
        
        print("\n" + "="*60)
        print("✅ EXECUÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n⚠️ Execução interrompida pelo usuário.")
        
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        print("🔍 Verifique os logs acima para mais detalhes.")


if __name__ == "__main__":
    main()