"""
Funções utilitárias para o sistema de classificação de viabilidade jurídica.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime


def debug_dataframe(df, nome="DataFrame"):
    """
    Função de debug para verificar o DataFrame
    """
    print(f"🔍 DEBUG DO {nome.upper()}:")
    print(f"Shape: {df.shape}")
    print(f"Colunas: {list(df.columns)}")
    print(f"Tipos de dados:")
    print(df.dtypes.value_counts())
    print(f"Valores nulos por coluna:")
    print(df.isnull().sum()[df.isnull().sum() > 0])
    print(f"Memória utilizada: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")


def verificar_colunas_necessarias(df, colunas_necessarias):
    """
    Verifica se as colunas necessárias existem no DataFrame
    """
    print("🔍 VERIFICANDO COLUNAS NECESSÁRIAS:")
    
    colunas_faltando = []
    for col in colunas_necessarias:
        if col in df.columns:
            print(f"✅ {col}: OK ({df[col].dtype})")
        else:
            print(f"❌ {col}: FALTANDO")
            colunas_faltando.append(col)
    
    if colunas_faltando:
        print(f"\n⚠️ {len(colunas_faltando)} colunas faltando: {colunas_faltando}")
        return False
    else:
        print(f"\n✅ Todas as {len(colunas_necessarias)} colunas necessárias estão presentes")
        return True


def criar_relatorio_qualidade_dados(df, nome_arquivo="relatorio_qualidade.txt"):
    """
    Cria relatório de qualidade dos dados
    """
    print(f"📊 GERANDO RELATÓRIO DE QUALIDADE DOS DADOS")
    
    relatorio = []
    relatorio.append("=" * 80)
    relatorio.append("RELATÓRIO DE QUALIDADE DOS DADOS")
    relatorio.append("=" * 80)
    relatorio.append(f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    relatorio.append("")
    
    # Informações básicas
    relatorio.append("📊 INFORMAÇÕES BÁSICAS:")
    relatorio.append(f"   Linhas: {df.shape[0]:,}")
    relatorio.append(f"   Colunas: {df.shape[1]:,}")
    relatorio.append(f"   Memória: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    relatorio.append("")
    
    # Tipos de dados
    relatorio.append("🏷️ TIPOS DE DADOS:")
    for dtype, count in df.dtypes.value_counts().items():
        relatorio.append(f"   {dtype}: {count} colunas")
    relatorio.append("")
    
    # Valores nulos
    nulos = df.isnull().sum()
    nulos_com_valores = nulos[nulos > 0]
    
    relatorio.append("❌ VALORES NULOS:")
    if len(nulos_com_valores) == 0:
        relatorio.append("   ✅ Nenhum valor nulo encontrado")
    else:
        for col, count in nulos_com_valores.items():
            percentage = (count / len(df)) * 100
            relatorio.append(f"   {col}: {count:,} ({percentage:.1f}%)")
    relatorio.append("")
    
    # Duplicatas
    duplicatas = df.duplicated().sum()
    relatorio.append("🔄 DUPLICATAS:")
    relatorio.append(f"   Total: {duplicatas:,} ({duplicatas/len(df)*100:.1f}%)")
    relatorio.append("")
    
    # Colunas numéricas
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        relatorio.append("🔢 ESTATÍSTICAS NUMÉRICAS:")
        for col in numeric_cols[:10]:  # Apenas primeiras 10
            relatorio.append(f"   {col}:")
            relatorio.append(f"     Média: {df[col].mean():.2f}")
            relatorio.append(f"     Mediana: {df[col].median():.2f}")
            relatorio.append(f"     Min: {df[col].min():.2f}")
            relatorio.append(f"     Max: {df[col].max():.2f}")
            relatorio.append("")
    
    # Salvar relatório
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write('\n'.join(relatorio))
    
    print(f"✅ Relatório salvo em: {nome_arquivo}")
    return relatorio


def plotar_distribuicao_target(y, target_names=None, titulo="Distribuição do Target"):
    """
    Plota distribuição da variável target
    """
    plt.figure(figsize=(12, 5))
    
    # Subplot 1: Contagem
    plt.subplot(1, 2, 1)
    counts = pd.Series(y).value_counts().sort_index()
    
    if target_names:
        labels = [target_names.get(i, f"Classe {i}") for i in counts.index]
    else:
        labels = [f"Classe {i}" for i in counts.index]
    
    bars = plt.bar(range(len(counts)), counts.values, color=['#ff6b6b', '#4ecdc4'])
    plt.title(f'{titulo} - Contagem')
    plt.ylabel('Quantidade')
    plt.xticks(range(len(counts)), labels)
    
    # Adiciona valores nas barras
    for bar, value in zip(bars, counts.values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(counts)*0.01,
                f'{value:,}', ha='center', va='bottom')
    
    # Subplot 2: Percentual
    plt.subplot(1, 2, 2)
    plt.pie(counts.values, labels=labels, autopct='%1.1f%%', startangle=90,
            colors=['#ff6b6b', '#4ecdc4'])
    plt.title(f'{titulo} - Percentual')
    
    plt.tight_layout()
    plt.show()


def criar_matriz_correlacao(df, figsize=(12, 10), limite_colunas=30):
    """
    Cria matriz de correlação para colunas numéricas
    """
    # Seleciona apenas colunas numéricas
    numeric_df = df.select_dtypes(include=[np.number])
    
    # Limita número de colunas se muito grande
    if len(numeric_df.columns) > limite_colunas:
        print(f"⚠️ Muitas colunas ({len(numeric_df.columns)}). Mostrando apenas as primeiras {limite_colunas}")
        numeric_df = numeric_df.iloc[:, :limite_colunas]
    
    # Calcula correlação
    corr_matrix = numeric_df.corr()
    
    # Plota
    plt.figure(figsize=figsize)
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', center=0,
                square=True, fmt='.2f', cbar_kws={"shrink": .8})
    plt.title('Matriz de Correlação')
    plt.tight_layout()
    plt.show()
    
    return corr_matrix


def salvar_dataframe_com_info(df, nome_arquivo, incluir_info=True):
    """
    Salva DataFrame com informações adicionais
    """
    print(f"💾 SALVANDO: {nome_arquivo}")
    
    # Salva o DataFrame principal
    df.to_csv(nome_arquivo, index=False, encoding='utf-8')
    
    if incluir_info:
        # Cria arquivo de informações
        info_filename = nome_arquivo.replace('.csv', '_info.txt')
        
        with open(info_filename, 'w', encoding='utf-8') as f:
            f.write(f"INFORMAÇÕES DO ARQUIVO: {nome_arquivo}\n")
            f.write("=" * 50 + "\n")
            f.write(f"Data de criação: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Shape: {df.shape}\n")
            f.write(f"Memória: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB\n\n")
            
            f.write("COLUNAS:\n")
            for i, col in enumerate(df.columns, 1):
                f.write(f"{i:3d}. {col} ({df[col].dtype})\n")
            
            f.write(f"\nVALORES NULOS:\n")
            nulos = df.isnull().sum()
            nulos_com_valores = nulos[nulos > 0]
            if len(nulos_com_valores) == 0:
                f.write("Nenhum valor nulo encontrado\n")
            else:
                for col, count in nulos_com_valores.items():
                    f.write(f"{col}: {count:,}\n")
        
        print(f"✅ Arquivo principal: {nome_arquivo}")
        print(f"✅ Arquivo de info: {info_filename}")
    else:
        print(f"✅ Salvo: {nome_arquivo}")


def validar_pipeline_input(df, etapa):
    """
    Valida entrada para cada etapa do pipeline
    """
    validacoes = {
        'preprocessamento': ['Atendida', 'ValorCausa'],
        'analise_exploratoria': ['DescricaoAssunto', 'DescricaoProblema', 'ValorCausa', 'Atendida'],
        'criacao_target': ['DescricaoAssunto', 'DescricaoProblema', 'ValorCausa', 'Atendida', 'ValorCausaConfianca'],
        'feature_engineering': ['DescricaoAssunto', 'DescricaoProblema', 'Viavel'],
        'balanceamento': ['Viavel']
    }
    
    if etapa not in validacoes:
        print(f"⚠️ Etapa '{etapa}' não reconhecida")
        return True
    
    colunas_necessarias = validacoes[etapa]
    return verificar_colunas_necessarias(df, colunas_necessarias)


def imprimir_estatisticas_resumidas(df, nome="Dataset"):
    """
    Imprime estatísticas resumidas do DataFrame
    """
    print(f"\n📊 ESTATÍSTICAS - {nome.upper()}")
    print("-" * 50)
    print(f"Shape: {df.shape}")
    print(f"Memória: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    # Tipos de dados
    print(f"\nTipos de dados:")
    for dtype, count in df.dtypes.value_counts().items():
        print(f"  {dtype}: {count}")
    
    # Valores nulos
    nulos = df.isnull().sum().sum()
    if nulos > 0:
        print(f"\nValores nulos: {nulos:,} ({nulos/(df.shape[0]*df.shape[1])*100:.1f}%)")
    else:
        print(f"\n✅ Sem valores nulos")
    
    # Se tem target, mostra distribuição
    if 'Viavel' in df.columns:
        print(f"\nDistribuição do target:")
        dist = df['Viavel'].value_counts()
        for valor, count in dist.items():
            label = 'VIÁVEL' if valor == 1 else 'NÃO VIÁVEL'
            print(f"  {label}: {count:,} ({count/len(df)*100:.1f}%)")