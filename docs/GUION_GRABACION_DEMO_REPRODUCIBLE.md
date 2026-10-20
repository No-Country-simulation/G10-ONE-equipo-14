# Guion de grabación de demostración: Los 3 recorridos reproducibles de CommunityLab

**Proyecto:** CommunityLab — Motor inteligente de transformación y distribución para comunidades digitales  
**Equipo:** G10 · Hackathon ONE · Equipo 14  
**Audiencia:** Jurado evaluador, mentores y stakeholders técnicos  
**Duración sugerida:** 7 a 8 minutos  
**Resolución recomendada:** 1080p (1920 × 1080) a 60 fps en pantalla completa  
**Herramientas recomendadas:** OBS Studio, Loom o Screen Studio  

---

## 1. Checklist previo a la grabación (Paso 0)

Antes de iniciar la grabación, verificar que el entorno cumpla con las siguientes condiciones técnicas:

1. **Variables de entorno (`.env` local):**
   ```ini
   APP_NAME="CommunityLab API"
   ENVIRONMENT=development
   DATABASE_URL=postgresql+psycopg://communitylab:communitylab@db:5432/communitylab
   API_URL=http://api:8000
   PUBLIC_API_URL=http://localhost:8000
   MUTATIONS_ENABLED=true
   API_WRITE_KEY=demo-secret
   MUTATION_RATE_LIMIT=120
   ANALYSIS_PROVIDER=mock
   STORAGE_BACKEND=local
   ```
   > **Nota clave:** Configurar `API_WRITE_KEY=demo-secret` tanto en la API como en el dashboard es imprescindible para que los botones interactivos de curaduría (**Guardar**, **Aprobar y publicar**, **Rechazar**) estén plenamente habilitados. Usar `ANALYSIS_PROVIDER=mock` garantiza tiempos de respuesta instantáneos y comportamiento determinístico idéntico a las pruebas automatizadas.

2. **Levantar los servicios Docker:**
   ```powershell
   docker compose up -d --build
   ```

3. **Verificación visual en navegador:**
   - Abrir Google Chrome o Microsoft Edge en modo incógnito (o con zoom al 100% / 110%) en `http://localhost:8501`.
   - Confirmar en la **barra lateral**:
     - Logo oficial de CommunityLab visible.
     - Indicador verde con el texto: **"Servicios disponibles"**.
     - **API:** Operativa.
     - **PostgreSQL:** Conectado / saludable.
   - Pestaña secundaria lista con Swagger: `http://localhost:8000/docs`.

4. **Archivo de datos para la prueba:**
   - Tener localizado en el explorador de archivos: `data/sample_interactions.json` (o `docs/sets_pruebas/set_04_prueba_inicial/entrada_interacciones_25.json`).

---

## 2. Estructura y cronograma de la grabación

| Bloque | Contenido | Tiempo estimado |
|:---:|---|:---:|
| **Módulo 1** | Portada, propósito, valor de negocio y panel lateral | 0:00 - 1:15 (1 min 15 s) |
| **Módulo 2** | **Recorrido 1:** Logro de comunidad → Post LinkedIn aprobado y publicado | 1:15 - 3:30 (2 min 15 s) |
| **Módulo 3** | **Recorrido 2:** Duda técnica recurrente → FAQ didáctica aprobada | 3:30 - 5:15 (1 min 45 s) |
| **Módulo 4** | **Recorrido 3:** PII sensible y frustración → Alerta interna y bloqueo | 5:15 - 6:45 (1 min 30 s) |
| **Módulo 5** | Robustez técnica: Deduplicación SHA-256 y persistencia por Run ID | 6:45 - 7:45 (1 min 00 s) |
| **Módulo 6** | Cierre técnico: 159 tests, definición de terminado y repositorio | 7:45 - 8:30 (45 s) |

---

## Módulo 1: Introducción, propósito y panel operativo (0:00 - 1:15)

### Acciones en pantalla
1. Iniciar la grabación con la portada completa del dashboard (`http://localhost:8501`).
2. Pasar el cursor suavemente sobre el Hero Banner (*"Convertí conversaciones en acciones útiles"*).
3. Mostrar el panel lateral izquierdo:
   - Señalar el estado de salud de la **API** y **PostgreSQL**.
   - Abrir brevemente el expander **"¿Para qué sirven los datos de la carga?"** para mostrar la explicación contextual de Organización, Comunidad y Período.
   - Mostrar los botones de acceso al Manual de Usuario, Swagger y GitHub.

