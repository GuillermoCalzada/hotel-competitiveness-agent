import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class DataProcessor:
    """Procesador de datos para análisis de competitividad hotelera"""
    
    def __init__(self):
        self.hound_internal = None
        self.hound_external = None  
        self.extranet = None
        
    def load_data(self, internal_path: str, external_path: str, extranet_path: str):
        """Cargar los tres datasets principales"""
        try:
            self.hound_internal = pd.read_csv(internal_path)
            self.hound_external = pd.read_csv(external_path)
            self.extranet = pd.read_csv(extranet_path)
            
            # Limpiar y preparar datos
            self._clean_data()
            return True
        except Exception as e:
            print(f"Error cargando datos: {e}")
            return False
    
    def _clean_data(self):
        """Limpiar y preparar los datasets"""
        
        # 1. Hound Internal - limpiar precios con comas
        price_columns = ['PamBaseRate ($)', 'ExpBaseRate ($)', 'HBGBaseRate ($)']
        for col in price_columns:
            if col in self.hound_internal.columns:
                self.hound_internal[col] = self.hound_internal[col].astype(str).str.replace(',', '').astype(float)
        
        # 2. Hound External - convertir fechas
        if 'check_in' in self.hound_external.columns:
            self.hound_external['check_in'] = pd.to_datetime(self.hound_external['check_in'], dayfirst=True)
            self.hound_external['check_out'] = pd.to_datetime(self.hound_external['check_out'], dayfirst=True)
        
        # 3. Calcular precio por noche
        self.hound_external['price_per_night_despegar'] = self.hound_external['price_despegar (USD)'] / self.hound_external['los']
        self.hound_external['price_per_night_competitor'] = self.hound_external['buyers_best_price_competitor_total (USD)'] / self.hound_external['los']
        
        # 4. Calcular diferencias porcentuales
        self.hound_external['price_diff_pct'] = (
            (self.hound_external['buyers_best_price_competitor_total (USD)'] - self.hound_external['price_despegar (USD)']) / 
            self.hound_external['price_despegar (USD)'] * 100
        )
    
    def validate_b2b_configuration(self, hotel_name: str = None) -> Dict:
        """Validar configuración B2B en Extranet"""
        
        df = self.extranet.copy()
        if hotel_name:
            df = df[df['Hotel'] == hotel_name]
        
        validation_results = {}
        
        for _, row in df.iterrows():
            hotel = row['Hotel']
            
            # Validaciones B2B
            validations = {
                'api_configured': row['Api_Tildado'] in ['Sí', 'Si', '1', 1],
                'html_configured': row['HTML_Tildado'] in ['Sí', 'Si', '1', 1],
                'wrapper_configured': row['availableWrapper'] in ['1', 1, 'Sí', 'Si'],
                'prepago_configured': row['PrepagoActivo'] in ['Sí', 'Si', '1', 1],
                'rate_type_valid': row['Rate_type'] != 'STANDALONE',
                'has_markets': bool(str(row['Pos_Tildado']).strip()),
                'good_availability': float(row['Disponibilidad']) >= 0.90
            }
            
            # Calcular score de configuración
            config_score = sum(validations.values()) / len(validations) * 100
            
            # Determinar status general
            critical_issues = []
            if not validations['api_configured']:
                critical_issues.append('API no configurado')
            if not validations['html_configured']:
                critical_issues.append('HTML no configurado')
            if not validations['wrapper_configured']:
                critical_issues.append('Wrapper no habilitado')
            if not validations['prepago_configured']:
                critical_issues.append('Prepago no activo')
            if not validations['rate_type_valid']:
                critical_issues.append('Rate type STANDALONE no recomendado')
            
            # Status general
            if config_score >= 85:
                status = 'optimal'
                priority = 'low'
            elif config_score >= 70:
                status = 'good'
                priority = 'medium'
            else:
                status = 'critical'
                priority = 'high'
            
            validation_results[hotel] = {
                'config_score': round(config_score, 1),
                'status': status,
                'priority': priority,
                'validations': validations,
                'critical_issues': critical_issues,
                'markets_configured': str(row['Pos_Tildado']).split(', '),
                'rate_type': row['Rate_type'],
                'availability': float(row['Disponibilidad'])
            }
        
        return validation_results
    
    def get_b2b_recommendations(self, hotel_name: str) -> List[str]:
        """Generar recomendaciones específicas de configuración B2B"""
        
        validation = self.validate_b2b_configuration(hotel_name)
        
        if hotel_name not in validation:
            return ["Hotel no encontrado en datos de extranet"]
        
        hotel_config = validation[hotel_name]
        recommendations = []
        
        # Recomendaciones críticas
        for issue in hotel_config['critical_issues']:
            if 'API' in issue:
                recommendations.append("🔴 CRÍTICO: Habilitar Api_Tildado en extranet")
            elif 'HTML' in issue:
                recommendations.append("🔴 CRÍTICO: Habilitar HTML_Tildado en extranet")
            elif 'Wrapper' in issue:
                recommendations.append("🔴 CRÍTICO: Activar availableWrapper en extranet")
            elif 'Prepago' in issue:
                recommendations.append("🔴 CRÍTICO: Activar PrepagoActivo en extranet")
            elif 'STANDALONE' in issue:
                recommendations.append("🟠 IMPORTANTE: Cambiar Rate_type de STANDALONE a PACKAGE u OPAQUE")
        
        # Recomendaciones de disponibilidad
        if hotel_config['availability'] < 0.90:
            recommendations.append(f"🟡 MEJORAR: Disponibilidad actual {hotel_config['availability']:.1%}, objetivo >90%")
        
        # Recomendaciones de mercados
        markets = hotel_config['markets_configured']
        if len(markets) < 3:
            recommendations.append("🟡 AMPLIAR: Considerar habilitar más mercados (PoS)")
        
        # Status general
        score = hotel_config['config_score']
        if score < 70:
            recommendations.append("⚠️ URGENTE: Configuración B2B deficiente, revisar con equipo técnico")
        elif score < 85:
            recommendations.append("📈 OPTIMIZAR: Oportunidad de mejorar configuración B2B")
        
        return recommendations if recommendations else ["✅ Configuración B2B óptima"]
    
    def calculate_availability_metrics(self) -> pd.DataFrame:
        """Calcular métricas de disponibilidad"""
        
        # Disponibilidad por hotel desde extranet
        availability_base = self.extranet[['Hotel', 'Disponibilidad', 'Pos_Tildado']].copy()
        
        # Agregar validaciones B2B
        b2b_validations = self.validate_b2b_configuration()
        
        for hotel in availability_base['Hotel']:
            if hotel in b2b_validations:
                availability_base.loc[availability_base['Hotel'] == hotel, 'B2B_Score'] = b2b_validations[hotel]['config_score']
                availability_base.loc[availability_base['Hotel'] == hotel, 'B2B_Status'] = b2b_validations[hotel]['status']
        
        # Contar ofertas en hound_external por hotel y PoS
        external_offers = self.hound_external.groupby(['Nombre_Hotel', 'PoS']).size().reset_index(name='offers_count')
        
        # Calcular disponibilidad relativa vs competidores
        competitor_availability = self.hound_external.groupby('Nombre_Hotel').agg({
            'buyers_best_price_competitor_total (USD)': 'count'
        }).reset_index()
        competitor_availability.columns = ['Nombre_Hotel', 'competitor_offers']
        
        return availability_base, external_offers, competitor_availability
    
    def identify_price_patterns(self, hotel_name: str = None) -> Dict:
        """Identificar patrones de precios significativos"""
        
        df = self.hound_external.copy()
        if hotel_name:
            df = df[df['Nombre_Hotel'] == hotel_name]
        
        patterns = {}
        
        # 1. Patrones por PoS
        pos_patterns = df.groupby('PoS').agg({
            'price_diff_pct': ['mean', 'std', 'count'],
            'price_despegar (USD)': 'mean',
            'buyers_best_price_competitor_total (USD)': 'mean'
        }).round(2)
        
        # 2. Patrones por combinación de pasajeros
        pax_patterns = df.groupby(['adults', 'children']).agg({
            'price_diff_pct': ['mean', 'std', 'count'],
            'price_despegar (USD)': 'mean'
        }).round(2)
        
        # 3. Patrones temporales (por mes)
        df['check_in_month'] = df['check_in'].dt.month
        temporal_patterns = df.groupby('check_in_month').agg({
            'price_diff_pct': ['mean', 'std', 'count']
        }).round(2)
        
        # 4. Patrones por duración de estadía
        los_patterns = df.groupby('los').agg({
            'price_diff_pct': ['mean', 'std', 'count'],
            'price_per_night_despegar': 'mean',
            'price_per_night_competitor': 'mean'
        }).round(2)
        
        return {
            'pos_patterns': pos_patterns,
            'pax_patterns': pax_patterns,
            'temporal_patterns': temporal_patterns,
            'los_patterns': los_patterns
        }
    
    def calculate_competitiveness_score(self, hotel_name: str) -> float:
        """Calcular score único de competitividad"""
        
        # Filtrar datos del hotel
        external_data = self.hound_external[self.hound_external['Nombre_Hotel'] == hotel_name]
        
        if external_data.empty:
            return 0.0
        
        # Componentes del score
        
        # 1. Diferencia de precio promedio (peso: 30%)
        avg_price_diff = external_data['price_diff_pct'].mean()
        price_score = max(0, min(100, 50 - avg_price_diff))  # Invertir: menor diferencia = mejor score
        
        # 2. Disponibilidad relativa (peso: 25%)
        total_searches = len(external_data)
        unique_combinations = external_data[['PoS', 'check_in', 'check_out', 'adults', 'children']].drop_duplicates()
        availability_ratio = len(unique_combinations) / max(1, total_searches)
        availability_score = availability_ratio * 100
        
        # 3. Consistencia (peso: 25%) - menor volatilidad = mejor
        price_volatility = external_data['price_diff_pct'].std()
        consistency_score = max(0, 100 - price_volatility)
        
        # 4. Configuración B2B (peso: 20%) - NUEVO
        b2b_validation = self.validate_b2b_configuration(hotel_name)
        b2b_score = b2b_validation.get(hotel_name, {}).get('config_score', 0) if b2b_validation else 0
        
        # Score final ponderado
        final_score = (
            price_score * 0.30 + 
            availability_score * 0.25 + 
            consistency_score * 0.25 +
            b2b_score * 0.20
        )
        
        return round(final_score, 2)
    
    def cross_market_analysis(self, external_price: float, hotel_name: str) -> Dict:
        """Analizar si precio externo corresponde a algún otro mercado"""
        
        # Obtener tarifas internas del hotel
        internal_data = self.hound_internal[self.hound_internal['Nombre_Hotel'] == hotel_name]
        
        if internal_data.empty:
            return {"match_found": False, "analysis": "Hotel no encontrado en datos internos"}
        
        # Calcular diferencias con cada PoS/mercado
        matches = []
        
        for _, row in internal_data.iterrows():
            pam_rate = row['PamBaseRate ($)']
            diff_percentage = abs((external_price - pam_rate) / pam_rate * 100)
            
            if diff_percentage <= 15:  # Threshold de similitud
                matches.append({
                    'pos': row['PoS'],
                    'pam_rate': pam_rate,
                    'external_price': external_price,
                    'difference_pct': round(diff_percentage, 2),
                    'currency': row['contractcurrencybase_pam']
                })
        
        return {
            "match_found": len(matches) > 0,
            "matches": sorted(matches, key=lambda x: x['difference_pct']),
            "analysis": f"Encontrados {len(matches)} mercados similares" if matches else "No se encontraron mercados similares"
        }
    
    def simulate_conversion_impact(self, hotel_name: str, price_change_pct: float) -> Dict:
        """Simular impacto en conversión por cambio de precio"""
        
        # Datos base del hotel
        external_data = self.hound_external[self.hound_external['Nombre_Hotel'] == hotel_name]
        
        if external_data.empty:
            return {"error": "Hotel no encontrado"}
        
        # Calcular métricas actuales
        current_avg_diff = external_data['price_diff_pct'].mean()
        current_competitive_positions = (external_data['price_diff_pct'] < 0).sum()
        total_positions = len(external_data)
        
        # Simular nuevo precio
        new_price_diff = current_avg_diff + price_change_pct
        
        # Estimar cambio en posiciones competitivas (mejorado)
        elasticity = -2.0
        competitiveness_change = price_change_pct * elasticity
        
        new_competitive_positions = min(total_positions, 
            max(0, current_competitive_positions + (competitiveness_change / 100) * total_positions))
        
        # Considerar configuración B2B en la simulación
        b2b_validation = self.validate_b2b_configuration(hotel_name)
        b2b_multiplier = 1.0
        if b2b_validation and hotel_name in b2b_validation:
            b2b_score = b2b_validation[hotel_name]['config_score']
            b2b_multiplier = 0.5 + (b2b_score / 100) * 0.5  # Factor 0.5-1.0 basado en config
        
        # Estimar impacto en conversión (mejorado)
        conversion_multiplier = 0.5 * b2b_multiplier
        estimated_conversion_change = competitiveness_change * conversion_multiplier
        
        return {
            "current_avg_diff_pct": round(current_avg_diff, 2),
            "new_avg_diff_pct": round(new_price_diff, 2),
            "current_competitive_positions": current_competitive_positions,
            "new_competitive_positions": round(new_competitive_positions),
            "estimated_conversion_change_pct": round(estimated_conversion_change, 2),
            "total_positions": total_positions,
            "b2b_config_impact": round((b2b_multiplier - 1) * 100, 1)
        }
    
    def get_hotel_summary(self, hotel_name: str) -> Dict:
        """Obtener resumen completo de un hotel"""
        
        # Datos básicos
        external_data = self.hound_external[self.hound_external['Nombre_Hotel'] == hotel_name]
        internal_data = self.hound_internal[self.hound_internal['Nombre_Hotel'] == hotel_name]
        extranet_data = self.extranet[self.extranet['Hotel'] == hotel_name]
        
        summary = {
            "hotel_name": hotel_name,
            "total_external_records": len(external_data),
            "total_internal_records": len(internal_data),
            "markets_pos": list(external_data['PoS'].unique()) if not external_data.empty else [],
            "competitiveness_score": self.calculate_competitiveness_score(hotel_name)
        }
        
        if not external_data.empty:
            summary.update({
                "avg_price_difference_pct": round(external_data['price_diff_pct'].mean(), 2),
                "price_volatility": round(external_data['price_diff_pct'].std(), 2),
                "competitive_positions": (external_data['price_diff_pct'] < 0).sum(),
                "total_searches": len(external_data),
                "agencies_interested": external_data['agency_name'].nunique()
            })
        
        if not extranet_data.empty:
            summary["availability"] = float(extranet_data['Disponibilidad'].iloc[0])
            
            # Agregar información B2B
            b2b_validation = self.validate_b2b_configuration(hotel_name)
            if hotel_name in b2b_validation:
                summary["b2b_config"] = b2b_validation[hotel_name]
        
        return summary

    def get_available_hotels(self) -> List[str]:
        """Obtener lista de hoteles disponibles"""
        if self.hound_external is not None:
            return sorted(self.hound_external['Nombre_Hotel'].unique().tolist())
        return []
    
    def get_configuration_dashboard_data(self) -> Dict:
        """Obtener datos para dashboard de configuración"""
        
        b2b_validations = self.validate_b2b_configuration()
        
        dashboard_data = {
            'total_hotels': len(b2b_validations),
            'well_configured': sum(1 for config in b2b_validations.values() if config['status'] == 'optimal'),
            'needs_attention': sum(1 for config in b2b_validations.values() if config['status'] == 'good'),
            'critical_issues': sum(1 for config in b2b_validations.values() if config['status'] == 'critical'),
            'avg_config_score': round(sum(config['config_score'] for config in b2b_validations.values()) / len(b2b_validations), 1),
            'hotels_detail': b2b_validations
        }
        
        return dashboard_data
