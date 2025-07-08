"""
Pipeline principal para classificação de viabilidade de causas jurídicas.
"""

import pandas as pd
import numpy as np
import sys
import warnings
warnings.filterwarnings('ignore')

# Imports dos módulos locais
from data_preprocessing import preprocessar_dados
from exploratory_analysis import executar_etapa_1
from target_creation import executar_etapa_2
from feature_engineering import executar_feature_engineering
from data_balancing import balancear_dados_viabilidade


class ViabilidadeClassificationPipeline:
    """
    Pipeline completo para classificação de viabilidade de causas jurídicas
    """
    
    def __init__(self):
        self.df_original = None
        self.df_preprocessado = None
        self.df_com_target = None
        self.df_features = None
        self.X_balanced = None
        self.y_balanced = None
        self.feature_names = None
        self.resultados = {}
    
    def carregar_dados(self, filepath):
        """
        Carrega dados do arquivo CSV
        """
        print("📂 CARREGANDO DADOS")
        print("=" * 30)
        
        try:
            self.df_original = pd.read_csv(filepath, encoding='utf-8')
            print(f"✅ Dados carregados: {self.df_original.shape}")
            print(f"   Colunas: {list(self.df_original.columns)}")
            return self.df_original
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            return None
    
    def executar_pipeline_completo(self, filepath, incluir_tfidf=False, estrategia_balanceamento='auto'):
        """
        Executa o pipeline completo de processamento
        
        Args:
            filepath: Caminho para o arquivo CSV
            incluir_tfidf: Se incluir features TF-IDF (lento)
            estrategia_balanceamento: Estratégia de balanceamento
        """
        print("🚀 INICIANDO PIPELINE COMPLETO DE CLASSIFICAÇÃO DE VIABILIDADE")
        print("=" * 80)
        
        # 1. Carregar dados
        if self.carregar_dados(filepath) is None:
            return None
        
        # 2. Preprocessamento
        print("\n" + "🔄 ETAPA 1: PREPROCESSAMENTO")
        self.df_preprocessado = preprocessar_dados(self.df_original)
        self.resultados['preprocessamento'] = {
            'linhas_originais': len(self.df_original),
            'linhas_processadas': len(self.df_preprocessado)
        }
        
        # 3. Análise exploratória
        print("\n" + "🔄 ETAPA 2: ANÁLISE EXPLORATÓRIA")
        analyzer, analise_resultados = executar_etapa_1(self.df_preprocessado)
        self.resultados['analise_exploratoria'] = analise_resultados
        
        # 4. Criação do target
        print("\n" + "🔄 ETAPA 3: CRIAÇÃO DO TARGET")
        target_creator, self.df_com_target, analise_target = executar_etapa_2(self.df_preprocessado)
        self.resultados['criacao_target'] = analise_target
        
        # 5. Feature engineering
        print("\n" + "🔄 ETAPA 4: FEATURE ENGINEERING")
        self.df_features = executar_feature_engineering(
            self.df_com_target, 
            incluir_tfidf=incluir_tfidf
        )
        self.resultados['feature_engineering'] = {
            'features_originais': self.df_com_target.shape[1],
            'features_criadas': self.df_features.shape[1],
            'linhas': self.df_features.shape[0]
        }
        
        # 6. Balanceamento de dados
        print("\n" + "🔄 ETAPA 5: BALANCEAMENTO DE DADOS")
        self.X_balanced, self.y_balanced, self.feature_names, balancer = balancear_dados_viabilidade(
            self.df_features,
            strategy=estrategia_balanceamento
        )
        self.resultados['balanceamento'] = {
            'amostras_originais': len(self.df_features),
            'amostras_balanceadas': len(self.y_balanced),
            'features_usadas': len(self.feature_names)
        }
        
        # 7. Salvar resultados
        self.salvar_resultados()
        
        # 8. Resumo final
        self.imprimir_resumo_final()
        
        return {
            'X_balanced': self.X_balanced,
            'y_balanced': self.y_balanced,
            'feature_names': self.feature_names,
            'df_features': self.df_features,
            'df_com_target': self.df_com_target,
            'resultados': self.resultados
        }
    
    def salvar_resultados(self):
        """
        Salva os DataFrames processados
        """
        print("\n" + "💾 SALVANDO RESULTADOS")
        print("-" * 25)
        
        try:
            # DataFrame preprocessado
            self.df_preprocessado.to_csv('dados_preprocessados.csv', index=False, encoding='utf-8')
            print("✅ dados_preprocessados.csv salvo")
            
            # DataFrame com target
            self.df_com_target.to_csv('dados_com_target.csv', index=False, encoding='utf-8')
            print("✅ dados_com_target.csv salvo")
            
            # DataFrame com features
            self.df_features.to_csv('dados_com_features.csv', index=False, encoding='utf-8')
            print("✅ dados_com_features.csv salvo")
            
            # Dados balanceados
            df_balanced = pd.DataFrame(self.X_balanced, columns=self.feature_names)
            df_balanced['target'] = self.y_balanced
            df_balanced.to_csv('dados_balanceados.csv', index=False, encoding='utf-8')
            print("✅ dados_balanceados.csv salvo")
            
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
    
    def imprimir_resumo_final(self):
        """
        Imprime resumo final do pipeline
        """
        print("\n" + "=" * 80)
        print("📊 RESUMO FINAL DO PIPELINE")
        print("=" * 80)
        
        print(f"1️⃣ DADOS ORIGINAIS:")
        print(f"   Linhas: {self.resultados['preprocessamento']['linhas_originais']:,}")
        
        print(f"\n2️⃣ APÓS PREPROCESSAMENTO:")
        print(f"   Linhas: {self.resultados['preprocessamento']['linhas_processadas']:,}")
        
        print(f"\n3️⃣ ANÁLISE EXPLORATÓRIA:")
        stats = self.resultados['analise_exploratoria']['stats_basicas']
        print(f"   Assuntos únicos: {stats['assuntos_unicos']:,}")
        print(f"   Problemas únicos: {stats['problemas_unicos']:,}")
        print(f"   Taxa de sucesso: {stats['taxa_sucesso']:.1%}")
        print(f"   Valor médio: R$ {stats['valor_medio']:,.2f}")
        
        print(f"\n4️⃣ TARGET CRIADO:")
        dist = self.resultados['criacao_target']['distribuicao_target']
        for classe, prop in dist.items():
            print(f"   {classe}: {prop:.1%}")
        
        print(f"\n5️⃣ FEATURE ENGINEERING:")
        fe_stats = self.resultados['feature_engineering']
        print(f"   Features criadas: {fe_stats['features_criadas'] - fe_stats['features_originais']}")
        print(f"   Total de features: {fe_stats['features_criadas']}")
        
        print(f"\n6️⃣ BALANCEAMENTO:")
        bal_stats = self.resultados['balanceamento']
        print(f"   Amostras originais: {bal_stats['amostras_originais']:,}")
        print(f"   Amostras balanceadas: {bal_stats['amostras_balanceadas']:,}")
        print(f"   Features para ML: {bal_stats['features_usadas']}")
        
        print(f"\n🎯 DADOS PRONTOS PARA MACHINE LEARNING!")
        print(f"   Shape X: {self.X_balanced.shape}")
        print(f"   Shape y: {self.y_balanced.shape}")
        
        print(f"\n📁 ARQUIVOS SALVOS:")
        print(f"   - dados_preprocessados.csv")
        print(f"   - dados_com_target.csv") 
        print(f"   - dados_com_features.csv")
        print(f"   - dados_balanceados.csv")