### Guion de locución sugerido
> *"Hola a todos. Bienvenidos a la demostración integral de **CommunityLab**, desarrollado por el Equipo 14 del Hackathon ONE G10.*  
>  
> *Las comunidades digitales generan cientos de interacciones valiosas todos los días en canales como Discord, Slack o foros: testimonios de éxito, dudas técnicas repetitivas y también situaciones de frustración. Sin embargo, procesar este volumen manualmente es insostenible.*  
>  
> *CommunityLab resuelve esto mediante un motor inteligente que ingesta estas conversaciones, las normaliza, detecta datos personales sensibles, extrae oportunidades con inteligencia artificial fundamentada y genera borradores de contenido para LinkedIn y FAQ, manteniendo siempre un curador humano en el centro antes de la publicación final.*  
>  
> *Como observamos en el panel lateral, nuestros microservicios en Docker —FastAPI, PostgreSQL 16 y Streamlit— se encuentran 100% operativos y saludables. Comencemos con los tres recorridos obligatorios del MVP."*

---

## Módulo 2: Recorrido 1 — Logro a post de LinkedIn aprobado y publicado (1:15 - 3:30)

### Acciones en pantalla
1. En la sección **1. Cargar interacciones**:
   - Verificar campos:
     - **Organización:** `one`
     - **Comunidad:** `demo-mvp`
     - **Período de referencia:** (dejar el valor por defecto, ej. `2026-W42`)
   - En **Archivo de interacciones**, arrastrar o seleccionar el archivo `data/sample_interactions.json`.
   - Hacer clic en el botón primario **Procesar archivo**.
2. Esperar el spinner (*"Guardando interacciones en PostgreSQL..."*) y la alerta verde *"Carga procesada correctamente"*.
3. En la sección **3. Resultado persistido**:
   - Hacer énfasis con el cursor en las métricas: **Recibidas (25)**, **Aceptadas (25)**, **Duplicadas (0)**, **Con errores (0)**.
   - Señalar los insights: **Sentimiento predominante**, **Temas principales** y **Tiempo de procesamiento** en milisegundos.
   - Destacar los bloques de solo lectura: **Run ID** y **Estado: COMPLETED**.
4. Ir a la sección **4. Análisis, oportunidades y curaduría**:
   - Abrir la pestaña **Análisis**: desplegar el primer análisis que corresponde al testimonio de logro. Mostrar:
     - Relevancia alta ($\ge 0.75$) y nivel de confianza.
     - Sección **Evidencia y fuentes**: leer la cita textual original (*"Gracias, conseguí entregar FastAPI con PostgreSQL y Docker"*) y señalar el `source_interaction_id`.
   - Pasar a la pestaña **LinkedIn y FAQ**:
     - Mostrar la tarjeta del activo de canal **LINKEDIN** en estado `PENDING_REVIEW` y versión `1`.
     - **Edición en vivo:** En el campo *Contenido*, añadir al inicio del texto: `"🎉 ¡Gran hito en la comunidad! "` y presionar el botón **Guardar**.
     - Observar la notificación verde: *"Nueva versión guardada"* y notar que el subtítulo ahora indica **versión 2**.
     - **Aprobación y publicación:** Presionar el botón azul **Aprobar y publicar**.
     - Observar que el activo se aprueba, se retira de la cola pendiente y la pantalla se desplaza a la sección inferior **Recibo de publicación**.
     - Hacer zoom/énfasis en los cuatro datos del recibo: **Bucket**, **Objeto** (ruta inmutable), **ETag** y el **SHA-256** de 64 caracteres.

### Guion de locución sugerido
> *"Vamos con el **Recorrido 1**: transformación de un logro de comunidad en una publicación de LinkedIn aprobada y publicada.*  
>  
> *Configuramos nuestra organización `one` y la comunidad `demo-mvp`. Cargamos nuestro set de 25 interacciones y presionamos 'Procesar archivo'.*  
>  
> *En milisegundos, el motor procesa el lote. Como vemos en las métricas, se aceptaron las 25 interacciones en una base limpia, sin duplicados ni errores. Aquí tenemos nuestro **Run ID**, un identificador UUID inmutable que asegura trazabilidad punta a punta.*  
>  
> *Si ingresamos a la pestaña de **Análisis**, vemos cómo la IA analizó el sentimiento, detectó los tópicos y, lo más importante: generó **Grounding**. No inventa información; cada afirmación está respaldada por una cita textual exacta y un ID de interacción original.*  
>  
> *Pasemos a la cola de curaduría en la pestaña **LinkedIn y FAQ**. Aquí encontramos el borrador generado para LinkedIn a partir de un testimonio de superación. Como curador de contenido, puedo perfeccionar el texto: agregamos un saludo inicial y presionamos 'Guardar'. Noten cómo el sistema aplica versionado inmutable: pasamos a la versión 2.*  
>  
> *Ahora hacemos clic en 'Aprobar y publicar'. El activo cumple la máquina de estados: pasa a APPROVED, se bloquea contra nuevas modificaciones y nuestro StorageAdapter genera el paquete final en almacenamiento con su recibo: Bucket, Object Key, ETag y un hash criptográfico SHA-256 inmutable. Recorrido 1 completado con éxito."*

