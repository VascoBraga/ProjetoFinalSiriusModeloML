"""
Orquestrador principal que executa sequencialmente os três pipelines SINDEC

Este script coordena a execução dos três arquivos main existentes:
1. main.py (data_preparation.py) - Preparação e enriquecimento dos dados
2. main2.py (ml_preparation.py) - Preparação para Machine Learning  
3. main3.py (model_training.py) - Treinamento de modelos

Mantém a modularidade atual, apenas coordenando a execução sequencial.

Autor: Sistema de Classificação de Viabilidade Jurídica
Versão: 1.0.0
"""

import os
import sys
import time
import subprocess
import argparse
from datetime import datetime
from typing import Optional, List
import logging


class SindecOrchestrator:
    """
    Orquestrador que coordena a execução dos três pipelines main existentes
    """
    
    def __init__(self, log_level: str = "INFO"):
        """
        Inicializa o orquestrador
        
        Args:
            log_level: Nível de log (DEBUG, INFO, WARNING, ERROR)
        """
        self.setup_logging(log_level)
        self.logger = logging.getLogger(__name__)
        
        self.start_time = None
        self.resultados_execucao = {}
        
        # Mapeamento dos arquivos main
        self.pipelines = {
            1: 'main.py',           # ou 'data_preparation.py' se renomeado
            2: 'main2.py',          # ou 'ml_preparation.py' se renomeado  
            3: 'main3.py'           # ou 'model_training.py' se renomeado
        }
        
        self.logger.info("🚀 SINDEC ORCHESTRATOR INICIALIZADO")
        self.logger.info("="*60)
    
    def setup_logging(self, level: str):
        """Configura o sistema de logging"""
        log_filename = f'sindec_orchestrator_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        
        logging.basicConfig(
            level=getattr(logging, level.upper()),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger.info(f"📝 Log salvo em: {log_filename}")
    
    def verificar_arquivos_existem(self, etapas: List[int]) -> bool:
        """
        Verifica se os arquivos main necessários existem
        
        Args:
            etapas: Lista de etapas para verificar
            
        Returns:
            True se todos os arquivos existem
        """
        self.logger.info("🔍 Verificando arquivos necessários...")
        
        arquivos_faltando = []
        
        for etapa in etapas:
            arquivo = self.pipelines[etapa]
            if not os.path.exists(arquivo):
                arquivos_faltando.append(arquivo)
        
        if arquivos_faltando:
            self.logger.error("❌ Arquivos não encontrados:")
            for arquivo in arquivos_faltando:
                self.logger.error(f"   - {arquivo}")
            return False
        
        self.logger.info("✅ Todos os arquivos necessários encontrados")
        return True
    
    def executar_pipeline(self, etapa: int, arquivo_dados: str, **kwargs) -> bool:
        """
        Executa um pipeline específico
        
        Args:
            etapa: Número da etapa (1, 2 ou 3)
            arquivo_dados: Caminho para o arquivo de dados
            **kwargs: Argumentos adicionais específicos de cada etapa
            
        Returns:
            True se executou com sucesso
        """
        arquivo_main = self.pipelines[etapa]
        
        self.logger.info(f"\n🔄 EXECUTANDO ETAPA {etapa}: {arquivo_main}")
        self.logger.info("="*50)
        
        start_time = time.time()
        
        try:
            if etapa == 1:
                # Etapa 1: main.py (preparação dos dados)
                sucesso = self._executar_etapa_1(arquivo_main, arquivo_dados, **kwargs)
                
            elif etapa == 2:
                # Etapa 2: main2.py (preparação ML)
                sucesso = self._executar_etapa_2(arquivo_main, arquivo_dados, **kwargs)
                
            elif etapa == 3:
                # Etapa 3: main3.py (treinamento)
                sucesso = self._executar_etapa_3(arquivo_main, **kwargs)
            
            else:
                raise ValueError(f"Etapa {etapa} não reconhecida")
            
            tempo_execucao = time.time() - start_time
            
            if sucesso:
                self.logger.info(f"✅ Etapa {etapa} concluída com sucesso em {tempo_execucao:.2f}s")
                self.resultados_execucao[f'etapa_{etapa}'] = {
                    'status': 'sucesso',
                    'tempo': tempo_execucao,
                    'arquivo': arquivo_main
                }
            else:
                self.logger.error(f"❌ Etapa {etapa} falhou após {tempo_execucao:.2f}s")
                self.resultados_execucao[f'etapa_{etapa}'] = {
                    'status': 'erro',
                    'tempo': tempo_execucao,
                    'arquivo': arquivo_main
                }
            
            return sucesso
            
        except Exception as e:
            tempo_execucao = time.time() - start_time
            self.logger.error(f"❌ Erro na Etapa {etapa}: {e}")
            self.resultados_execucao[f'etapa_{etapa}'] = {
                'status': 'erro',
                'tempo': tempo_execucao,
                'arquivo': arquivo_main,
                'erro': str(e)
            }
            return False
    
    def _executar_etapa_1(self, arquivo_main: str, arquivo_dados: str, **kwargs) -> bool:
        """Executa a etapa 1 (preparação dos dados)"""
        try:
            # Importa e executa o main.py
            sys.path.insert(0, os.path.dirname(os.path.abspath(arquivo_main)))
            
            # Import dinâmico do main.py
            spec = importlib.util.spec_from_file_location("main_etapa1", arquivo_main)
            main_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main_module)
            
            # Executa a função main se existir
            if hasattr(main_module, 'main'):
                # Configura argumentos para simular linha de comando
                original_argv = sys.argv
                sys.argv = ['main.py']  # Simula execução sem argumentos adicionais
                
                try:
                    main_module.main()
                    return True
                finally:
                    sys.argv = original_argv
            else:
                self.logger.warning("⚠️ Função main() não encontrada em main.py")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao executar {arquivo_main}: {e}")
            return False
    
    def _executar_etapa_2(self, arquivo_main: str, arquivo_dados: str, **kwargs) -> bool:
        """Executa a etapa 2 (preparação ML)"""
        try:
            # Constrói comando para executar main2.py
            cmd = [sys.executable, arquivo_main, arquivo_dados]
            
            # Adiciona argumentos opcionais
            if kwargs.get('incluir_tfidf', False):
                cmd.append('--tfidf')
            
            if 'estrategia' in kwargs:
                cmd.extend(['--strategy', kwargs['estrategia']])
            
            self.logger.info(f"Executando: {' '.join(cmd)}")
            
            # Executa via subprocess
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info("Saída do processo:")
                self.logger.info(result.stdout)
                return True
            else:
                self.logger.error("Erro na execução:")
                self.logger.error(result.stderr)
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao executar {arquivo_main}: {e}")
            return False
    
    def _executar_etapa_3(self, arquivo_main: str, **kwargs) -> bool:
        """Executa a etapa 3 (treinamento)"""
        try:
            # Import dinâmico do main3.py
            import importlib.util
            
            spec = importlib.util.spec_from_file_location("main_etapa3", arquivo_main)
            main_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main_module)
            
            # Verifica se tem dados da etapa anterior
            arquivo_dados_ml = 'dados_com_target.csv'  # Arquivo gerado pela etapa 2
            
            if not os.path.exists(arquivo_dados_ml):
                self.logger.error(f"❌ Arquivo {arquivo_dados_ml} não encontrado. Execute a Etapa 2 primeiro.")
                return False
            
            # Carrega dados e executa pipeline
            import pandas as pd
            df_com_target = pd.read_csv(arquivo_dados_ml)
            
            modo = kwargs.get('modo_treinamento', 'completo')
            
            if modo == 'completo':
                resultado = main_module.executar_pipeline_completo(df_com_target)
            else:
                resultado = main_module.executar_pipeline_simples(df_com_target)
            
            if resultado is not None:
                self.logger.info("🎯 Treinamento concluído com sucesso")
                return True
            else:
                self.logger.error("❌ Falha no treinamento")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao executar {arquivo_main}: {e}")
            return False
    
    def executar_pipeline_completo(self, arquivo_dados: str,
                                 etapas: Optional[List[int]] = None,
                                 **kwargs) -> bool:
        """
        Executa o pipeline completo coordenando os três mains
        
        Args:
            arquivo_dados: Caminho para o arquivo CSV original
            etapas: Lista de etapas para executar [1,2,3] ou None para todas
            **kwargs: Argumentos adicionais para as etapas
            
        Returns:
            True se todas as etapas executaram com sucesso
        """
        self.start_time = time.time()
        
        if etapas is None:
            etapas = [1, 2, 3]
        
        self.logger.info("🚀 INICIANDO PIPELINE COMPLETO SINDEC")
        self.logger.info("="*60)
        self.logger.info(f"📁 Arquivo de dados: {arquivo_dados}")
        self.logger.info(f"🔢 Etapas a executar: {etapas}")
        
        # Verifica se arquivo de dados existe
        if not os.path.exists(arquivo_dados):
            self.logger.error(f"❌ Arquivo de dados não encontrado: {arquivo_dados}")
            return False
        
        # Verifica se arquivos main necessários existem
        if not self.verificar_arquivos_existem(etapas):
            return False
        
        # Executa etapas sequencialmente
        todas_sucesso = True
        
        for etapa in sorted(etapas):
            sucesso = self.executar_pipeline(etapa, arquivo_dados, **kwargs)
            
            if not sucesso:
                self.logger.error(f"❌ Falha na Etapa {etapa}. Interrompendo pipeline.")
                todas_sucesso = False
                break
        
        # Resumo final
        tempo_total = time.time() - self.start_time
        self.imprimir_resumo_final(tempo_total, todas_sucesso)
        
        return todas_sucesso
    
    def imprimir_resumo_final(self, tempo_total: float, sucesso: bool):
        """Imprime resumo final da execução"""
        self.logger.info("\n" + "="*60)
        self.logger.info("📊 RESUMO FINAL DO PIPELINE SINDEC")
        self.logger.info("="*60)
        
        for etapa_nome, dados in self.resultados_execucao.items():
            numero = etapa_nome.split('_')[1]
            status = dados['status']
            tempo = dados['tempo']
            arquivo = dados['arquivo']
            
            emoji = "✅" if status == 'sucesso' else "❌"
            self.logger.info(f"{emoji} Etapa {numero}: {status.upper()} ({tempo:.2f}s) - {arquivo}")
            
            if 'erro' in dados:
                self.logger.info(f"   ⚠️ Erro: {dados['erro']}")
        
        self.logger.info(f"\n⏱️ TEMPO TOTAL: {tempo_total:.2f} segundos ({tempo_total/60:.1f} minutos)")
        
        status_final = "SUCESSO" if sucesso else "FALHA"
        emoji_final = "🎉" if sucesso else "💥"
        self.logger.info(f"{emoji_final} STATUS FINAL: {status_final}")
        
        if sucesso:
            self.logger.info("\n🎯 Pipeline completo executado com sucesso!")
            self.logger.info("📁 Verifique os arquivos de saída gerados por cada etapa.")
        else:
            self.logger.info("\n⚠️ Pipeline interrompido devido a falhas.")
            self.logger.info("🔍 Verifique os logs acima para detalhes dos erros.")


