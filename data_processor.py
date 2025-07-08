"""
Processador de dados SINDEC
"""

import pandas as pd
import numpy as np
from config import FILE_ENCODING_INPUT, CSV_SEPARATOR_INPUT, FILE_ENCODING_OUTPUT


class DataProcessor:
    """Classe para processamento de dados SINDEC"""
    
    def __init__(self):
        self.df = None
    
    def load_sindec_data(self, file_path: str) -> pd.DataFrame:
        """
        Carrega dados do arquivo SINDEC
        
        Args:
            file_path: Caminho para o arquivo CSV
            
        Returns:
            DataFrame com os dados carregados
        """
        print(f"📊 Carregando dados de {file_path}")
        
        try:
            self.df = pd.read_csv(
                file_path, 
                sep=CSV_SEPARATOR_INPUT, 
                encoding=FILE_ENCODING_INPUT, 
                on_bad_lines='skip'
            )
            
            print(f"✅ Dados carregados: {len(self.df):,} registros")
            return self.df
            
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            raise
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpa os dados removendo registros com CodigoProblema nulo
        
        Args:
            df: DataFrame a ser limpo
            
        Returns:
            DataFrame limpo
        """
        print("🧹 Limpando dados...")
        
        initial_count = len(df)
        
        # Remove registros sem CodigoProblema
        df_clean = df.dropna(subset=['CodigoProblema']).copy()
        
        final_count = len(df_clean)
        removed_count = initial_count - final_count
        
        print(f"✅ Limpeza concluída:")
        print(f"   📊 Registros iniciais: {initial_count:,}")
        print(f"   🗑️ Registros removidos: {removed_count:,}")
        print(f"   ✅ Registros finais: {final_count:,}")
        
        return df_clean
    
    def remove_empty_records(self, df: pd.DataFrame, num_columns: int = 15) -> pd.DataFrame:
        """
        Remove registros onde as primeiras N colunas são todas nulas
        
        Args:
            df: DataFrame a ser processado
            num_columns: Número de colunas a verificar
            
        Returns:
            DataFrame filtrado
        """
        print(f"🧹 Removendo registros com {num_columns} primeiras colunas nulas...")
        
        primeiras_colunas = df.columns[:num_columns]
        mascara_nulos = df[primeiras_colunas].isnull().all(axis=1)
        
        registros_nulos = mascara_nulos.sum()
        df_filtrado = df[~mascara_nulos].copy()
        
        print(f"✅ Registros removidos: {registros_nulos:,}")
        print(f"📊 Registros restantes: {len(df_filtrado):,}")
        
        return df_filtrado
    
    def save_results(self, df: pd.DataFrame, filename: str):
        """
        Salva o DataFrame em arquivo CSV
        
        Args:
            df: DataFrame a ser salvo
            filename: Nome do arquivo de saída
        """
        try:
            df.to_csv(filename, index=False, encoding=FILE_ENCODING_OUTPUT)
            print(f"✅ Arquivo salvo: {filename}")
            
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo {filename}: {e}")
            raise
    
    def create_summary_report(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cria relatório resumo por assunto
        
        Args:
            df: DataFrame com dados processados
            
        Returns:
            DataFrame com resumo por assunto
        """
        print("📊 Criando relatório resumo...")
        
        try:
            resumo = df.groupby('DescricaoAssunto').agg({
                'ValorCausa': ['count', 'mean', 'median', 'std', 'min', 'max', 'sum'],
                'ValorCausaConfianca': 'mean'
            }).round(2)
            
            resumo.columns = [
                'Quantidade', 'Valor_Medio', 'Valor_Mediano', 'Desvio_Padrao',
                'Valor_Minimo', 'Valor_Maximo', 'Valor_Total', 'Confianca_Media'
            ]
            
            resumo = resumo.sort_values('Valor_Total', ascending=False)
            
            print(f"✅ Resumo criado com {len(resumo)} assuntos")
            return resumo
            
        except Exception as e:
            print(f"❌ Erro ao criar resumo: {e}")
            raise
    
    def print_data_info(self, df: pd.DataFrame, title: str = "INFORMAÇÕES DOS DADOS"):
        """
        Imprime informações básicas do DataFrame
        
        Args:
            df: DataFrame a analisar
            title: Título da seção
        """
        print(f"\n{'='*60}")
        print(f"📊 {title}")
        print(f"{'='*60}")
        
        print(f"📈 Total de registros: {len(df):,}")
        print(f"📋 Total de colunas: {len(df.columns)}")
        
        if 'ValorCausa' in df.columns:
            valores = df['ValorCausa'].dropna()
            if len(valores) > 0:
                print(f"\n💰 VALORES:")
                print(f"   Registros com valor: {len(valores):,}")
                print(f"   Soma total: R$ {valores.sum():,.2f}")
                print(f"   Valor médio: R$ {valores.mean():,.2f}")
                print(f"   Valor mediano: R$ {valores.median():,.2f}")
        
        # Top 5 assuntos
        if 'DescricaoAssunto' in df.columns:
            print(f"\n📋 TOP 5 ASSUNTOS:")
            top_assuntos = df['DescricaoAssunto'].value_counts().head()
            for assunto, count in top_assuntos.items():
                print(f"   {assunto[:50]}...: {count:,}")