---

## Módulo 3: Recorrido 2 — Duda técnica recurrente a FAQ aprobada (3:30 - 5:15)

### Acciones en pantalla
1. En la misma pestaña **LinkedIn y FAQ**:
   - Presionar el botón **Actualizar cola**.
   - Ubicar el activo de canal **FAQ** generado por el motor.
   - Señalar el **Título**: resaltar que está formulado canónicamente como pregunta finalizada en signo de interrogación (`?`).
   - Abrir el desplegable **Evidencia y fuentes**:
     - Mostrar que este activo contiene **múltiples interacciones fuente** (`source_interaction_ids`).
     - Mostrar los dos extractos donde dos miembros distintos consultan sobre cómo configurar Docker y conectar PostgreSQL.
2. Explicar la regla de negocio: si hubiera sido una sola pregunta aislada, el router la hubiera descartado o enviado a mentoría interna; pero al alcanzar el umbral de recurrencia (`FAQ_RECURRENCE_THRESHOLD >= 2`), se disparó la creación de la FAQ.
3. Presionar el botón **Guardar** para validar el texto y luego hacer clic en **Aprobar** (o *Aprobar y publicar*).
4. Desplazarse a la sección inferior **Activos aprobados** y confirmar que el activo FAQ figura en la lista con su identificador permanente y versión consolidada.

### Guion de locución sugerido
> *"Pasamos ahora al **Recorrido 2**: detección de una duda técnica recurrente y su conversión en una FAQ educativa validada.*  
>  
> *Una de las reglas de negocio más importantes de CommunityLab es que **no se genera una FAQ por una pregunta aislada**. Nuestro router agrupa las preguntas temáticas y evalúa el umbral de recurrencia.*  
>  
> *En este caso, dos miembros distintos preguntaron cómo conectar FastAPI con PostgreSQL en Docker. Al alcanzar el umbral de 2 menciones, el motor redactó este activo FAQ.*  
>  
> *Fíjense en dos detalles de calidad: primero, el título está formulado estrictamente como pregunta con signo de cierre interrogativo. Segundo, al abrir 'Evidencia y fuentes', vemos que el activo enlaza las dos interacciones de origen con sus respectivas citas textuales.*  
>  
> *Como curador, valido que la explicación técnica sea certera y presiono 'Aprobar'. El activo queda formalmente aprobado, inmutable y disponible para ser consumido por el equipo de documentación o soporte. Recorrido 2 cumplido."*

---

## Módulo 4: Recorrido 3 — Contenido sensible, frustración y PII bloqueada (5:15 - 6:45)

### Acciones en pantalla
1. Dirigirse a la pestaña **Oportunidades**:
   - Mostrar la tabla de oportunidades detectadas.
   - Ubicar la fila donde el estado figura en rojo/destacado como **`BLOCKED`**.
   - Mostrar la columna *reason*: señalar que indica frustración severa o detección de datos de contacto personales.
2. Dirigirse a la pestaña **Alertas internas**:
   - Señalar el aviso: *"X alerta(s) interna(s) abierta(s)"*.
   - Mostrar la tabla de alertas `OPEN`:
     - Identificador del miembro afectado.
     - Resumen del problema (ej. fallo crítico de conexión y queja).
     - Nivel de severidad o prioridad alta.
3. Volver a la pestaña **LinkedIn y FAQ**:
   - Demostrar fehacientemente que **NO existe ningún activo público** generado a partir de este mensaje sensible.
   - Explicar la redacción automática de PII: si un usuario incluyó su correo o teléfono, el sistema los reemplazó por `[EMAIL]` y `[PHONE]`, y si no dio consentimiento explícito (`publication_consent: false`), su nombre se sustituyó por `[PERSON]`.

