# CommunityLab — Criterios del Motor de Contenido

> Documento de referencia: qué datos entran al sistema, con qué criterios se decide generar contenido, y cuáles son los insumos posibles que puede producir.

---

## 1. Criterios de entrada

### 1.1 Fuentes y formato

| Origen | Formato | Modo |
|---|---|---|
| Discord, Slack, Foros, GitHub, Formularios | JSON, CSV, Webhook | Lote o tiempo real |

### 1.2 Tipos de interacción aceptados

- **Testimonio**: logro, contratación, superación
- **Pregunta técnica**: duda puntual o recurrente
- **Feedback de curso**
- **Entrega de proyecto**
- **Debate en foro**

### 1.3 Variables que se analizan por cada interacción

- **Sentimiento**: Altamente Positivo / Positivo / Neutral / Negativo o Frustración
- **Temas principales**: extracción de entidades/temas
- **Relevancia**: score que estima qué tan valioso es el mensaje para convertirse en contenido
- **Recurrencia**: si una misma duda o tema se repite entre varios miembros

### 1.4 Condiciones mínimas para que un dato sea procesable

- Longitud mínima de texto (evita generar contenido a partir de mensajes tipo "ok", "gracias")
- Autor y canal identificados
- Score de confianza del análisis de sentimiento por encima de un umbral definido; si está por debajo, el dato se marca para revisión manual en vez de generarse automáticamente
- Se descartan mensajes fuera de tema o marcados como spam

---

## 2. Criterios para la creación de los insumos

### 2.1 Lógica de decisión (condición → insumo)

| Condición | Insumo que dispara |
|---|---|
| Testimonio + sentimiento Altamente Positivo | Caso de Éxito / Post LinkedIn |
| Pregunta técnica + recurrente (≥ N veces) | FAQ / Tip educativo |
| Pregunta técnica + no recurrente | Se deriva a mentoría (no genera insumo) |
| Cualquier tipo + sentimiento Negativo/Frustración alta | Alerta interna |
| Cualquier tipo + tema en tendencia | Insumo para Destaque/Highlights semanal |
| Agregación de todo el periodo | Informe de sentimiento |

### 2.2 Reglas de prioridad

Cuando un mismo mensaje podría disparar más de un insumo, el orden de prioridad es:

1. **Alerta interna** (bienestar del miembro, siempre primero)
2. **Caso de Éxito / Testimonio**
3. **FAQ / Tip educativo**
4. **Destaque / Highlights** (agregación, no compite con lo anterior)

### 2.3 Validaciones antes de generar

- No usar información personal sensible sin autorización explícita del autor
- No generar contenido a partir de miembros marcados como "no desea ser mencionado"
- El contenido educativo (FAQ/Tip) requiere validación técnica antes de publicarse, para evitar respuestas incorrectas
- Las alertas internas nunca se convierten en contenido público

### 2.4 Tono y estilo por canal destino

- **LinkedIn** → inspirador, storytelling
- **X/Twitter** → conciso, directo
- **FAQ/Docs** → didáctico
- **Newsletter** → resumen breve, informativo
- **Uso interno** → neutral, informativo

---

## 3. Catálogo de insumos posibles

| Insumo | Disparador | Canal destino | Tono | Formato / longitud | Dato importante |
|---|---|---|---|---|---|
| **Post LinkedIn** | Testimonio + sentimiento Altamente Positivo, o logro/proyecto destacado | LinkedIn | Inspirador | Título + copy (~150–300 palabras) con hashtags | Requiere validar que el autor autoriza usar su nombre/cita públicamente |
| **Post X (Twitter)** | Mismo evento que el post de LinkedIn, en versión breve | X/Twitter | Conciso, directo | ≤ 280 caracteres | Se genera como variante corta del mismo insumo, no como evento aparte |
| **Caso de Éxito / Testimonio** | Testimonio con logro laboral/personal + sentimiento alto | Insumo base para marketing | Inspirador | Cita extraída + contexto narrativo | Requiere autorización del autor antes de usar su cita públicamente |
| **FAQ / Tip educativo** | Pregunta técnica recurrente (≥ N menciones) | Blog / Docs | Didáctico | Pregunta + respuesta breve, con ejemplo si aplica | Requiere validación técnica antes de publicar |
| **Destaque / Community Highlights** | Agregación semanal de los insumos con mayor relevancia | Newsletter | Informativo | Titular + resumen de 2–3 líneas por hito | Se genera en lote (por periodo), no evento a evento |
| **Alerta interna** | Sentimiento Negativo/Frustración alto, o señal de que un miembro necesita apoyo | Interno (Community Manager) | Neutral | Resumen del problema + autor + canal + urgencia | Nunca se publica externamente; tiene la prioridad más alta |
| **Informe de sentimiento** | Agregación periódica (diaria/semanal) de todos los datos | Dashboard interno | Analítico | Métricas + tendencia + temas en tendencia | Uso interno para toma de decisiones, no es contenido de publicación |