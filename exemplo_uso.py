"""
Exemplo de uso do sistema de análise SINDEC
"""

from main import SindecProcessor
from valor_estimator import ValorCausaEstimatorBackup
from analyzer import ViabilityChecker


def exemplo_basico():
    """Exemplo básico de uso do sistema"""
    
    print("🎯 EXEMPLO BÁSICO DE USO DO SISTEMA SINDEC")
    print("="*50)
    
    # 1. Análise de viabilidade individual
    print("\n📋 1. ANÁLISE DE VIABILIDADE INDIVIDUAL")
    print("-" * 30)
    
    checker = ViabilityChecker()
    
    casos_exemplo = [
        {
            "valor": 5000,
            "assunto": "Energia Elétrica",
            "problema": "Cobrança Indevida", 
            "regiao": "Sudeste",
            "uf": "SP"
        },
        {
            "valor": 1500,
            "assunto": "Telefonia Celular",
            "problema": "Interrupção do Serviço",
            "regiao": "Nordeste", 
            "uf": "CE"
        },
        {
            "valor": 8000,
            "assunto": "Banco comercial",
            "problema": "Cobrança indevida",
            "regiao": "Sul",
            "uf": "RS"
        }
    ]
    
    for i, caso in enumerate(casos_exemplo, 1):
        print(f"\n🔍 Caso {i}: {caso['assunto']} - {caso['problema']}")
        print(f"💰 Valor: R$ {caso['valor']:,.2f} | 📍 {caso['regiao']}/{caso['uf']}")
        
        resultado = checker.analisar_viabilidade(
            valor=caso['valor'],
            tipo_assunto=caso['assunto'],
            problema=caso['problema'],
            regiao=caso['regiao'],
            uf=caso['uf']
        )
        
        print(f"📊 Status: {resultado['status']}")
        print(f"🎯 Recomendação: {resultado['recomendacao']}")
        print(f"📈 Probabilidade Viável: {resultado['probabilidade_viavel']:.1%}")


def exemplo_estimativa_valores():
    """Exemplo de estimativa de valores"""
    
    print("\n💰 2. ESTIMATIVA DE VALORES DE CAUSA")
    print("-" * 30)
    
    estimador = ValorCausaEstimatorBackup()
    
    casos_estimativa = [
        {
            "assunto": "Cartão de Crédito",
            "problema": "Anuidade cobrada indevidamente",
            "uf": "SP",
            "ano": 2021
        },
        {
            "assunto": "Internet banda larga",
            "problema": "Velocidade inferior à contratada",
            "uf": "RJ",
            "ano": 2020
        },
        {
            "assunto": "Compra online",
            "problema": "Produto não entregue no prazo",
            "uf": "MG", 
            "ano": 2021
        }
    ]
    
    for i, caso in enumerate(casos_estimativa, 1):
        print(f"\n🔍 Estimativa {i}: {caso['assunto']}")
        print(f"📝 Problema: {caso['problema']}")
        print(f"📍 {caso['uf']}/{caso['ano']}")
        
        estimativa = estimador.estimar_valor_causa(
            descricao_assunto=caso['assunto'],
            descricao_problema=caso['problema'],
            uf=caso['uf'],
            ano=caso['ano']
        )
        
        print(f"💰 Valor estimado: R$ {estimativa['valor_estimado']:,.2f}")
        print(f"📊 Faixa: R$ {estimativa['valor_minimo']:,.2f} - R$ {estimativa['valor_maximo']:,.2f}")
        print(f"🎯 Confiança: {estimativa['confianca']:.2f}")
        print(f"📂 Categoria: {estimativa['categoria']}")


def exemplo_processamento_arquivo():
    """Exemplo de processamento de arquivo completo"""
    
    print("\n📁 3. PROCESSAMENTO DE ARQUIVO (EXEMPLO)")
    print("-" * 30)
    
    print("🔧 Para processar um arquivo SINDEC completo:")
    print()
    print("```python")
    print("from main import SindecProcessor")
    print()
    print("# Inicializa processador")
    print("processor = SindecProcessor(api_key='SUA_API_KEY_DATAJUD')  # Opcional")
    print()
    print("# Processa arquivo")
    print("df_resultado = processor.processar_completo('PROCON_2017_21.csv')")
    print()
    print("# Ou sem API DataJud:")
    print("processor = SindecProcessor()  # Só estimativas históricas")
    print("df_resultado = processor.processar_completo('seu_arquivo.csv')")
    print("```")
    print()
    print("📄 Arquivos gerados:")
    print("   - SINDEC_com_valores_causa.csv (dados completos)")
    print("   - SINDEC_resumo_por_assunto.csv (resumo estatístico)")


def exemplo_configuracao_api():
    """Exemplo de configuração da API DataJud"""
    
    print("\n🌐 4. CONFIGURAÇÃO API DATAJUD (OPCIONAL)")
    print("-" * 30)
    
    print("🔑 Para usar a API DataJud do CNJ:")
    print()
    print("1. Acesse: https://www.cnj.jus.br/sistemas/datajud/api-publica/")
    print("2. Registre-se e obtenha sua chave API")
    print("3. Configure no código:")
    print()
    print("```python")
    print("# Em main.py, linha ~XX:")
    print("API_KEY = 'cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=='")
    print()
    print("# Ou diretamente:")
    print("processor = SindecProcessor(api_key='sua_chave_aqui')")
    print("```")
    print()
    print("⚠️ Sem API Key: Sistema funciona com estimativas históricas")
    print("✅ Com API Key: Busca valores reais de processos do TJSP")


def main():
    """Executa todos os exemplos"""
    
    try:
        exemplo_basico()
        exemplo_estimativa_valores()
        exemplo_processamento_arquivo()
        exemplo_configuracao_api()
        
        print("\n" + "="*60)
        print("✅ EXEMPLOS EXECUTADOS COM SUCESSO!")
        print("="*60)
        print("📚 Consulte o README.md para mais informações")
        print("🚀 Execute 'python main.py' para processar seus dados")
        
    except Exception as e:
        print(f"\n❌ Erro durante execução dos exemplos: {e}")


if __name__ == "__main__":
    main()