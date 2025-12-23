"""
Hotel Competitiveness Agent

Un agente de IA para análisis de competitividad hotelera.
"""

__version__ = "1.0.0"
__author__ = "Tu Nombre"

from .data_processor import DataProcessor
from .competitive_analyzer import CompetitiveAnalyzer
from .hotel_agent import HotelAgent

__all__ = [
    "DataProcessor",
    "CompetitiveAnalyzer", 
    "HotelAgent"
]
