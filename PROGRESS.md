# HU Analyzer — Log de Progreso

> Actualizar al final de cada sesión de desarrollo.

---

## Estado del proyecto

**Fase actual:** Sesión 6 completada ✅ — Frontend listo, falta integración final

---

## Módulos

| Módulo | Estado | Notas |
|--------|--------|-------|
| Estructura base del proyecto | ✅ Completo | Sesión 2 |
| Backend: FastAPI setup + CORS | ✅ Completo | Sesión 2 |
| Backend: Pydantic schemas | ✅ Completo | Sesión 2 |
| Backend: Config + variables de entorno | ✅ Completo | Sesión 2 |
| Backend: FileParser (docx, pdf, xlsx, txt) | ✅ Completo | Sesión 3 |
| Backend: BaseModule + módulos de análisis | ✅ Completo | Sesión 4 |
| Backend: Analyzer + integración Claude API | ✅ Completo | Sesión 5 |
| Backend: Endpoint `/api/v1/analyze` (completo) | ✅ Completo | Sesión 5 |
| Backend: Extracción global (objetivo/stakeholders/reglas) | ✅ Completo | Sesión 5 |
| Frontend: Setup React + Vite + Tailwind | ✅ Completo | Sesión 6 |
| Frontend: Componente FileUpload | ✅ Completo | Sesión 6 |
| Frontend: Vista de resultados por HU | ✅ Completo | Sesión 6 |
| Frontend: Vista resumen del proyecto | ✅ Completo | Sesión 6 |
| Integración frontend ↔ backend | ⬜ Pendiente | Sesión 7 |
| Pruebas con archivos reales | ⬜ Pendiente | Sesión 7 |

---

## Cómo levantar el proyecto completo

### Backend

```bash
cd backend

# 1. CREAR el entorno virtual (solo la primera vez)
python -m venv venv
# Si python no funciona, probar:  py -m venv venv  o  python3 -m venv venv

# 2. ACTIVAR el entorno virtual
# Mac/Linux:
source venv/bin/activate
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear el archivo de entorno
cp .env.example .env        # Mac/Linux
copy .env.example .env      # Windows

# 5. Editar .env y agregar tu API key real
# ANTHROPIC_API_KEY=sk-ant-...

# 6. Levantar el servidor
uvicorn app.main:app --reload
# Swagger disponible en: http://localhost:8000/docs
```

> ⚠️ **Windows PowerShell:** si `.\venv\Scripts\Activate.ps1` falla con error de permisos,
> ejecutar primero: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### Frontend (en otra terminal)

```bash
cd frontend

npm install
npm run dev
# App disponible en: http://localhost:5173
```

---

## Decisiones tomadas — Sesión 6

- **Firma visual:** anillo SVG circular por HU (`ScoreBadge`) — colores verde/ámbar/rojo según score
- **ResultCard expandible:** clic en la tarjeta despliega el texto original + tabs de Observaciones/Sugerencias
- **Proxy en Vite:** `/api → http://localhost:8000` — no hay CORS en desarrollo local
- **Fuentes:** Inter (cuerpo) + JetBrains Mono (IDs de HU) via Google Fonts
- **Paleta:** fondo #FAFAF9, texto #111827, acento violeta-600 (#7C3AED), score colores semánticos
- **Flujo App:** upload → loading spinner → ProjectSummary (arriba) + lista de ResultCards

---

## Archivos creados — Sesión 6

```
frontend/
├── package.json
├── vite.config.js            ← proxy /api → backend
├── postcss.config.js
├── tailwind.config.js        ← paleta violeta extendida + fuentes
├── index.html                ← Google Fonts Inter + JetBrains Mono
└── src/
    ├── index.css             ← @tailwind + clases card, badge-score-*
    ├── main.jsx
    ├── App.jsx               ← estado global, flujo upload→loading→resultados
    ├── services/api.js       ← analyzeFile(file) → fetch POST /api/v1/analyze
    └── components/
        ├── ScoreBadge.jsx    ← anillo SVG con animación
        ├── FileUpload.jsx    ← drag & drop + validación client-side
        ├── ResultCard.jsx    ← tarjeta expandible con tabs
        └── ProjectSummary.jsx ← objetivo, stakeholders, reglas de negocio
```

---

## Deuda técnica

- PDFs escaneados sin texto → OCR con pytesseract (iteración futura)
- Word con HU en tablas → iteración futura
- HU analizadas secuencialmente → paralelizar con asyncio.gather si el volumen crece
- Frontend sin tests → agregar Vitest en iteración futura
