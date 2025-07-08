"""
Pacote de páginas para o sistema de análise jurídica
"""

from .individual_analysis import show_individual_analysis
from .batch_analysis import show_batch_analysis
from .dashboard import show_dashboard
from .about import show_about

__all__ = [
    'show_individual_analysis',
    'show_batch_analysis', 
    'show_dashboard',
    'show_about'
]