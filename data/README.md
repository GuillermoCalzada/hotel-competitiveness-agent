# 📁 Data Directory

Este directorio contiene archivos de datos para el Hotel Competitiveness Agent.

## 🔒 Seguridad de Datos

**IMPORTANTE**: Esta carpeta NO debe contener datos reales de producción cuando subas el proyecto a GitHub público.

## 📊 Archivos de Ejemplo

Los archivos incluidos son datos **FICTICIOS** para demostración:

### `sample_hound_internal.csv`
- **Propósito**: Demostrar funcionalidad de análisis interno
- **Contenido**: 120 registros de ejemplo con hoteles ficticios
- **Uso**: Testing y demonstración de features

### `sample_hound_external.csv` 
- **Propósito**: Demostrar comparación con competencia externa
- **Contenido**: 300 registros de búsquedas simuladas
- **Uso**: Validar algoritmos de competitividad

### `sample_extranet.csv`
- **Propósito**: Demostrar configuración de hoteles
- **Contenido**: 5 hoteles de ejemplo con configuraciones
- **Uso**: Testing de disponibilidad y mercados

## 🚀 Uso en Producción

### Para datos reales:
1. **NO subir archivos reales** al repositorio
2. **Usar la interface de Streamlit** para cargar datos
3. **Los archivos se procesan localmente** y no se almacenan
4. **Cada sesión es independiente** y privada

### Formato esperado:
- **CSV con encoding UTF-8**
- **Headers exactos** como en los samples
- **Fechas en formato DD/MM/YYYY**
- **Precios numéricos** (sin símbolos de moneda en los datos)

## 🧪 Testing Local

Para probar la aplicación localmente con datos de ejemplo:

```bash
# Ejecutar Streamlit
streamlit run streamlit_app/main.py

# Cargar los archivos sample_*.csv en la interface
```

## ⚠️ Disclaimer

Los datos de ejemplo son completamente ficticios y no representan información real de ningún hotel, cadena hotelera o competidor. Son generados aleatoriamente solo para propósitos de demostración técnica.