### Guion de locución sugerido
> *"Llegamos al **Recorrido 3**, fundamental para la seguridad, privacidad y ética del producto: detección de contenido sensible, frustración y bloqueo preventivo de activos.*  
>  
> *En una comunidad, cuando un miembro experimenta frustración o comparte un problema con sus datos de contacto, la inteligencia artificial jamás debe convertirlo en un post público de marketing.*  
>  
> *Miren lo que ocurrió: nuestro filtro de privacidad escaneó los datos, redactó correos y teléfonos bajo etiquetas [EMAIL] y [PHONE], y el clasificador determinístico detectó sentimiento negativo severo.*  
>  
> *En la pestaña **Oportunidades**, vemos que la oportunidad quedó en estado **BLOCKED**. Inmediatamente, el sistema derivó el caso a la pestaña **Alertas internas**, creando una alerta con estado OPEN para que el Community Manager atienda al usuario de forma privada y humana.*  
>  
> *Y lo más importante: si volvemos a la pestaña de LinkedIn y FAQ, confirmamos que **no se generó ningún borrador público**. Se protegió la privacidad del usuario y la reputación de la organización. Recorrido 3 verificado."*

---

## Módulo 5: Robustez técnica — Deduplicación e Idempotencia (6:45 - 7:45)

### Acciones en pantalla
1. **Demostración de deduplicación:**
   - Volver a la sección superior **1. Cargar interacciones**.
   - Mantener exactamente la misma comunidad: `demo-mvp`.
   - Mantener el mismo archivo seleccionado: `sample_interactions.json`.
   - Presionar nuevamente el botón **Procesar archivo**.
   - Mostrar el nuevo resumen:
     - **Recibidas:** 25.
     - **Aceptadas:** 0.
     - **Duplicadas:** 25.
     - Explicar que el fingerprint SHA-256 evitó duplicar datos en PostgreSQL.
2. **Demostración de persistencia e idempotencia por Run ID:**
   - Copiar el **Run ID** mostrado en pantalla.
   - Presionar **F5** en el navegador para recargar la página por completo (la pantalla vuelve a su estado inicial en blanco).
   - En la sección **2. Recuperar una ejecución**, pegar el Run ID en el campo de texto.
   - Presionar el botón **Buscar ejecución**.
   - Mostrar cómo en menos de un segundo reaparecen exactamente todas las métricas, análisis, oportunidades y el estado de la cola guardados en PostgreSQL.

### Guion de locución sugerido
> *"Para cerrar, demostremos dos garantías arquitectónicas clave del proyecto: **Deduplicación por Fingerprint** y **Persistencia por Run ID**.*  
>  
> *¿Qué pasa si un usuario o un webhook vuelve a enviar accidentalmente el mismo archivo? Presionamos 'Procesar archivo' por segunda vez sobre la misma comunidad.*  
>  
> *El sistema no falla ni duplica registros: gracias al cálculo de un fingerprint SHA-256 por interacción, reporta con precisión 25 duplicadas y 0 aceptadas.*  
>  
> *Ahora copiemos el Run ID y recarguemos completamente el navegador con F5. La sesión en memoria se vacía. Pegamos nuestro Run ID en 'Recuperar ejecución' y presionamos 'Buscar ejecución'.*  
>  
> *Como PostgreSQL es nuestra única fuente de verdad persistente, recuperamos al instante todo el estado del procesamiento: métricas, análisis, alertas y decisiones de curaduría."*

---

## Módulo 6: Cierre, métricas de calidad y repositorio (7:45 - 8:30)

### Acciones en pantalla
1. Cambiar brevemente a la pestaña de Swagger / OpenAPI (`http://localhost:8000/docs`) para mostrar los contratos REST versionados `/api/v1`.
2. Volver al dashboard y mostrar en el sidebar el enlace al repositorio de GitHub.
3. Despedida a cámara o paneo del Hero.

### Guion de locución sugerido
> *"Con esto demostramos que CommunityLab cumple al 100% todos los criterios de salida del MVP definidos en las bases:*  
> - *Entorno reproducible con Docker Compose.*  
> - *Ingesta y deduplicación estricta de interacciones.*  
> - *Pipeline de IA con Grounding verificable y redacción de PII.*  
> - *Generación de activos para LinkedIn y FAQ.*  
> - *Curaduría humana con auditoría y versionado.*  
> - *Almacenamiento con manifiesto SHA-256 y recibo verificable.*  
> - *Una suite automatizada con **159 pruebas aprobadas** y cero secretos.*  
>  
> *Muchas gracias por su atención y quedamos a disposición para cualquier consulta técnica."*

---

## 3. Resumen de comandos útiles para el operador

```powershell
# Iniciar servicios antes de grabar
docker compose up -d --build

# Confirmar salud de contenedores
docker compose ps

# Ver logs en tiempo real durante la grabación
docker compose logs -f api dashboard

# Ejecutar las 159 pruebas para verificar salud del código
docker compose exec db createdb -U communitylab communitylab_test
docker compose exec -e TEST_DATABASE_URL=postgresql+psycopg://communitylab:communitylab@db:5432/communitylab_test api python -m pytest -q tests

# Detener los servicios conservando los datos de la demo
docker compose down
```
