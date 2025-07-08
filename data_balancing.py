"""
Módulo para balanceamento de dados com múltiplas estratégias.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.utils import resample
import warnings
warnings.filterwarnings('ignore')

# Bibliotecas de balanceamento
from imblearn.over_sampling import SMOTE, ADASYN, BorderlineSMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.combine import SMOTEENN, SMOTETomek

from config import RANDOM_STATE, COLUNAS_PROBLEMATICAS


class DataBalancer:
    """
    Classe para balanceamento de dados com múltiplas estratégias
    """

    def __init__(self, random_state=RANDOM_STATE):
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.balancing_strategies = {}
        self.results_comparison = {}

    def analyze_imbalance(self, X, y, target_names=None):
        """
        Analisa o grau de desbalanceamento dos dados
        """
        print("=" * 80)
        print("📊 ANÁLISE DE DESBALANCEAMENTO")
        print("=" * 80)

        # Contagem das classes
        class_counts = Counter(y)
        total = len(y)

        print(f"📋 DISTRIBUIÇÃO ATUAL:")
        for class_val, count in sorted(class_counts.items()):
            class_name = target_names[class_val] if target_names else f"Classe {class_val}"
            percentage = (count / total) * 100
            print(f"   {class_name}: {count:,} ({percentage:.1f}%)")

        # Calcula ratio de desbalanceamento
        minority_class = min(class_counts.values())
        majority_class = max(class_counts.values())
        imbalance_ratio = majority_class / minority_class

        print(f"\n📈 MÉTRICAS DE DESBALANCEAMENTO:")
        print(f"   Ratio de desbalanceamento: {imbalance_ratio:.1f}:1")
        print(f"   Classe minoritária: {minority_class:,} amostras")
        print(f"   Classe majoritária: {majority_class:,} amostras")

        # Classificação do nível de desbalanceamento
        if imbalance_ratio < 2:
            level = "BAIXO"
            emoji = "✅"
        elif imbalance_ratio < 5:
            level = "MODERADO"
            emoji = "⚠️"
        elif imbalance_ratio < 10:
            level = "ALTO"
            emoji = "🔴"
        else:
            level = "EXTREMO"
            emoji = "💀"

        print(f"   Nível de desbalanceamento: {emoji} {level}")

        return {
            'class_counts': class_counts,
            'imbalance_ratio': imbalance_ratio,
            'level': level,
            'minority_class': minority_class,
            'majority_class': majority_class
        }

    def create_balanced_datasets(self, X, y, strategies='all'):
        """
        Cria datasets balanceados usando diferentes estratégias
        """
        print("\n" + "=" * 80)
        print("⚖️ CRIANDO DATASETS BALANCEADOS")
        print("=" * 80)

        balanced_datasets = {}

        # Define estratégias disponíveis
        available_strategies = {
            'random_oversample': self._random_oversample,
            'random_undersample': self._random_undersample,
            'smote': self._smote_balance,
            'borderline_smote': self._borderline_smote,
            'adasyn': self._adasyn_balance,
            'smote_tomek': self._smote_tomek,
            'smote_enn': self._smote_enn,
            'hybrid_custom': self._hybrid_custom
        }

        # Seleciona estratégias para executar
        if strategies == 'all':
            strategies_to_run = available_strategies.keys()
        elif isinstance(strategies, list):
            strategies_to_run = [s for s in strategies if s in available_strategies]
        else:
            strategies_to_run = [strategies] if strategies in available_strategies else []

        # Executa cada estratégia
        for strategy_name in strategies_to_run:
            print(f"\n🔄 Executando: {strategy_name.upper()}")

            try:
                X_balanced, y_balanced = available_strategies[strategy_name](X, y)
                balanced_datasets[strategy_name] = {
                    'X': X_balanced,
                    'y': y_balanced,
                    'original_shape': X.shape,
                    'new_shape': X_balanced.shape,
                    'distribution': Counter(y_balanced)
                }

                # Mostra resultado
                counts = Counter(y_balanced)
                total = len(y_balanced)
                print(f"   ✅ Sucesso! Nova distribuição:")
                for class_val, count in sorted(counts.items()):
                    percentage = (count / total) * 100
                    print(f"      Classe {class_val}: {count:,} ({percentage:.1f}%)")

            except Exception as e:
                print(f"   ❌ Erro: {e}")
                continue

        self.balancing_strategies = balanced_datasets
        return balanced_datasets

    def _random_oversample(self, X, y):
        """Oversampling aleatório da classe minoritária"""
        # Identifica classes
        class_counts = Counter(y)
        max_count = max(class_counts.values())

        X_resampled = []
        y_resampled = []

        for class_val in class_counts.keys():
            # Dados da classe atual
            class_mask = (y == class_val)
            X_class = X[class_mask]
            y_class = y[class_mask]

            # Oversample para igualar à classe majoritária
            X_class_resampled = resample(
                X_class,
                replace=True,
                n_samples=max_count,
                random_state=self.random_state
            )
            y_class_resampled = np.full(max_count, class_val)

            X_resampled.append(X_class_resampled)
            y_resampled.append(y_class_resampled)

        return np.vstack(X_resampled), np.hstack(y_resampled)

    def _random_undersample(self, X, y):
        """Undersampling aleatório da classe majoritária"""
        rus = RandomUnderSampler(random_state=self.random_state)
        return rus.fit_resample(X, y)

    def _smote_balance(self, X, y):
        """SMOTE - Synthetic Minority Oversampling Technique"""
        smote = SMOTE(random_state=self.random_state, k_neighbors=5)
        return smote.fit_resample(X, y)

    def _borderline_smote(self, X, y):
        """Borderline SMOTE - Foca nos casos de fronteira"""
        borderline_smote = BorderlineSMOTE(random_state=self.random_state)
        return borderline_smote.fit_resample(X, y)

    def _adasyn_balance(self, X, y):
        """ADASYN - Adaptive Synthetic Sampling"""
        adasyn = ADASYN(random_state=self.random_state)
        return adasyn.fit_resample(X, y)

    def _smote_tomek(self, X, y):
        """SMOTE + Tomek Links (híbrido)"""
        smote_tomek = SMOTETomek(random_state=self.random_state)
        return smote_tomek.fit_resample(X, y)

    def _smote_enn(self, X, y):
        """SMOTE + Edited Nearest Neighbours (híbrido)"""
        smote_enn = SMOTEENN(random_state=self.random_state)
        return smote_enn.fit_resample(X, y)

    def _hybrid_custom(self, X, y):
        """Estratégia híbrida customizada"""
        # Primeiro aplica SMOTE moderado
        smote = SMOTE(random_state=self.random_state, sampling_strategy=0.7)
        X_smote, y_smote = smote.fit_resample(X, y)

        # Depois aplica undersampling leve
        rus = RandomUnderSampler(random_state=self.random_state, sampling_strategy=0.8)
        return rus.fit_resample(X_smote, y_smote)

    def evaluate_strategies(self, test_size=0.3, cv_folds=3):
        """
        Avalia diferentes estratégias de balanceamento
        """
        print("\n" + "=" * 80)
        print("📈 AVALIAÇÃO DAS ESTRATÉGIAS DE BALANCEAMENTO")
        print("=" * 80)

        results = {}

        for strategy_name, data in self.balancing_strategies.items():
            print(f"\n🔍 Avaliando: {strategy_name.upper()}")

            X_balanced = data['X']
            y_balanced = data['y']

            # Split train/test
            X_train, X_test, y_train, y_test = train_test_split(
                X_balanced, y_balanced,
                test_size=test_size,
                random_state=self.random_state,
                stratify=y_balanced
            )

            # Treina modelo simples para avaliação
            model = RandomForestClassifier(
                n_estimators=100,
                random_state=self.random_state,
                n_jobs=-1
            )

            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]

            # Calcula métricas
            auc_score = roc_auc_score(y_test, y_pred_proba)
            report = classification_report(y_test, y_pred, output_dict=True)

            results[strategy_name] = {
                'auc_score': auc_score,
                'precision_0': report['0']['precision'],
                'recall_0': report['0']['recall'],
                'f1_0': report['0']['f1-score'],
                'precision_1': report['1']['precision'],
                'recall_1': report['1']['recall'],
                'f1_1': report['1']['f1-score'],
                'macro_f1': report['macro avg']['f1-score'],
                'weighted_f1': report['weighted avg']['f1-score'],
                'training_size': len(y_train)
            }

            print(f"   AUC: {auc_score:.3f}")
            print(f"   Macro F1: {report['macro avg']['f1-score']:.3f}")
            print(f"   Weighted F1: {report['weighted avg']['f1-score']:.3f}")
            print(f"   Tamanho treino: {len(y_train):,}")

        self.results_comparison = results
        return results

    def get_best_strategy(self, metric='macro_f1'):
        """
        Retorna a melhor estratégia baseada na métrica escolhida
        """
        if not self.results_comparison:
            print("❌ Execute evaluate_strategies() primeiro!")
            return None

        best_strategy = max(
            self.results_comparison.items(),
            key=lambda x: x[1][metric]
        )

        strategy_name = best_strategy[0]
        strategy_score = best_strategy[1][metric]

        print(f"\n🏆 MELHOR ESTRATÉGIA (por {metric.upper()}):")
        print(f"   Estratégia: {strategy_name.upper()}")
        print(f"   Score: {strategy_score:.3f}")

        return strategy_name, self.balancing_strategies[strategy_name]

    def create_final_balanced_dataset(self, X, y, strategy='auto', target_ratio=0.4):
        """
        Cria dataset final balanceado com controle fino

        Args:
            X, y: Dados originais
            strategy: 'auto', 'conservative', 'moderate', 'aggressive' ou nome específico
            target_ratio: Ratio desejado para classe minoritária (0.4 = 40%)
        """
        print("\n" + "=" * 80)
        print("🎯 CRIANDO DATASET FINAL BALANCEADO")
        print("=" * 80)

        # Define estratégias predefinidas
        if strategy == 'auto':
            # Baseado na análise anterior, escolhe automaticamente
            imbalance_ratio = max(Counter(y).values()) / min(Counter(y).values())

            if imbalance_ratio < 3:
                strategy = 'conservative'
            elif imbalance_ratio < 7:
                strategy = 'moderate'
            else:
                strategy = 'aggressive'

            print(f"📊 Estratégia automática selecionada: {strategy.upper()}")

        # Aplica estratégia escolhida
        if strategy == 'conservative':
            # Undersampling leve + pequeno oversampling
            rus = RandomUnderSampler(
                random_state=self.random_state,
                sampling_strategy=0.7  # Reduz classe majoritária para 70% vs 30%
            )
            X_balanced, y_balanced = rus.fit_resample(X, y)

        elif strategy == 'moderate':
            # SMOTE balanceado
            smote = SMOTE(
                random_state=self.random_state,
                sampling_strategy=target_ratio  # Ex: 40% classe minoritária
            )
            X_balanced, y_balanced = smote.fit_resample(X, y)

        elif strategy == 'aggressive':
            # SMOTE + limpeza
            smote_enn = SMOTEENN(random_state=self.random_state)
            X_balanced, y_balanced = smote_enn.fit_resample(X, y)

        else:
            # Estratégia nomeada específica
            if strategy in self.balancing_strategies:
                data = self.balancing_strategies[strategy]
                X_balanced = data['X']
                y_balanced = data['y']
            else:
                print(f"❌ Estratégia '{strategy}' não encontrada!")
                return None, None

        # Resultados
        original_dist = Counter(y)
        new_dist = Counter(y_balanced)

        print(f"\n📊 RESULTADO FINAL:")
        print(f"   Dataset original: {X.shape[0]:,} amostras")
        print(f"   Dataset balanceado: {X_balanced.shape[0]:,} amostras")

        print(f"\n   Distribuição original:")
        total_orig = len(y)
        for class_val, count in sorted(original_dist.items()):
            print(f"      Classe {class_val}: {count:,} ({count/total_orig*100:.1f}%)")

        print(f"\n   Distribuição balanceada:")
        total_new = len(y_balanced)
        for class_val, count in sorted(new_dist.items()):
            print(f"      Classe {class_val}: {count:,} ({count/total_new*100:.1f}%)")

        return X_balanced, y_balanced


def balancear_dados_viabilidade(df_com_target, target_col='Viavel',
                               features_to_use=None, strategy='auto'):
    """
    Função principal para balanceamento de dados de viabilidade

    Args:
        df_com_target: DataFrame com target criado
        target_col: Nome da coluna target
        features_to_use: Lista de features para usar (None = usar todas numéricas)
        strategy: Estratégia de balanceamento

    Returns:
        X_balanced, y_balanced, feature_names, balancer
    """
    print("🎯 BALANCEAMENTO DE DADOS - VIABILIDADE JURÍDICA")
    print("=" * 60)

    # Prepara dados
    if features_to_use is None:
        # Usa features numéricas automaticamente
        numeric_cols = df_com_target.select_dtypes(include=[np.number]).columns
        features_to_use = [col for col in numeric_cols if col != target_col]

    # Remove colunas problemáticas
    features_to_use = [col for col in features_to_use if col not in COLUNAS_PROBLEMATICAS]

    print(f"📊 Usando {len(features_to_use)} features para balanceamento")

    # Prepara X e y
    X = df_com_target[features_to_use].copy()
    y = df_com_target[target_col].copy()

    # Trata valores missing e infinitos
    X = X.fillna(0)
    X = X.replace([np.inf, -np.inf], 0)

    # Inicializa balanceador
    balancer = DataBalancer(random_state=RANDOM_STATE)

    # Analisa desbalanceamento
    balancer.analyze_imbalance(X.values, y.values, {0: 'NÃO VIÁVEL', 1: 'VIÁVEL'})

    # Cria dataset balanceado
    X_balanced, y_balanced = balancer.create_final_balanced_dataset(
        X.values, y.values, strategy=strategy
    )

    return X_balanced, y_balanced, features_to_use, balancer