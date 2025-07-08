"""
Exemplo de uso do algoritmo de classificação SINDEC - Parte 3
"""

import pandas as pd
import numpy as np
from main import (
    executar_pipeline_completo, 
    executar_pipeline_simples,
    salvar_modelo_final,
    carregar_modelo_final,
    fazer_predicao
)


def exemplo_pipeline_completo():
    """Exemplo de uso do pipeline completo"""
    print("=" * 60)
    print("EXEMPLO 1: PIPELINE COMPLETO")
    print("=" * 60)
    
    # Simula dados (substitua pela carga real dos seus dados)
    print("📊 Carregando dados...")
    # df_com_target = pd.read_csv('seus_dados_com_target.csv')
    
    # Para demonstração, vamos assumir que você tem os dados
    print("⚠️  Substitua esta linha pela carga real dos seus dados:")
    print("    df_com_target = pd.read_csv('seus_dados_com_target.csv')")
    
    print("\n🚀 Para executar o pipeline completo:")
    print("""
    # Executa pipeline completo com análise detalhada
    resultados = executar_pipeline_completo(
        df_com_target,
        strategy='moderate',      # ou 'conservative', 'aggressive', 'auto'
        run_analysis=True         # inclui análise comparativa
    )
    
    if resultados:
        # Acessa o melhor modelo
        melhor_modelo = resultados['best_model']['model']
        nome_modelo = resultados['best_model']['name']
        score = resultados['best_model']['score']
        
        print(f"✅ Melhor modelo: {nome_modelo} (AUC: {score:.3f})")
        
        # Acessa dados processados
        df_balanceado = resultados['data']['df_balanced']
        feature_names = resultados['data']['feature_names']
        
        # Salva modelo para uso futuro
        salvar_modelo_final(melhor_modelo, feature_names, 'modelo_final.pkl')
    """)


def exemplo_pipeline_simples():
    """Exemplo de uso do pipeline simplificado"""
    print("\n" + "=" * 60)
    print("EXEMPLO 2: PIPELINE SIMPLIFICADO (MAIS RÁPIDO)")
    print("=" * 60)
    
    print("⚡ Para execução mais rápida sem análise detalhada:")
    print("""
    # Pipeline simplificado
    resultados = executar_pipeline_simples(
        df_com_target,
        strategy='moderate'
    )
    
    if resultados:
        melhor_modelo = resultados['best_model']
        nome_modelo = resultados['best_model_name']
        score = resultados['best_score']
        
        print(f"✅ Modelo treinado: {nome_modelo} (AUC: {score:.3f})")
        
        # Dados para validação
        X_test = resultados['X_test']
        y_test = resultados['y_test']
        feature_names = resultados['feature_names']
        
        # Salva modelo
        salvar_modelo_final(melhor_modelo, feature_names)
    """)


def exemplo_uso_modular():
    """Exemplo de uso modular dos componentes"""
    print("\n" + "=" * 60)
    print("EXEMPLO 3: USO MODULAR")
    print("=" * 60)
    
    print("🔧 Para usar componentes individuais:")
    print("""
    # Apenas balanceamento
    from balancing import aplicar_balanceamento_sindec
    df_balanced, results = aplicar_balanceamento_sindec(
        df_com_target,
        strategy='moderate',
        run_analysis=False  # mais rápido
    )
    
    # Apenas treinamento com dados limpos
    from model_training import treinar_modelo_limpo, selecionar_melhor_modelo
    model_results, X_train, X_test, y_train, y_test, features = treinar_modelo_limpo(df_balanced)
    
    if model_results:
        nome_melhor, melhor_modelo, melhor_score = selecionar_melhor_modelo(model_results)
        print(f"Melhor modelo: {nome_melhor}")
    
    # Apenas criação de features limpas
    from clean_features import preparar_dados_limpos
    X_clean, y_clean, feature_names = preparar_dados_limpos(df_balanced)
    """)


def exemplo_salvar_carregar_modelo():
    """Exemplo de como salvar e carregar modelos"""
    print("\n" + "=" * 60)
    print("EXEMPLO 4: SALVAR E CARREGAR MODELOS")
    print("=" * 60)
    
    print("💾 Salvando e carregando modelos:")
    print("""
    # Salvar modelo após treinamento
    salvar_modelo_final(
        modelo=melhor_modelo,
        feature_names=feature_names,
        nome_arquivo='modelo_sindec_producao.pkl'
    )
    
    # Carregar modelo para uso
    modelo_data = carregar_modelo_final('modelo_sindec_producao.pkl')
    
    if modelo_data:
        # Fazer predições com novos dados
        # dados_novos deve ter as mesmas colunas do treinamento
        predicoes, probabilidades = fazer_predicao(modelo_data, dados_novos)
        
        # Interpretar resultados
        for i, (pred, prob) in enumerate(zip(predicoes, probabilidades)):
            status = "VIÁVEL" if pred == 1 else "NÃO VIÁVEL"
            print(f"Caso {i+1}: {status} (probabilidade: {prob:.3f})")
    """)


def exemplo_fluxo_completo():
    """Exemplo de fluxo completo de trabalho"""
    print("\n" + "=" * 60)
    print("EXEMPLO 5: FLUXO COMPLETO DE TRABALHO")
    print("=" * 60)
    
    print("🔄 Fluxo recomendado para produção:")
    print("""
    import pandas as pd
    from main import executar_pipeline_completo, salvar_modelo_final
    
    # 1. Carrega dados com target criado (das partes 1 e 2)
    df_com_target = pd.read_csv('dados_sindec_com_target.csv')
    print(f"Dados carregados: {df_com_target.shape}")
    
    # 2. Executa pipeline completo
    print("Executando pipeline de ML...")
    resultados = executar_pipeline_completo(
        df_com_target,
        strategy='auto',        # deixa o algoritmo escolher
        run_analysis=True       # análise completa
    )
    
    # 3. Verifica resultados
    if resultados:
        modelo = resultados['best_model']['model']
        nome = resultados['best_model']['name'] 
        score = resultados['best_model']['score']
        features = resultados['data']['feature_names']
        
        print(f"✅ Treinamento concluído!")
        print(f"📊 Melhor modelo: {nome}")
        print(f"🎯 Performance (AUC): {score:.3f}")
        print(f"📋 Features utilizadas: {len(features)}")
        
        # 4. Salva modelo para produção
        salvar_modelo_final(modelo, features, 'modelo_producao.pkl')
        
        # 5. Salva dataset balanceado para análises futuras
        df_balanced = resultados['data']['df_balanced']
        df_balanced.to_csv('dataset_balanceado.csv', index=False)
        
        print("💾 Arquivos salvos para produção!")
        
    else:
        print("❌ Erro no pipeline. Verifique os dados de entrada.")
    """)


if __name__ == "__main__":
    print("🎯 EXEMPLOS DE USO - ALGORITMO SINDEC PARTE 3")
    print("=" * 70)
    
    # Executa todos os exemplos
    exemplo_pipeline_completo()
    exemplo_pipeline_simples()
    exemplo_uso_modular()
    exemplo_salvar_carregar_modelo()
    exemplo_fluxo_completo()
    
    print("\n" + "=" * 70)
    print("✅ EXEMPLOS CONCLUÍDOS")
    print("📝 Edite este arquivo e substitua os comentários pelo seu código real")
    print("🚀 Para executar: python example.py")
    print("=" * 70)