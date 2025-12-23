# 🏨 Hotel Competitiveness Agent

Un agente de IA conversacional para análisis de competitividad hotelera, desarrollado con Python y Streamlit. Incluye validación de configuración B2B y análisis integral de extranet.

## 🚀 Características Principales

### 💰 Análisis de Competitividad
- **Score único (0-100)** que combina precio, disponibilidad, consistencia y configuración B2B
- **Identificación de patrones** por PoS, pasajeros, fechas y duración
- **Detección de disparidades** significativas vs ruido puntual

### ⚙️ Validación de Configuración B2B
- **Verificación automática** de configuraciones en extranet
- **Validación de campos críticos**: Api_Tildado, HTML_Tildado, availableWrapper, PrepagoActivo
- **Control de Rate_type**: Detecta configuraciones problemáticas (STANDALONE)
- **Verificación de mercados**: Valida que los PoS estén habilitados correctamente

### 📊 Análisis Multi-dimensional
- **Por Mercado (PoS)**: AR, BR, MX, US, etc.
- **Por Pasajeros**: Adultos y niños
- **Por Fechas**: Patrones temporales y estacionalidad
- **Por Duración**: Análisis por número de noches
- **Por Configuración**: Impacto de setup B2B en competitividad

### 🎯 Funcionalidades Avanzadas
- **Cross-Market Analysis**: Detecta si tarifas externas corresponden a otros mercados
- **Simulador de Conversión**: Estima impacto de cambios de precio considerando configuración B2B
- **Recomendaciones IA**: Estrategias personalizadas por hotel incluyendo config técnica
- **Chat Interactivo**: Interface conversacional natural con detección de intenciones

## 📁 Estructura del Proyecto

```
hotel-competitiveness-agent/
├── 📁 src/
│   ├── data_processor.py      # Procesamiento de datos + validaciones B2B
│   ├── competitive_analyzer.py # Análisis y visualizaciones
│   ├── hotel_agent.py         # Agente conversacional
│   └── utils.py               # Utilidades
├── 📁 streamlit_app/
│   └── main.py                # Aplicación web
├── 📁 data/                   # Datos de ejemplo
│   ├── sample_hound_internal.csv
│   ├── sample_hound_external.csv
│   ├── sample_extranet.csv
│   └── README.md
├── 📁 .streamlit/
│   └── config.toml            # Configuración de tema
├── requirements.txt           # Dependencias
├── README.md                  # Este archivo
└── setup.py                   # Configuración del paquete
```

## 📊 Fuentes de Datos

### 1. Hound Internal
- **Descripción**: Competitividad interna vs proveedores
- **Contenido**: Tarifas sin impuestos ni comisiones (PamBaseRate, ExpBaseRate, HBGBaseRate)
- **Formato**: 1 fila = 1 búsqueda única (2 adultos)
- **Moneda**: Múltiples (contractcurrencybase_pam)

### 2. Hound External  
- **Descripción**: Comparación vs competidores externos
- **Contenido**: Precios finales con impuestos/comisiones en USD
- **Formato**: 1 fila = 1 agencia interesada
- **Combinaciones**: Diferentes adultos/niños, múltiples agencias

### 3. Extranet ⭐ **ACTUALIZADO**
- **Descripción**: Configuración real de hoteles + validaciones B2B
- **Campos críticos B2B**:
  - `Api_Tildado`: Debe ser 'Sí' o '1'
  - `HTML_Tildado`: Debe ser 'Sí' o '1'  
  - `availableWrapper`: Debe ser '1'
  - `PrepagoActivo`: Debe ser 'Sí' o '1'
  - `Rate_type`: Debe ser diferente a 'STANDALONE'
  - `Pos_Tildado`: Mercados habilitados

## 🛠️ Instalación y Uso

### Prerrequisitos
```bash
Python 3.8+
pip
git
```

### Instalación Local

1. **Clonar repositorio**
```bash
git clone https://github.com/tuusuario/hotel-competitiveness-agent.git
cd hotel-competitiveness-agent
```

