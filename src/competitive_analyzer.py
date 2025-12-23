import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Tuple
import seaborn as sns
import matplotlib.pyplot as plt

class CompetitiveAnalyzer:
    """Analizador de competitividad hotelera con visualizaciones"""
    
    def __init__(self, data_processor):
        self.dp = data_processor
        
    def create_price_comparison_chart(self, hotel_name: str):
        """Crear gráfico de comparación de precios"""
        
        data = self.dp.hound_external[self.dp.hound_external['Nombre_Hotel'] == hotel_name]
        
        if data.empty:
            return None
            
        # Preparar datos para visualización
        plot_data = data.groupby('PoS').agg({
            'price_despegar (USD)': 'mean',
            'buyers_best_price_competitor_total (USD)': 'mean',
            'price_diff_pct': 'mean'
        }).reset_index()
        
        # Crear gráfico
        fig = go.Figure()
        
        # Barras de precios
        fig.add_trace(go.Bar(
            name='Despegar',
            x=plot_data['PoS'],
            y=plot_data['price_despegar (USD)'],
            marker_color='#1f77b4'
        ))
        
        fig.add_trace(go.Bar(
            name='Competidores',
            x=plot_data['PoS'],
            y=plot_data['buyers_best_price_competitor_total (USD)'],
            marker_color='#ff7f0e'
        ))
        
        fig.update_layout(
            title=f'Comparación de Precios - {hotel_name}',
            xaxis_title='Mercado (PoS)',
            yaxis_title='Precio Promedio (USD)',
            barmode='group',
            height=500
        )
        
        return fig
    
    def create_competitiveness_dashboard(self, hotel_name: str):
        """Crear dashboard completo de competitividad"""
        
        data = self.dp.hound_external[self.dp.hound_external['Nombre_Hotel'] == hotel_name]
        
        if data.empty:
            return None
        
        # Crear subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Diferencia de Precios por PoS', 'Distribución de Diferencias',
                          'Patrones Temporales', 'Análisis por Duración'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # 1. Diferencias por PoS
        pos_data = data.groupby('PoS')['price_diff_pct'].agg(['mean', 'std']).reset_index()
        
        fig.add_trace(
            go.Bar(x=pos_data['PoS'], y=pos_data['mean'], 
                   name='Diff Promedio', showlegend=False,
                   marker_color=['red' if x < 0 else 'green' for x in pos_data['mean']]),
            row=1, col=1
        )
        
        # 2. Histograma de diferencias
        fig.add_trace(
            go.Histogram(x=data['price_diff_pct'], name='Distribución', 
                        showlegend=False, marker_color='lightblue'),
            row=1, col=2
        )
        
        # 3. Tendencia temporal
        data['month'] = data['check_in'].dt.month
        temporal_data = data.groupby('month')['price_diff_pct'].mean().reset_index()
        
        fig.add_trace(
            go.Scatter(x=temporal_data['month'], y=temporal_data['month'], 
                      mode='lines+markers', name='Tendencia', showlegend=False),
            row=2, col=1
        )
        
        # 4. Análisis por duración
        los_data = data.groupby('los')['price_diff_pct'].mean().reset_index()
        
        fig.add_trace(
            go.Scatter(x=los_data['los'], y=los_data['price_diff_pct'], 
                      mode='markers', name='Por Duración', showlegend=False,
                      marker_size=10),
            row=2, col=2
        )
        
        fig.update_layout(height=600, title_text=f"Dashboard de Competitividad - {hotel_name}")
        
        return fig
    
    def analyze_market_opportunities(self, hotel_name: str) -> Dict:
        """Analizar oportunidades por mercado"""
        
        data = self.dp.hound_external[self.dp.hound_external['Nombre_Hotel'] == hotel_name]
        
        if data.empty:
            return {}
        
        opportunities = {}
        
        for pos in data['PoS'].unique():
            pos_data = data[data['PoS'] == pos]
            
            avg_diff = pos_data['price_diff_pct'].mean()
            volatility = pos_data['price_diff_pct'].std()
            volume = len(pos_data)
            agencies = pos_data['agency_name'].nunique()
            
            # Clasificar oportunidad
            if avg_diff < -5:  # Estamos significativamente más baratos
                opportunity_type = "Subir precios"
                priority = "Media"
            elif avg_diff > 10:  # Estamos significativamente más caros
                opportunity_type = "Bajar precios"
                priority = "Alta"
            else:
                opportunity_type = "Monitorear"
                priority = "Baja"
            
            opportunities[pos] = {
                'avg_price_diff': round(avg_diff, 2),
                'volatility': round(volatility, 2),
                'search_volume': volume,
                'interested_agencies': agencies,
                'opportunity_type': opportunity_type,
                'priority': priority,
                'competitiveness_score': self._calculate_market_score(avg_diff, volatility, volume)
            }
        
        return opportunities
    
    def _calculate_market_score(self, avg_diff: float, volatility: float, volume: int) -> float:
        """Calcular score de competitividad por mercado"""
        
        # Normalizar componentes
        price_component = max(0, 50 - avg_diff)  # Menor diferencia = mejor
        stability_component = max(0, 50 - volatility)  # Menor volatilidad = mejor
        volume_component = min(50, volume / 10)  # Más volumen = mejor, cap en 50
        
        score = (price_component + stability_component + volume_component) / 3
        return round(score, 2)
    
    def identify_pricing_anomalies(self, hotel_name: str, threshold: float = 2.0) -> List[Dict]:
        """Identificar anomalías de precios (outliers)"""
        
        data = self.dp.hound_external[self.dp.hound_external['Nombre_Hotel'] == hotel_name]
        
        if data.empty:
            return []
        
        anomalies = []
        
        # Calcular z-score para identificar outliers
        data['z_score'] = np.abs((data['price_diff_pct'] - data['price_diff_pct'].mean()) / 
                                data['price_diff_pct'].std())
        
        outliers = data[data['z_score'] > threshold]
        
        for _, row in outliers.iterrows():
            anomalies.append({
                'date': row['check_in'].strftime('%Y-%m-%d'),
                'pos': row['PoS'],
                'adults': row['adults'],
                'children': row['children'],
                'los': row['los'],
                'price_diff_pct': round(row['price_diff_pct'], 2),
                'z_score': round(row['z_score'], 2),
                'agency': row['agency_name'],
                'our_price': row['price_despegar (USD)'],
                'competitor_price': row['buyers_best_price_competitor_total (USD)']
            })
        
        return sorted(anomalies, key=lambda x: abs(x['price_diff_pct']), reverse=True)
    
    def generate_recommendations(self, hotel_name: str) -> List[str]:
        """Generar recomendaciones específicas"""
        
        summary = self.dp.get_hotel_summary(hotel_name)
        opportunities = self.analyze_market_opportunities(hotel_name)
        
        recommendations = []
        
        # Recomendaciones basadas en score general
        score = summary.get('competitiveness_score', 0)
        if score < 30:
            recommendations.append("🔴 Prioridad ALTA: Revisar estrategia de pricing general")
        elif score < 60:
            recommendations.append("🟡 Prioridad MEDIA: Optimizar precios en mercados específicos")
        else:
            recommendations.append("🟢 Prioridad BAJA: Mantener monitoreo y ajustes menores")
        
        # Recomendaciones por mercado
        high_priority_markets = [pos for pos, data in opportunities.items() 
                               if data.get('priority') == 'Alta']
        
        if high_priority_markets:
            recommendations.append(f"📍 Mercados críticos: {', '.join(high_priority_markets)}")
        
        # Recomendaciones específicas
        avg_diff = summary.get('avg_price_difference_pct', 0)
        if avg_diff > 15:
            recommendations.append("💰 Considerar reducción de precios del 5-10%")
        elif avg_diff < -10:
            recommendations.append("📈 Oportunidad de incrementar precios del 3-7%")
        
        # Recomendaciones de disponibilidad
        competitive_ratio = summary.get('competitive_positions', 0) / max(1, summary.get('total_searches', 1))
        if competitive_ratio < 0.3:
            recommendations.append("🎯 Mejorar competitividad: menos del 30% de posiciones ganadoras")
        
        return recommendations
    
    def create_market_heatmap(self, hotel_name: str):
        """Crear mapa de calor de competitividad por mercado"""
        
        data = self.dp.hound_external[self.dp.hound_external['Nombre_Hotel'] == hotel_name]
        
        if data.empty:
            return None
        
        # Preparar datos para heatmap
        heatmap_data = data.groupby(['PoS', 'los']).agg({
            'price_diff_pct': 'mean'
        }).reset_index()
        
        # Pivot para heatmap
        pivot_data = heatmap_data.pivot(index='PoS', columns='los', values='price_diff_pct')
        
        # Crear heatmap con plotly
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale='RdYlGn_r',
            zmid=0,
            colorbar=dict(title="Diferencia de Precio (%)")
        ))
        
        fig.update_layout(
            title=f'Mapa de Competitividad: {hotel_name}',
            xaxis_title='Duración de Estadía (noches)',
            yaxis_title='Mercado (PoS)',
            height=400
        )
        
        return fig