def main():
    """
    Função principal para execução via linha de comando
    """
    if len(sys.argv) < 2:
        print("❌ Uso: python main.py <caminho_arquivo_csv> [--tfidf] [--strategy estrategia]")
        print("\nExemplo:")
        print("python main.py dados_sindec.csv")
        print("python main.py dados_sindec.csv --tfidf --strategy moderate")
        print("\nEstratégias disponíveis: auto, conservative, moderate, aggressive")
        return
    
    # Argumentos
    filepath = sys.argv[1]
    incluir_tfidf = '--tfidf' in sys.argv
    
    # Estratégia de balanceamento
    estrategia = 'auto'
    if '--strategy' in sys.argv:
        try:
            idx = sys.argv.index('--strategy')
            estrategia = sys.argv[idx + 1]
        except (IndexError, ValueError):
            print("⚠️ Estratégia inválida, usando 'auto'")
    
    # Executa pipeline
    pipeline = ViabilidadeClassificationPipeline()
    resultados = pipeline.executar_pipeline_completo(
        filepath, 
        incluir_tfidf=incluir_tfidf,
        estrategia_balanceamento=estrategia
    )
    
    if resultados:
        print("\n✅ Pipeline executado com sucesso!")
        print("Os dados estão prontos para treinamento de modelos de ML")
    else:
        print("\n❌ Erro na execução do pipeline")


if __name__ == "__main__":
    main()