def main():
    """Função principal para execução via linha de comando"""
    parser = argparse.ArgumentParser(
        description="Orquestrador que executa sequencialmente os três pipelines SINDEC",
        epilog="""
Exemplos de uso:
  python main_orchestrator.py dados_sindec.csv
  python main_orchestrator.py dados_sindec.csv --etapas 1 2
  python main_orchestrator.py dados_sindec.csv --tfidf --strategy moderate
        """
    )
    
    parser.add_argument("arquivo", help="Caminho para o arquivo CSV de dados")
    parser.add_argument("--etapas", nargs='+', type=int, choices=[1, 2, 3],
                       help="Etapas para executar (ex: --etapas 1 2)")
    parser.add_argument("--tfidf", action="store_true", 
                       help="Incluir features TF-IDF na Etapa 2")
    parser.add_argument("--strategy", default="auto", 
                       choices=['auto', 'conservative', 'moderate', 'aggressive'],
                       help="Estratégia de balanceamento para Etapa 2")
    parser.add_argument("--modo", default="completo", choices=['completo', 'simples'],
                       help="Modo de treinamento para Etapa 3")
    parser.add_argument("--log-level", default="INFO", 
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help="Nível de log")
    
    args = parser.parse_args()
    
    try:
        # Inicializa orquestrador
        orchestrator = SindecOrchestrator(log_level=args.log_level)
        
        # Prepara argumentos para as etapas
        kwargs = {
            'incluir_tfidf': args.tfidf,
            'estrategia': args.strategy,
            'modo_treinamento': args.modo
        }
        
        # Executa pipeline
        sucesso = orchestrator.executar_pipeline_completo(
            arquivo_dados=args.arquivo,
            etapas=args.etapas,
            **kwargs
        )
        
        return 0 if sucesso else 1
        
    except KeyboardInterrupt:
        print("\n⚠️ Execução interrompida pelo usuário.")
        return 130
        
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        return 1


if __name__ == "__main__":
    import importlib.util
    sys.exit(main())