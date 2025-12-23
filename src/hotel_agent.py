import json
from typing import Dict, List, Optional
from dataclasses import dataclass
import pandas as pd

@dataclass
class AgentResponse:
    """Estructura de respuesta del agente"""
    message: str
    data: Optional[Dict] = None
    chart: Optional[object] = None
    recommendations: Optional[List[str]] = None

class HotelAgent:
    """Agente conversacional para análisis de competitividad hotelera"""
    
    def __init__(self, data_processor, competitive_analyzer):
        self.dp = data_processor
        self.ca = competitive_analyzer
        self.context = {}
        self.current_hotel = None
        
    def process_query(self, user_input: str) -> AgentResponse:
        """Procesar consulta del usuario y generar respuesta"""
        
        user_input = user_input.lower().strip()
        
        # Detectar intención
        intent = self._detect_intent(user_input)
        
        # Procesar según intención
        if intent == "hotel_selection":
            return self._handle_hotel_selection(user_input)
        elif intent == "competitiveness_analysis":
            return self._handle_competitiveness_analysis(user_input)
        elif intent == "price_comparison":
            return self._handle_price_comparison(user_input)
        elif intent == "market_analysis":
            return self._handle_market_analysis(user_input)
        elif intent == "recommendations":
            return self._handle_recommendations(user_input)
        elif intent == "simulation":
            return self._handle_simulation(user_input)
        elif intent == "cross_market":
            return self._handle_cross_market_analysis(user_input)
        elif intent == "b2b_configuration":
            return self._handle_b2b_configuration(user_input)
        elif intent == "help":
            return self._handle_help()
        else:
            return self._handle_general_query(user_input)
    
    def _detect_intent(self, user_input: str) -> str:
        """Detectar la intención del usuario"""
        
        # Keywords para cada intención
        intents = {
            "hotel_selection": ["hotel", "seleccionar", "elegir", "cambiar hotel", "ver hoteles"],
            "competitiveness_analysis": ["competitividad", "score", "análisis", "posición", "competitivo"],
            "price_comparison": ["precio", "tarifa", "comparar", "diferencia", "más barato", "más caro"],
            "market_analysis": ["mercado", "pos", "país", "oportunidad", "patrón"],
            "recommendations": ["recomendación", "sugerir", "qué hacer", "mejorar", "estrategia"],
            "simulation": ["simular", "simulación", "cambiar precio", "impacto", "conversión"],
            "cross_market": ["cross market", "otro mercado", "tarifa similar", "comparar mercados"],
            "b2b_configuration": ["configuración", "extranet", "b2b", "api", "html", "wrapper", "prepago", "rate type"],
            "help": ["ayuda", "help", "qué puedes hacer", "comandos", "funciones"]
        }
        
        # Buscar matches
        for intent, keywords in intents.items():
            if any(keyword in user_input for keyword in keywords):
                return intent
        
        return "general"
    
    def _handle_hotel_selection(self, user_input: str) -> AgentResponse:
        """Manejar selección de hotel"""
        
        available_hotels = self.dp.get_available_hotels()
        
        if not available_hotels:
            return AgentResponse(
                message="❌ No hay datos de hoteles disponibles. Por favor, carga los datos primero."
            )
        
        # Si menciona un hotel específico, intentar seleccionarlo
        for hotel in available_hotels:
            if any(word in hotel.lower() for word in user_input.split()):
                self.current_hotel = hotel
                summary = self.dp.get_hotel_summary(hotel)
                
                # Agregar información de configuración B2B
                b2b_info = ""
                if 'b2b_config' in summary:
                    config = summary['b2b_config']
                    status_emoji = "✅" if config['status'] == 'optimal' else "🟡" if config['status'] == 'good' else "🔴"
                    b2b_info = f"\n• Configuración B2B: {status_emoji} {config['config_score']}/100"
                
                return AgentResponse(
                    message=f"✅ Hotel seleccionado: **{hotel}**\n\n"
                           f"📊 **Resumen rápido:**\n"
                           f"• Score de competitividad: {summary.get('competitiveness_score', 'N/A')}/100\n"
                           f"• Diferencia promedio de precio: {summary.get('avg_price_difference_pct', 'N/A')}%\n"
                           f"• Mercados activos: {len(summary.get('markets_pos', []))}\n"
                           f"• Búsquedas totales: {summary.get('total_searches', 'N/A'):,}{b2b_info}\n\n"
                           f"¿Qué te gustaría analizar?",
                    data=summary
                )
        
        # Si no encuentra hotel específico, mostrar lista
        hotel_list = "\n".join([f"• {hotel}" for hotel in available_hotels])
        
        return AgentResponse(
            message=f"🏨 **Hoteles disponibles:**\n\n{hotel_list}\n\n"
                   f"Por favor, menciona el nombre del hotel que quieres analizar."
        )
    
    def _handle_competitiveness_analysis(self, user_input: str) -> AgentResponse:
        """Manejar análisis de competitividad"""
        
        if not self.current_hotel:
            return AgentResponse(
                message="❌ Primero selecciona un hotel. Usa: 'seleccionar hotel [nombre]'"
            )
        
        # Calcular análisis completo
        summary = self.dp.get_hotel_summary(self.current_hotel)
        patterns = self.dp.identify_price_patterns(self.current_hotel)
        opportunities = self.ca.analyze_market_opportunities(self.current_hotel)
        
        # Crear mensaje detallado
        score = summary.get('competitiveness_score', 0)
        if score >= 70:
            status = "🟢 **EXCELENTE**"
        elif score >= 50:
            status = "🟡 **REGULAR**"
        else:
            status = "🔴 **CRÍTICO**"
        
        message = f"📈 **Análisis de Competitividad - {self.current_hotel}**\n\n"
        message += f"{status} - Score: **{score}/100**\n\n"
        
        message += f"📊 **Métricas Clave:**\n"
        message += f"• Diferencia promedio: {summary.get('avg_price_difference_pct', 0):.1f}%\n"
        message += f"• Posiciones competitivas: {summary.get('competitive_positions', 0)}/{summary.get('total_searches', 0)}\n"
        message += f"• Volatilidad de precios: {summary.get('price_volatility', 0):.1f}%\n"
        message += f"• Agencias interesadas: {summary.get('agencies_interested', 0)}\n"
        
        # Información de configuración B2B
        if 'b2b_config' in summary:
            config = summary['b2b_config']
            status_emoji = "✅" if config['status'] == 'optimal' else "🟡" if config['status'] == 'good' else "🔴"
            message += f"• Configuración B2B: {status_emoji} {config['config_score']}/100\n"
            
            if config['critical_issues']:
                message += f"  ⚠️  Issues críticos: {len(config['critical_issues'])}\n"
        
        message += "\n"
        
        # Top 3 mercados críticos
        critical_markets = sorted(opportunities.items(), 
                                key=lambda x: x[1]['avg_price_diff'], reverse=True)[:3]
        
        if critical_markets:
            message += f"🎯 **Mercados Prioritarios:**\n"
            for market, data in critical_markets:
                message += f"• **{market}**: {data['avg_price_diff']:+.1f}% ({data['opportunity_type']})\n"
        
        # Crear gráfico
        chart = self.ca.create_competitiveness_dashboard(self.current_hotel)
        
        return AgentResponse(
            message=message,
            data={"summary": summary, "opportunities": opportunities},
            chart=chart
        )
    
    def _handle_price_comparison(self, user_input: str) -> AgentResponse:
        """Manejar comparación de precios"""
        
        if not self.current_hotel:
            return AgentResponse(
                message="❌ Primero selecciona un hotel para comparar precios."
            )
        
        # Análisis de precios por mercado
        data = self.dp.hound_external[self.dp.hound_external['Nombre_Hotel'] == self.current_hotel]
        
        if data.empty:
            return AgentResponse(
                message="❌ No hay datos de precios disponibles para este hotel."
            )
        
        # Estadísticas por PoS
        price_stats = data.groupby('PoS').agg({
            'price_despegar (USD)': 'mean',
            'buyers_best_price_competitor_total (USD)': 'mean',
            'price_diff_pct': ['mean', 'min', 'max']
        }).round(2)
        
        message = f"💰 **Comparación de Precios - {self.current_hotel}**\n\n"
        
        for pos in price_stats.index:
            our_price = price_stats.loc[pos, ('price_despegar (USD)', 'mean')]
            comp_price = price_stats.loc[pos, ('buyers_best_price_competitor_total (USD)', 'mean')]
            avg_diff = price_stats.loc[pos, ('price_diff_pct', 'mean')]
            
            if avg_diff < 0:
                status = "🟢 Ganamos"
            elif avg_diff < 10:
                status = "🟡 Competitivo"
            else:
                status = "🔴 Perdemos"
            
            message += f"**{pos}:** {status}\n"
            message += f"  • Nuestro precio: ${our_price:,.0f}\n"
            message += f"  • Competidores: ${comp_price:,.0f}\n"
            message += f"  • Diferencia: {avg_diff:+.1f}%\n\n"
        
        # Crear gráfico de comparación
        chart = self.ca.create_price_comparison_chart(self.current_hotel)
        
        return AgentResponse(
            message=message,
            chart=chart
        )
    
    def _handle_market_analysis(self, user_input: str) -> AgentResponse:
        """Manejar análisis por mercado"""
        
        if not self.current_hotel:
            return AgentResponse(
                message="❌ Primero selecciona un hotel para analizar mercados."
            )
        
        patterns = self.dp.identify_price_patterns(self.current_hotel)
        opportunities = self.ca.analyze_market_opportunities(self.current_hotel)
        
        message = f"🌍 **Análisis por Mercados - {self.current_hotel}**\n\n"
        
        # Análisis por PoS
        message += "📍 **Por Mercado (PoS):**\n"
        for pos, data in opportunities.items():
            priority_emoji = "🔴" if data['priority'] == 'Alta' else "🟡" if data['priority'] == 'Media' else "🟢"
            message += f"{priority_emoji} **{pos}**: {data['avg_price_diff']:+.1f}% - {data['opportunity_type']}\n"
            message += f"   Volume: {data['search_volume']} búsquedas, {data['interested_agencies']} agencias\n\n"
        
        # Patrones por pasajeros
        if 'pax_patterns' in patterns:
            pax_data = patterns['pax_patterns']
            if not pax_data.empty:
                message += "👥 **Por Combinación de Pasajeros:**\n"
                for (adults, children), row in pax_data.iterrows():
                    avg_diff = row[('price_diff_pct', 'mean')]
                    count = row[('price_diff_pct', 'count')]
                    message += f"• {adults}A + {children}C: {avg_diff:+.1f}% ({count} registros)\n"
        
        # Crear heatmap
        chart = self.ca.create_market_heatmap(self.current_hotel)
        
        return AgentResponse(
            message=message,
            chart=chart,
            data=opportunities
        )
    
    def _handle_recommendations(self, user_input: str) -> AgentResponse:
        """Manejar generación de recomendaciones"""
        
        if not self.current_hotel:
            return AgentResponse(
                message="❌ Primero selecciona un hotel para generar recomendaciones."
            )
        
        recommendations = self.ca.generate_recommendations(self.current_hotel)
        b2b_recommendations = self.dp.get_b2b_recommendations(self.current_hotel)
        
        message = f"💡 **Recomendaciones Estratégicas - {self.current_hotel}**\n\n"
        
        # Recomendaciones de competitividad
        message += "🎯 **Competitividad de Precios:**\n"
        for i, rec in enumerate(recommendations, 1):
            message += f"{i}. {rec}\n\n"
        
        # Recomendaciones de configuración B2B
        if b2b_recommendations:
            message += "⚙️ **Configuración B2B:**\n"
            for i, rec in enumerate(b2b_recommendations, 1):
                message += f"{i}. {rec}\n\n"
        
        # Agregar próximos pasos
        message += "🎯 **Próximos Pasos:**\n"
        message += "• Revisar mercados y configuraciones prioritarias\n"
        message += "• Validar cambios con equipo comercial y técnico\n"
        message += "• Implementar ajustes de forma gradual\n"
        message += "• Monitorear impacto en 1-2 semanas\n"
        
        all_recommendations = recommendations + b2b_recommendations
        
        return AgentResponse(
            message=message,
            recommendations=all_recommendations
        )
    
    def _handle_simulation(self, user_input: str) -> AgentResponse:
        """Manejar simulaciones de cambio de precio"""
        
        if not self.current_hotel:
            return AgentResponse(
                message="❌ Primero selecciona un hotel para simular cambios."
            )
        
        # Intentar extraer porcentaje del input
        import re
        percentage_match = re.search(r'(-?\d+(?:\.\d+)?)%?', user_input)
        
        if not percentage_match:
            return AgentResponse(
                message="💭 **Simulador de Impacto**\n\n"
                       "Para simular un cambio de precios, especifica el porcentaje:\n"
                       "• 'simular -10%' (reducir precios 10%)\n"
                       "• 'simular +5%' (aumentar precios 5%)\n"
                       "• 'simular -7.5%' (reducir precios 7.5%)"
            )
        
        change_pct = float(percentage_match.group(1))
        
        # Ejecutar simulación
        simulation = self.dp.simulate_conversion_impact(self.current_hotel, change_pct)
        
        message = f"📊 **Simulación de Impacto - {self.current_hotel}**\n\n"
        message += f"💰 **Cambio de Precio:** {change_pct:+.1f}%\n\n"
        
        message += f"📈 **Resultados Proyectados:**\n"
        message += f"• Diferencia actual vs competencia: {simulation['current_avg_diff_pct']:+.1f}%\n"
        message += f"• Nueva diferencia proyectada: {simulation['new_avg_diff_pct']:+.1f}%\n"
        message += f"• Posiciones competitivas actuales: {simulation['current_competitive_positions']}/{simulation['total_positions']}\n"
        message += f"• Nuevas posiciones proyectadas: {simulation['new_competitive_positions']}/{simulation['total_positions']}\n"
        message += f"• **Impacto estimado en conversión: {simulation['estimated_conversion_change_pct']:+.1f}%**\n"
        
        # Agregar impacto de configuración B2B si está disponible
        if 'b2b_config_impact' in simulation and simulation['b2b_config_impact'] != 0:
            message += f"• Factor configuración B2B: {simulation['b2b_config_impact']:+.1f}%\n"
        
        message += "\n"
        
        # Interpretación
        if simulation['estimated_conversion_change_pct'] > 5:
            message += "🟢 **Impacto positivo significativo esperado**"
        elif simulation['estimated_conversion_change_pct'] > 0:
            message += "🟡 **Impacto positivo moderado esperado**"
        else:
            message += "🔴 **Considerar riesgos del cambio**"
        
        return AgentResponse(
            message=message,
            data=simulation
        )
    
    def _handle_cross_market_analysis(self, user_input: str) -> AgentResponse:
        """Manejar análisis cross-market"""
        
        if not self.current_hotel:
            return AgentResponse(
                message="❌ Primero selecciona un hotel para análisis cross-market."
            )
        
        # Obtener datos externos
        external_data = self.dp.hound_external[self.dp.hound_external['Nombre_Hotel'] == self.current_hotel]
        
        if external_data.empty:
            return AgentResponse(
                message="❌ No hay datos externos para análisis cross-market."
            )
        
        message = f"🔄 **Análisis Cross-Market - {self.current_hotel}**\n\n"
        
        # Analizar algunas tarifas externas
        sample_analyses = []
        for _, row in external_data.sample(min(3, len(external_data))).iterrows():
            competitor_price = row['buyers_best_price_competitor_total (USD)']
            per_night = competitor_price / row['los']
            
            analysis = self.dp.cross_market_analysis(per_night, self.current_hotel)
            
            if analysis['match_found']:
                sample_analyses.append({
                    'external_price': competitor_price,
                    'per_night': per_night,
                    'matches': analysis['matches'][:2]  # Top 2 matches
                })
        
        if sample_analyses:
            message += "🎯 **Posibles Correlaciones Encontradas:**\n\n"
            
            for analysis in sample_analyses:
                message += f"💰 **Precio externo: ${analysis['external_price']:,.0f} (${analysis['per_night']:.0f}/noche)**\n"
                
                for match in analysis['matches']:
                    message += f"  • Mercado {match['pos']}: ${match['pam_rate']:,.0f} "
                    message += f"(diferencia: {match['difference_pct']:.1f}%)\n"
                
                message += "\n"
        else:
            message += "❌ No se encontraron correlaciones significativas con otros mercados."
        
        return AgentResponse(
            message=message,
            data=sample_analyses
        )
    
    def _handle_b2b_configuration(self, user_input: str) -> AgentResponse:
        """Manejar análisis de configuración B2B"""
        
        if not self.current_hotel:
            return AgentResponse(
                message="❌ Primero selecciona un hotel para revisar configuración B2B."
            )
        
        # Validar configuración B2B del hotel
        validation = self.dp.validate_b2b_configuration(self.current_hotel)
        
        if self.current_hotel not in validation:
            return AgentResponse(
                message="❌ No se encontraron datos de configuración para este hotel."
            )
        
        config = validation[self.current_hotel]
        
        # Determinar emoji de status
        status_emoji = "✅" if config['status'] == 'optimal' else "🟡" if config['status'] == 'good' else "🔴"
        status_text = {"optimal": "ÓPTIMA", "good": "BUENA", "critical": "CRÍTICA"}[config['status']]
        
        message = f"⚙️ **Configuración B2B - {self.current_hotel}**\n\n"
        message += f"{status_emoji} **Status: {status_text}** - Score: {config['config_score']}/100\n\n"
        
        # Detalles de configuración
        message += "🔧 **Estado de Configuraciones:**\n"
        validations = config['validations']
        
        api_status = "✅" if validations['api_configured'] else "❌"
        html_status = "✅" if validations['html_configured'] else "❌"
        wrapper_status = "✅" if validations['wrapper_configured'] else "❌"
        prepago_status = "✅" if validations['prepago_configured'] else "❌"
        rate_status = "✅" if validations['rate_type_valid'] else "❌"
        
        message += f"• API Tildado: {api_status}\n"
        message += f"• HTML Tildado: {html_status}\n"
        message += f"• Available Wrapper: {wrapper_status}\n"
        message += f"• Prepago Activo: {prepago_status}\n"
        message += f"• Rate Type válido: {rate_status} ({config['rate_type']})\n"
        message += f"• Disponibilidad: {config['availability']:.1%}\n"
        
        # Mercados configurados
        message += f"\n🌍 **Mercados Habilitados:**\n"
        for market in config['markets_configured']:
            message += f"• {market}\n"
        
        # Issues críticos
        if config['critical_issues']:
            message += f"\n⚠️ **Issues Críticos:**\n"
            for issue in config['critical_issues']:
                message += f"• {issue}\n"
        
        # Recomendaciones específicas
        recommendations = self.dp.get_b2b_recommendations(self.current_hotel)
        if recommendations and recommendations[0] != "✅ Configuración B2B óptima":
            message += f"\n💡 **Acciones Recomendadas:**\n"
            for i, rec in enumerate(recommendations, 1):
                message += f"{i}. {rec}\n"
        
        return AgentResponse(
            message=message,
            data=config
        )
    
    def _handle_help(self) -> AgentResponse:
        """Mostrar ayuda y comandos disponibles"""
        
        message = """🤖 **Hotel Competitiveness Agent - Guía de Uso**

🏨 **Selección de Hotel:**
• "seleccionar hotel Paradise Resort"
• "ver hoteles disponibles"
• "cambiar a Ocean View Grand"

📊 **Análisis de Competitividad:**
• "análisis de competitividad"
• "mostrar score de competitividad"
• "¿qué tal está mi hotel?"

💰 **Comparación de Precios:**
• "comparar precios"
• "diferencias de precio"
• "¿estamos más caros?"

🌍 **Análisis por Mercados:**
• "analizar mercados"
• "patrones por país"
• "oportunidades por PoS"

⚙️ **Configuración B2B:**
• "revisar configuración B2B"
• "estado de extranet"
• "configuración api"

💡 **Recomendaciones:**
• "dame recomendaciones"
• "qué debo hacer"
• "estrategia de precios"

📈 **Simulaciones:**
• "simular -10%" (reducir 10%)
• "simular +5%" (aumentar 5%)
• "impacto de cambio de precio"

🔄 **Cross-Market:**
• "análisis cross market"
• "precios en otros mercados"

❓ **Otras consultas:**
• Pregunta en lenguaje natural sobre tu hotel
• El agente intentará interpretar tu consulta
"""
        
        return AgentResponse(message=message)
    
    def _handle_general_query(self, user_input: str) -> AgentResponse:
        """Manejar consultas generales"""
        
        if not self.current_hotel:
            return AgentResponse(
                message="🤔 No estoy seguro de qué quieres hacer. "
                       "Primero selecciona un hotel con: **'seleccionar hotel [nombre]'**\n\n"
                       "O escribe **'ayuda'** para ver todos los comandos disponibles."
            )
        
        # Intentar dar una respuesta útil basada en el hotel actual
        message = f"🤔 No estoy seguro de cómo interpretar tu consulta sobre **{self.current_hotel}**.\n\n"
        message += "**Puedes probar:**\n"
        message += "• 'análisis de competitividad'\n"
        message += "• 'comparar precios'\n"
        message += "• 'configuración b2b'\n"
        message += "• 'dame recomendaciones'\n"
        message += "• 'simular -5%'\n\n"
        message += "O escribe **'ayuda'** para ver todas las opciones."
        
        return AgentResponse(message=message)
