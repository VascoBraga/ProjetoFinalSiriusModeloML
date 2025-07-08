"""
Script de setup para o Sistema de Classificação de Viabilidade de Causas Jurídicas.
"""

import os
import sys
import subprocess
from pathlib import Path


def verificar_python():
    """Verifica versão do Python"""
    print("🐍 VERIFICANDO VERSÃO DO PYTHON...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} detectado.")
        print("✅ Este projeto requer Python 3.8 ou superior.")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
    return True


def instalar_dependencias():
    """Instala as dependências do requirements.txt"""
    print("\n📦 INSTALANDO DEPENDÊNCIAS...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, capture_output=True, text=True)
        print("✅ Dependências instaladas com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        print("Tente instalar manualmente:")
        print("pip install -r requirements.txt")
        return False


def verificar_imports():
    """Verifica se os imports principais funcionam"""
    print("\n🔍 VERIFICANDO IMPORTS...")
    
    imports_para_testar = [
        ("pandas", "pd"),
        ("numpy", "np"),
        ("sklearn", "sklearn"),
        ("matplotlib.pyplot", "plt"),
        ("seaborn", "sns"),
        ("imblearn", "imblearn")
    ]
    
    imports_com_erro = []
    
    for modulo, alias in imports_para_testar:
        try:
            __import__(modulo)
            print(f"✅ {modulo}")
        except ImportError:
            print(f"❌ {modulo}")
            imports_com_erro.append(modulo)
    
    if imports_com_erro:
        print(f"\n⚠️ {len(imports_com_erro)} módulos com problema:")
        for modulo in imports_com_erro:
            print(f"   - {modulo}")
        return False
    
    print("✅ Todos os imports funcionando")
    return True


def verificar_estrutura_arquivos():
    """Verifica se todos os arquivos necessários estão presentes"""
    print("\n📁 VERIFICANDO ESTRUTURA DE ARQUIVOS...")
    
    arquivos_necessarios = [
        "config.py",
        "data_preprocessing.py", 
        "exploratory_analysis.py",
        "target_creation.py",
        "feature_engineering.py",
        "data_balancing.py",
        "utils.py",
        "main.py",
        "requirements.txt",
        "README.md",
        "__init__.py",
        "exemplo_uso.py"
    ]
    
    arquivos_faltando = []
    
    for arquivo in arquivos_necessarios:
        if Path(arquivo).exists():
            print(f"✅ {arquivo}")
        else:
            print(f"❌ {arquivo}")
            arquivos_faltando.append(arquivo)
    
    if arquivos_faltando:
        print(f"\n⚠️ {len(arquivos_faltando)} arquivos faltando:")
        for arquivo in arquivos_faltando:
            print(f"   - {arquivo}")
        return False
    
    print("✅ Todos os arquivos presentes")
    return True


def criar_diretorios():
    """Cria diretórios necessários"""
    print("\n📂 CRIANDO DIRETÓRIOS...")
    
    diretorios = [
        "data",      # Para dados de entrada
        "output",    # Para resultados
        "models",    # Para modelos treinados
        "reports",   # Para relatórios
        "logs"       # Para logs
    ]
    
    for diretorio in diretorios:
        Path(diretorio).mkdir(exist_ok=True)
        print(f"✅ {diretorio}/")
    
    # Cria arquivos .gitkeep para manter diretórios no git
    for diretorio in diretorios:
        gitkeep_file = Path(diretorio) / ".gitkeep"
        if not gitkeep_file.exists():
            gitkeep_file.touch()


def testar_imports_modulos():
    """Testa imports dos módulos do projeto"""
    print("\n🧪 TESTANDO IMPORTS DOS MÓDULOS...")
    
    modulos_projeto = [
        "config",
        "data_preprocessing", 
        "exploratory_analysis",
        "target_creation",
        "feature_engineering",
        "data_balancing",
        "utils",
        "main"
    ]
    
    imports_com_erro = []
    
    for modulo in modulos_projeto:
        try:
            __import__(modulo)
            print(f"✅ {modulo}")
        except ImportError as e:
            print(f"❌ {modulo}: {e}")
            imports_com_erro.append(modulo)
    
    if imports_com_erro:
        print(f"\n⚠️ Problemas nos módulos:")
        for modulo in imports_com_erro:
            print(f"   - {modulo}")
        return False
    
    print("✅ Todos os módulos importando corretamente")
    return True


def criar_arquivo_exemplo():
    """Cria arquivo de dados de exemplo para teste"""
    print("\n📄 CRIANDO ARQUIVO DE DADOS DE EXEMPLO...")
    
    try:
        import pandas as pd
        import numpy as np
        
        # Cria dados de exemplo mínimos
        np.random.seed(42)
        
        dados_exemplo = {
            'AnoCalendario': [2020] * 1000,
            'Regiao': np.random.choice(['Sudeste', 'Sul', 'Centro-oeste', 'Nordeste', 'Norte'], 1000),
            'UF': np.random.choice(['SP', 'RJ', 'MG', 'RS', 'PR', 'DF', 'GO'], 1000),
            'DescricaoAssunto': np.random.choice([
                'Telefone Celular',
                'Cartão de Crédito', 
                'Banco Comercial',
                'TV Por Assinatura',
                'Internet'
            ], 1000),
            'DescricaoProblema': np.random.choice([
                'Cobrança indevida',
                'Produto defeituoso',
                'Atendimento',
                'Cancelamento',
                'Negativação'
            ], 1000),
            'ValorCausa': np.random.lognormal(7.5, 0.5, 1000),
            'ValorCausaConfianca': np.random.uniform(0.5, 0.9, 1000),
            'Atendida': np.random.choice(['S', 'N'], 1000, p=[0.6, 0.4]),
            'SexoConsumidor': np.random.choice(['M', 'F'], 1000),
            'FaixaEtariaConsumidor': np.random.choice([
                'até 20 anos', '21 a 30 anos', '31 a 40 anos', 
                '41 a 50 anos', '51 a 60 anos', 'mais de 60 anos'
            ], 1000)
        }
        
        df_exemplo = pd.DataFrame(dados_exemplo)
        df_exemplo.to_csv('data/dados_exemplo.csv', index=False)
        print("✅ data/dados_exemplo.csv criado")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar dados de exemplo: {e}")
        return False


def main():
    """Função principal do setup"""
    print("🚀 SETUP DO SISTEMA DE VIABILIDADE JURÍDICA")
    print("=" * 60)
    
    etapas = [
        ("Verificar Python", verificar_python),
        ("Verificar estrutura", verificar_estrutura_arquivos),
        ("Instalar dependências", instalar_dependencias),
        ("Verificar imports", verificar_imports),
        ("Criar diretórios", criar_diretorios),
        ("Testar módulos", testar_imports_modulos),
        ("Criar dados exemplo", criar_arquivo_exemplo)
    ]
    
    resultados = []
    
    for nome, funcao in etapas:
        print(f"\n{'='*20} {nome.upper()} {'='*20}")
        try:
            resultado = funcao()
            resultados.append((nome, resultado))
        except Exception as e:
            print(f"❌ Erro inesperado em {nome}: {e}")
            resultados.append((nome, False))
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📊 RESUMO DO SETUP")
    print("=" * 60)
    
    sucessos = 0
    for nome, resultado in resultados:
        status = "✅" if resultado else "❌"
        print(f"{status} {nome}")
        if resultado:
            sucessos += 1
    
    print(f"\n🎯 RESULTADO: {sucessos}/{len(etapas)} etapas concluídas com sucesso")
    
    if sucessos == len(etapas):
        print("\n🎉 SETUP CONCLUÍDO COM SUCESSO!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Execute: python exemplo_uso.py")
        print("2. Ou teste com: python main.py data/dados_exemplo.csv")
        print("3. Para dados reais, substitua o CSV em data/")
    else:
        print("\n⚠️ SETUP INCOMPLETO")
        print("Verifique os erros acima e tente novamente.")
        print("Para ajuda, consulte o README.md")
    
    return sucessos == len(etapas)


if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1)