2. **Crear entorno virtual**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Ejecutar aplicación**
```bash
streamlit run streamlit_app/main.py
```

### Despliegue en Streamlit Cloud

1. **Fork este repositorio**
2. **Ir a [share.streamlit.io](https://share.streamlit.io)**
3. **Conectar con GitHub**
4. **Seleccionar:**
   - Repository: `tu-usuario/hotel-competitiveness-agent`
   - Branch: `main`
   - Main file path: `streamlit_app/main.py`

## 🤖 Guía de Uso del Agente

### Comandos Básicos

#### Selección de Hotel
```
"seleccionar hotel Paradise Resort"
"ver hoteles disponibles"
"cambiar a Ocean View Grand"
```

#### Análisis de Competitividad
```
"análisis de competitividad"
"mostrar score"
"¿qué tal está mi hotel?"
```

#### Comparación de Precios
```
"comparar precios"
"diferencias por mercado"
"¿estamos más caros?"
```

#### ⭐ Configuración B2B (NUEVO)
```
"revisar configuración B2B"
"estado de extranet"
"configuración api"
"problemas de configuración"
```

#### Análisis por Mercados
```
"analizar mercados"
"patrones por país"
"oportunidades por PoS"
```

#### Recomendaciones
```
"dame recomendaciones"
"qué debo hacer"
"estrategia de precios"
```

#### Simulaciones
```
"simular -10%"  # Reducir precios 10%
"simular +5%"   # Aumentar precios 5%
"impacto de cambio"
```

#### Cross-Market Analysis
```
"análisis cross market"
"precios en otros mercados"
"correlaciones"
```

### Ejemplos de Conversación

```
👤 Usuario: "Hola, quiero analizar el Paradise Resort"

🤖 Agente: "✅ Hotel seleccionado: Paradise Resort
📊 Score de competitividad: 78/100
• Diferencia promedio: +3.2%
• Mercados activos: 4
• Configuración B2B: ✅ 95/100
¿Qué te gustaría analizar?"

👤 Usuario: "¿Está bien configurado para B2B?"

🤖 Agente: "⚙️ Configuración B2B - Paradise Resort
✅ Status: ÓPTIMA - Score: 95/100

🔧 Estado de Configuraciones:
• API Tildado: ✅
• HTML Tildado: ✅  
• Available Wrapper: ✅
• Prepago Activo: ✅
• Rate Type válido: ✅ (PACKAGE)
• Disponibilidad: 97%

🌍 Mercados Habilitados: AR, BR, CL, MX"

👤 Usuario: "Simular bajar precios 8%"

🤖 Agente: "📊 Simulación de Impacto:
💰 Cambio: -8%
📈 Nueva diferencia: -4.8%
🎯 Posiciones ganadoras: 65 → 89
💡 Impacto estimado: +14.2% conversión
• Factor configuración B2B: +2.5%"
```

## 📊 Validaciones B2B

### Configuración Óptima ✅
- **Api_Tildado**: 'Sí' o '1'
- **HTML_Tildado**: 'Sí' o '1'
- **availableWrapper**: '1'
- **PrepagoActivo**: 'Sí' o '1'
- **Rate_type**: 'PACKAGE' o 'OPAQUE' (NO 'STANDALONE')
- **Pos_Tildado**: Mercados objetivo habilitados
- **Disponibilidad**: ≥ 90%

### Issues Críticos ❌
- API no configurado → Sin acceso B2B
- HTML no habilitado → Problemas de visualización
- Wrapper deshabilitado → Integración incompleta
- Prepago inactivo → Limitaciones de pago
- Rate type STANDALONE → Configuración subóptima

### Recomendaciones Automáticas
- **Críticas**: Habilitar configuraciones faltantes
- **Importantes**: Cambiar rate type problemático
- **Optimización**: Mejorar disponibilidad y ampliar mercados

## 📈 Métricas y Algoritmos

### Score de Competitividad (Actualizado)
```python
score = (precio_component * 0.30 + 
         disponibilidad_component * 0.25 + 
         consistencia_component * 0.25 +
         configuracion_b2b * 0.20)  # NUEVO
```

### Validación B2B
```python
config_score = (api_ok + html_ok + wrapper_ok + 
                prepago_ok + rate_valid + markets_ok + 
                availability_ok) / 7 * 100
```

### Simulador de Conversión (Mejorado)
- **Elasticidad**: -1% precio = +2% competitividad
- **Factor B2B**: Multiplicador basado en configuración (0.5-1.0)
- **Conversión**: Ajustada por setup técnico

## 🎯 Datos de Ejemplo

El proyecto incluye datos ficticios para demostración:

### Hoteles de Ejemplo:
1. **Hotel Paradise Resort** ✅ - Bien configurado, PACKAGE
2. **Ocean View Grand** ✅ - Bien configurado, OPAQUE  
3. **Mountain Lodge Premium** ❌ - Mal configurado, STANDALONE
4. **City Center Boutique** ✅ - Bien configurado, PACKAGE
5. **Beachfront Luxury** ⚠️ - Parcialmente configurado

### Configuraciones Variadas:
- **3/5 hoteles** correctamente configurados para B2B
- **2/5 hoteles** con issues críticos
- **Diferentes mercados** y volúmenes de datos
- **Patrones realistas** de competitividad

## 🔧 Configuración y Personalización

### Variables de Configuración
```python
# En data_processor.py
B2B_VALIDATION_FIELDS = {
    'api': ['Api_Tildado', ['Sí', 'Si', '1']],
    'html': ['HTML_Tildado', ['Sí', 'Si', '1']],
    'wrapper': ['availableWrapper', ['1']],
    'prepago': ['PrepagoActivo', ['Sí', 'Si', '1']]
}

COMPETITIVENESS_WEIGHTS = {
    'price': 0.30,
    'availability': 0.25,
    'consistency': 0.25,
    'b2b_config': 0.20  # NUEVO
}
```

### Personalizar Validaciones
```python
# Agregar nuevas validaciones B2B
def custom_b2b_validation(row):
    # Tu lógica personalizada
    return validation_result
```

## 🧪 Datos de Prueba

### Ejecutar con Datos de Ejemplo
```bash
# Los archivos sample_*.csv están incluidos
streamlit run streamlit_app/main.py

# Cargar en la interface:
# 1. sample_hound_internal.csv
# 2. sample_hound_external.csv  
# 3. sample_extranet.csv
```

### Validar Configuraciones
```python
# En Python
from src.data_processor import DataProcessor

dp = DataProcessor()
dp.load_data('data/sample_internal.csv', 'data/sample_external.csv', 'data/sample_extranet.csv')

# Validar configuraciones B2B
validations = dp.validate_b2b_configuration()
print(validations)
```

## 🤝 Contribución

### Roadmap
- [x] Validaciones de configuración B2B
- [x] Score integrado con setup técnico
- [x] Recomendaciones de configuración
- [ ] Alertas automáticas por email
- [ ] Integración con APIs de extranet
- [ ] Modelo ML para predicciones
- [ ] Dashboard ejecutivo
- [ ] Export a Excel/PDF

### Cómo Contribuir
1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/B2BEnhancements`)
3. Commit cambios (`git commit -m 'Add B2B validation system'`)
4. Push al branch (`git push origin feature/B2BEnhancements`)
5. Crear Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 👨‍💻 Autor

**Tu Nombre**
- GitHub: [@tuusuario](https://github.com/tuusuario)
- LinkedIn: [Tu LinkedIn](https://linkedin.com/in/tuperfil)
- Email: tu.email@ejemplo.com

## 🙏 Agradecimientos

- Streamlit por el framework
- Plotly por las visualizaciones
- Pandas por el procesamiento de datos
- La comunidad de desarrolladores de Python

---

⭐ **¿Te gustó el proyecto? ¡Dale una estrella!** ⭐

🏨 **Hotel Competitiveness Agent** - Transformando el análisis de competitividad hotelera con IA
