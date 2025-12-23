"""
Utilidades para el Hotel Competitiveness Agent
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any, Optional

def validate_data_quality(df: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
    """Validar calidad de los datos"""
    
    report = {
        "dataset": dataset_name,
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_values": {},
        "data_types": {},
        "duplicates": 0,
        "anomalies": [],
        "quality_score": 0
    }
    
    # Valores faltantes
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        missing_pct = (missing_count / len(df)) * 100
        report["missing_values"][col] = {
            "count": int(missing_count),
            "percentage": round(missing_pct, 2)
        }
    
    # Tipos de datos
    for col in df.columns:
        report["data_types"][col] = str(df[col].dtype)
    
    # Duplicados
    report["duplicates"] = int(df.duplicated().sum())
    
    # Calcular score de calidad (0-100)
    score = 100
    
    # Penalizar por valores faltantes excesivos
    high_missing = sum(1 for v in report["missing_values"].values() if v["percentage"] > 20)
    score -= high_missing * 10
    
    # Penalizar por duplicados excesivos
    if report["duplicates"] > len(df) * 0.1:  # Más del 10%
        score -= 20
    
    report["quality_score"] = max(0, score)
    
    return report

def format_currency(amount: float, currency: str = "USD") -> str:
    """Formatear cantidad como moneda"""
    if pd.isna(amount):
        return "N/A"
    
    if currency == "USD":
        return f"${amount:,.0f}"
    else:
        return f"{amount:,.0f} {currency}"

def format_percentage(value: float, include_sign: bool = True) -> str:
    """Formatear porcentaje"""
    if pd.isna(value):
        return "N/A"
    
    sign = "+" if value > 0 and include_sign else ""
    return f"{sign}{value:.1f}%"

def calculate_date_features(date_series: pd.Series) -> pd.DataFrame:
    """Calcular características de fechas"""
    
    df_features = pd.DataFrame()
    
    df_features['year'] = date_series.dt.year
    df_features['month'] = date_series.dt.month
    df_features['day'] = date_series.dt.day
    df_features['weekday'] = date_series.dt.weekday
    df_features['is_weekend'] = date_series.dt.weekday >= 5
    df_features['quarter'] = date_series.dt.quarter
    
    # Temporada (ejemplo para hemisferio norte)
    df_features['season'] = df_features['month'].map({
        12: 'Winter', 1: 'Winter', 2: 'Winter',
        3: 'Spring', 4: 'Spring', 5: 'Spring',
        6: 'Summer', 7: 'Summer', 8: 'Summer',
        9: 'Fall', 10: 'Fall', 11: 'Fall'
    })
    
    return df_features

def detect_outliers(series: pd.Series, method: str = 'zscore', threshold: float = 2.0) -> pd.Series:
    """Detectar outliers en una serie"""
    
    if method == 'zscore':
        z_scores = np.abs((series - series.mean()) / series.std())
        return z_scores > threshold
    
    elif method == 'iqr':
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return (series < lower_bound) | (series > upper_bound)
    
    else:
        raise ValueError("Method must be 'zscore' or 'iqr'")

def generate_summary_stats(df: pd.DataFrame, numeric_columns: List[str]) -> Dict:
    """Generar estadísticas resumen"""
    
    summary = {}
    
    for col in numeric_columns:
        if col in df.columns:
            series = pd.to_numeric(df[col], errors='coerce')
            
            summary[col] = {
                'count': int(series.count()),
                'mean': round(series.mean(), 2),
                'median': round(series.median(), 2),
                'std': round(series.std(), 2),
                'min': round(series.min(), 2),
                'max': round(series.max(), 2),
                'q25': round(series.quantile(0.25), 2),
                'q75': round(series.quantile(0.75), 2)
            }
    
    return summary

def create_data_dictionary() -> Dict:
    """Crear diccionario de datos para mejor comprensión"""
    
    return {
        "hound_internal": {
            "description": "Competitividad interna vs proveedores",
            "key_fields": {
                "PamBaseRate ($)": "Tarifa base sin impuestos (Despegar)",
                "ExpBaseRate ($)": "Tarifa base competidor 1",  
                "HBGBaseRate ($)": "Tarifa base competidor 2",
                "PoS": "Punto de venta / Mercado",
                "contractcurrencybase_pam": "Moneda del contrato"
            }
        },
        "hound_external": {
            "description": "Competencia externa con precios finales",
            "key_fields": {
                "price_despegar (USD)": "Precio final Despegar en USD",
                "buyers_best_price_competitor_total (USD)": "Mejor precio competencia",
                "adults": "Número de adultos",
                "children": "Número de niños",
                "los": "Duración de estadía (noches)",
                "agency_name": "Nombre de la agencia interesada"
            }
        },
        "extranet": {
            "description": "Configuración real de hoteles",
            "key_fields": {
                "Disponibilidad": "% de disponibilidad (0-1)",
                "Pos_Tildado": "Mercados habilitados",
                "Rate_type": "Tipo de tarifa (OPAQUE, STANDALONE, PACKAGE)"
            }
        }
    }

def export_analysis_report(data: Dict, filename: str = None) -> str:
    """Exportar reporte de análisis a JSON"""
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hotel_analysis_report_{timestamp}.json"
    
    # Convertir datetime objects to strings for JSON serialization
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        raise TypeError(f"Object {obj} of type {type(obj)} is not JSON serializable")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=json_serializer)
    
    return filename

def clean_price_columns(df: pd.DataFrame, price_columns: List[str]) -> pd.DataFrame:
    """Limpiar columnas de precios (remover comas, convertir a float)"""
    
    df_clean = df.copy()
    
    for col in price_columns:
        if col in df_clean.columns:
            # Remover comas y convertir a float
            df_clean[col] = df_clean[col].astype(str).str.replace(',', '').astype(float)
    
    return df_clean

def calculate_business_metrics(df_external: pd.DataFrame, hotel_name: str) -> Dict:
    """Calcular métricas de negocio específicas"""
    
    hotel_data = df_external[df_external['Nombre_Hotel'] == hotel_name]
    
    if hotel_data.empty:
        return {}
    
    # Métricas básicas
    total_searches = len(hotel_data)
    unique_agencies = hotel_data['agency_name'].nunique()
    avg_los = hotel_data['los'].mean()
    
    # Competitividad por segmento
    segments = {
        'couples': hotel_data[(hotel_data['adults'] == 2) & (hotel_data['children'] == 0)],
        'families': hotel_data[hotel_data['children'] > 0],
        'groups': hotel_data[hotel_data['adults'] > 2]
    }
    
    segment_metrics = {}
    for segment_name, segment_data in segments.items():
        if not segment_data.empty:
            segment_metrics[segment_name] = {
                'searches': len(segment_data),
                'avg_price_diff': round(segment_data['price_diff_pct'].mean(), 2),
                'competitive_ratio': round((segment_data['price_diff_pct'] < 0).mean() * 100, 2)
            }
    
    return {
        'total_searches': total_searches,
        'unique_agencies': unique_agencies,
        'avg_length_of_stay': round(avg_los, 1),
        'segment_analysis': segment_metrics
    }

def generate_recommendations_engine(hotel_summary: Dict, opportunities: Dict) -> List[str]:
    """Motor de recomendaciones basado en reglas de negocio"""
    
    recommendations = []
    
    # Score general
    score = hotel_summary.get('competitiveness_score', 0)
    
    if score < 30:
        recommendations.append("🚨 ACCIÓN CRÍTICA: Revisar toda la estrategia de pricing")
    elif score < 50:
        recommendations.append("⚠️ ATENCIÓN: Optimizar precios en mercados prioritarios")
    
    # Análisis por mercado
    high_priority_count = sum(1 for data in opportunities.values() 
                             if data.get('priority') == 'Alta')
    
    if high_priority_count >= 3:
        recommendations.append("🎯 Múltiples mercados críticos: implementar strategy review")
    
    # Diferencia promedio
    avg_diff = hotel_summary.get('avg_price_difference_pct', 0)
    
    if avg_diff > 20:
        recommendations.append("💰 Considerar reducción de precios del 10-15%")
    elif avg_diff > 10:
        recommendations.append("💰 Ajuste de precios del 5-10% recomendado")
    elif avg_diff < -15:
        recommendations.append("📈 Oportunidad de incrementar precios del 8-12%")
    elif avg_diff < -5:
        recommendations.append("📈 Considerar incremento moderado del 3-6%")
    
    # Volatilidad
    volatility = hotel_summary.get('price_volatility', 0)
    
    if volatility > 30:
        recommendations.append("📊 Alta volatilidad detectada: revisar consistencia de pricing")
    
    # Disponibilidad vs competencia
    competitive_ratio = (hotel_summary.get('competitive_positions', 0) / 
                        max(1, hotel_summary.get('total_searches', 1)))
    
    if competitive_ratio < 0.2:
        recommendations.append("🎯 Baja competitividad: menos del 20% de posiciones ganadoras")
    
    return recommendations

if __name__ == "__main__":
    # Ejemplo de uso
    print("🔧 Hotel Competitiveness Agent - Utilities")
    print("Módulo de utilidades cargado correctamente")
