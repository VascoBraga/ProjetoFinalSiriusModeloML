"""
Módulo para treinamento de modelos de machine learning
"""

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score

from clean_features import preparar_dados_limpos
from config import DEFAULT_CONFIG


def treinar_modelo_limpo(df_balanced):
    """
    Treina modelo com dados limpos (sem data leakage)
    
    Args:
        df_balanced: DataFrame balanceado
        
    Returns:
        tuple: (resultados, X_train, X_test, y_train, y_test, feature_names)
    """
    print("🚀 TREINANDO MODELO LIMPO")
    print("=" * 30)
    
    # Prepara dados limpos
    X, y, feature_names = preparar_dados_limpos(df_balanced)
    
    if X is None:
        return None, None, None, None, None, None
    
    # Split dos dados
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=DEFAULT_CONFIG['random_state'], stratify=y
    )
    
    # Modelos para testar
    modelos = {
        'Random Forest': RandomForestClassifier(
            n_estimators=DEFAULT_CONFIG['n_estimators'], 
            random_state=DEFAULT_CONFIG['random_state']
        ),
        'Gradient Boosting': GradientBoostingClassifier(
            n_estimators=DEFAULT_CONFIG['n_estimators'], 
            random_state=DEFAULT_CONFIG['random_state']
        ),
        'Logistic Regression': LogisticRegression(
            random_state=DEFAULT_CONFIG['random_state'], 
            max_iter=DEFAULT_CONFIG['max_iter']
        )
    }
    
    resultados = {}
    
    print(f"\n📊 RESULTADOS REALISTAS:")
    print("=" * 30)
    
    for nome, modelo in modelos.items():
        # Treina
        modelo.fit(X_train, y_train)
        
        # Predições
        y_pred = modelo.predict(X_test)
        y_proba = modelo.predict_proba(X_test)[:, 1]
        
        # Métricas
        auc = roc_auc_score(y_test, y_proba)
        report = classification_report(y_test, y_pred, output_dict=True)
        
        resultados[nome] = {
            'auc': auc,
            'f1': report['macro avg']['f1-score'],
            'precision_viavel': report['1']['precision'],
            'recall_viavel': report['1']['recall'],
            'model': modelo
        }
        
        print(f"\n🔍 {nome}:")
        print(f"   AUC: {auc:.3f}")
        print(f"   F1-Score: {report['macro avg']['f1-score']:.3f}")
        print(f"   Precision (Viável): {report['1']['precision']:.3f}")
        print(f"   Recall (Viável): {report['1']['recall']:.3f}")
        
        # Feature importance se disponível
        if hasattr(modelo, 'feature_importances_'):
            importances = modelo.feature_importances_
            top_features = sorted(zip(feature_names, importances),
                                key=lambda x: x[1], reverse=True)[:5]
            print(f"   Top 5 features:")
            for feat, imp in top_features:
                print(f"     {feat}: {imp:.3f}")
    
    return resultados, X_train, X_test, y_train, y_test, feature_names


def avaliar_modelo_completo(modelo, X_test, y_test, nome_modelo):
    """
    Avalia um modelo treinado de forma completa
    
    Args:
        modelo: Modelo treinado
        X_test: Features de teste
        y_test: Target de teste
        nome_modelo: Nome do modelo para exibição
        
    Returns:
        dict: Métricas do modelo
    """
    print(f"\n📊 AVALIAÇÃO COMPLETA - {nome_modelo}")
    print("=" * 40)
    
    # Predições
    y_pred = modelo.predict(X_test)
    y_proba = modelo.predict_proba(X_test)[:, 1]
    
    # Métricas
    auc = roc_auc_score(y_test, y_proba)
    report = classification_report(y_test, y_pred, output_dict=True)
    
    print(f"AUC: {auc:.3f}")
    print(f"Accuracy: {report['accuracy']:.3f}")
    print(f"F1-Score (Macro): {report['macro avg']['f1-score']:.3f}")
    print(f"F1-Score (Weighted): {report['weighted avg']['f1-score']:.3f}")
    
    print("\nDetalhes por classe:")
    for classe in ['0', '1']:
        if classe in report:
            label = 'NÃO VIÁVEL' if classe == '0' else 'VIÁVEL'
            print(f"  {label}:")
            print(f"    Precision: {report[classe]['precision']:.3f}")
            print(f"    Recall: {report[classe]['recall']:.3f}")
            print(f"    F1-Score: {report[classe]['f1-score']:.3f}")
            print(f"    Support: {report[classe]['support']}")
    
    return {
        'auc': auc,
        'accuracy': report['accuracy'],
        'f1_macro': report['macro avg']['f1-score'],
        'f1_weighted': report['weighted avg']['f1-score'],
        'precision_viavel': report.get('1', {}).get('precision', 0),
        'recall_viavel': report.get('1', {}).get('recall', 0),
        'report': report
    }


def selecionar_melhor_modelo(resultados):
    """
    Seleciona o melhor modelo baseado nas métricas
    
    Args:
        resultados: Dicionário com resultados dos modelos
        
    Returns:
        tuple: (nome_melhor_modelo, melhor_modelo, melhor_score)
    """
    print("\n🏆 SELECIONANDO MELHOR MODELO")
    print("=" * 35)
    
    melhor_score = 0
    melhor_modelo = None
    nome_melhor = None
    
    print("Comparação por AUC:")
    for nome, resultado in resultados.items():
        auc = resultado['auc']
        print(f"  {nome}: {auc:.3f}")
        
        if auc > melhor_score:
            melhor_score = auc
            melhor_modelo = resultado['model']
            nome_melhor = nome
    
    print(f"\n🥇 Melhor modelo: {nome_melhor} (AUC: {melhor_score:.3f})")
    
    return nome_melhor, melhor_modelo, melhor_score