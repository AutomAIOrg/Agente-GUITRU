#!/bin/bash
# Script para ejecutar diferentes conjuntos de tests

set -e  # Salir si hay errores

echo "🧪 Test Suite - Agente GUITRU"
echo "=============================="
echo ""

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para mostrar uso
show_usage() {
    echo "Uso: ./run_tests.sh [opción]"
    echo ""
    echo "Opciones:"
    echo "  all           - Ejecutar todos los tests"
    echo "  integration   - Solo tests de integración"
    echo "  unit          - Solo tests unitarios"
    echo "  coverage      - Tests con reporte de cobertura"
    echo "  fast          - Solo tests rápidos"
    echo "  repo          - Tests de repositorios"
    echo "  usecase       - Tests de casos de uso"
    echo "  db            - Tests de base de datos"
    echo "  watch         - Ejecutar tests en modo watch (re-ejecuta al cambiar)"
    echo "  help          - Mostrar esta ayuda"
    echo ""
}

# Verificar que pytest esté instalado
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest no está instalado"
    echo "Ejecuta: pip install -r requirements.txt"
    exit 1
fi

# Procesar argumentos
case "${1:-all}" in
    all)
        echo -e "${BLUE}Ejecutando todos los tests...${NC}"
        pytest -v
        ;;
    
    integration)
        echo -e "${BLUE}Ejecutando tests de integración...${NC}"
        pytest -v -m integration
        ;;
    
    unit)
        echo -e "${BLUE}Ejecutando tests unitarios...${NC}"
        pytest -v -m unit
        ;;
    
    coverage)
        echo -e "${BLUE}Ejecutando tests con coverage...${NC}"
        pytest --cov=backend --cov-report=html --cov-report=term
        echo ""
        echo -e "${GREEN}✅ Reporte de coverage generado en: htmlcov/index.html${NC}"
        ;;
    
    fast)
        echo -e "${BLUE}Ejecutando tests rápidos...${NC}"
        pytest -v -m "not slow"
        ;;
    
    repo)
        echo -e "${BLUE}Ejecutando tests de repositorios...${NC}"
        pytest -v backend/tests/integration/test_sql_message_repository.py
        ;;
    
    usecase)
        echo -e "${BLUE}Ejecutando tests de casos de uso...${NC}"
        pytest -v backend/tests/integration/test_process_incoming_message_use_case.py
        ;;
    
    db)
        echo -e "${BLUE}Ejecutando tests de base de datos...${NC}"
        pytest -v backend/tests/integration/test_database_connection.py
        ;;
    
    watch)
        echo -e "${BLUE}Ejecutando tests en modo watch...${NC}"
        echo -e "${YELLOW}Presiona Ctrl+C para salir${NC}"
        pytest-watch
        ;;
    
    help)
        show_usage
        ;;
    
    *)
        echo -e "${YELLOW}⚠️  Opción desconocida: $1${NC}"
        echo ""
        show_usage
        exit 1
        ;;
esac

# Si llegamos aquí, los tests pasaron
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Tests completados exitosamente${NC}"
else
    echo ""
    echo -e "${YELLOW}⚠️  Algunos tests fallaron${NC}"
    exit 1
fi
