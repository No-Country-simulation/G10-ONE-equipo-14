# CommunityLab — Ejemplos de salida esperada

Estos ejemplos ilustran resultados esperados según los criterios de contenido y el archivo de entrada [`ejemplo_datos_crudos_discord.json`](ejemplo_datos_crudos_discord.json). LinkedIn y FAQ corresponden a los tipos de contenido del MVP descritos en el README; la alerta y los Highlights son salidas adicionales contempladas por los criterios. Son una referencia documental, no una ejecución real del motor.

---

## 1. Post de LinkedIn (historia de éxito)

- **Disparador:** Testimonio de logro laboral con sentimiento altamente positivo (`msg_9823410293`).
- **Autor en el origen:** `carlos_dev99`.
- **Canal de origen:** `#logros-y-empleo`.
- **Regla aplicada:** Tono inspirador; 150–300 palabras. El borrador se mantiene anonimizado porque el archivo no registra autorización para usar el nombre o la cita.

```text
Ocho meses de práctica, una nueva etapa: un contrato como Frontend Jr

Un integrante de nuestra comunidad compartió una gran noticia: firmó un contrato como desarrollador Frontend Jr.

En su mensaje cuenta que pasó ocho meses programando todos los días, enfrentándose a desafíos con React y colaborando en la comunidad. También agradece a las personas que lo acompañaron en el canal de código. Su logro habla de constancia, aprendizaje y del valor de compartir el camino con otras personas.

En el hilo, sus compañeros celebran el esfuerzo que vieron en los ejercicios. Carlos, a su vez, agradece las mentorías y los debates que encontró aquí. Es una muestra de cómo una comunidad puede acompañar el aprendizaje: compartir preguntas, practicar con constancia y celebrar los avances de cada persona. No todas las trayectorias son iguales, pero escuchar una experiencia real también puede ayudar a alguien a dar su siguiente paso.

Cada recorrido profesional es distinto. A veces, avanzar significa volver a intentarlo, pedir ayuda y seguir practicando; otras veces, también significa tender una mano a quien recién empieza. Celebramos este nuevo paso y esperamos que abra muchas oportunidades.

¿Qué aprendizaje o logro te gustaría compartir con la comunidad? Te leemos.

---
#ComunidadDev #DesarrolloWeb #Frontend #React #ComunidadTech
```

**Antes de publicar:** confirmar autorización para identificar al autor o reproducir sus palabras. Si no hay autorización, conservar la versión anonimizada o no publicar el caso.

---

## 2. FAQ / Tip educativo

- **Disparador:** Pregunta técnica sobre variables de entorno (`msg_9823554101`) y señal de recurrencia en la respuesta (`msg_9823565555`), que menciona que unas cinco personas ya preguntaron lo mismo esa semana; serviría si el umbral configurado es `N ≤ 5`.
- **Tema:** Next.js, Vercel y variables de entorno `NEXT_PUBLIC_`.
- **Nota de evidencia:** El export contiene una pregunta explícita y una referencia textual a preguntas anteriores; no contiene cinco mensajes de pregunta independientes. El umbral `N` de recurrencia debe definirse en los criterios.
- **Regla aplicada:** Tono didáctico. Requiere validación técnica antes de publicar.

### FAQ: ¿Por qué una variable de entorno aparece como `undefined` en el cliente de Next.js?

**Pregunta:** Al desplegar en Vercel, ¿cómo hago accesibles desde el cliente algunas variables de entorno de mi proyecto Next.js?

**Respuesta:**

En Next.js, las variables cuyo nombre empieza con `NEXT_PUBLIC_` pueden incluirse en el código enviado al navegador. Por ejemplo, `NEXT_PUBLIC_API_URL` puede usarse en el cliente. No pongas secretos, claves privadas ni credenciales en una variable con ese prefijo: cualquier persona puede inspeccionar el bundle del cliente.

En Vercel, configura la variable en los ajustes del proyecto para el entorno correspondiente (Development, Preview o Production) y vuelve a desplegar para que el nuevo valor se incluya en la compilación. Si sigue apareciendo como `undefined`, comprueba que el nombre coincida exactamente y que la variable esté configurada para el entorno del despliegue.

```javascript
const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/users`);
const users = await response.json();
```

---

## 3. Alerta interna para el Community Manager

- **Disparador:** Frustración explícita sobre fallos repetidos al entregar un trabajo (`msg_9823712900`).
- **Autor:** `andrea_ux`.
- **Canal de origen:** `#soporte-comunidad`.
- **Regla aplicada:** Resumen neutral para uso interno. Nunca se publica externamente. El JSON no contiene un score de confianza del análisis.

```text
[ALERTA CM - PRIORIDAD ALTA]
ID de interacción: msg_9823712900
Fecha/hora: 2026-06-07T09:45:10Z
Autor: @andrea_ux
Canal: #soporte-comunidad
Urgencia: Alta (frustración explícita y entregas fallidas)

Resumen:
La autora indica que intentó subir su entrega del sprint 2 tres veces, que el servidor se bloqueó y perdió el progreso. También dice que no ha recibido respuesta a sus mensajes privados y que la situación le hace considerar dejar el curso. Adjuntó un archivo llamado error_504_gateway.png; el contenido de la imagen no está descrito en los datos.

Seguimiento registrado en el hilo:
admin_clara respondió que escaló el caso al equipo técnico y que contactaría a la autora por privado para ayudarla a recuperar la entrega.

Uso interno únicamente. No inferir un score numérico ni afirmar que el problema ya fue resuelto.
```

---

## 4. Candidato a Destaque semanal (Community Highlights)

- **Disparador previsto:** Agregación semanal de eventos relevantes.
- **Fuente disponible en este ejemplo:** Export de Discord con interacciones del 2026-06-07.
- **Limitación:** Este único export no demuestra que esté cubierto el periodo semanal completo. El contenido siguiente ilustra el formato; no debe publicarse como resumen semanal hasta consolidar el periodo y verificar autorizaciones.

```text
CommunityLab Highlights — borrador

Un integrante de la comunidad compartió que firmó un contrato como desarrollador Frontend Jr, tras ocho meses de práctica diaria y aprendizaje con React. El borrador público debe permanecer anonimizado hasta confirmar su autorización.

También apareció una consulta recurrente sobre variables de entorno de Next.js en Vercel. La comunidad señaló el prefijo NEXT_PUBLIC_; el tip requiere validación técnica y debe recordar que esas variables quedan expuestas al cliente.

Este resumen es provisional: el archivo de muestra no acredita una semana completa ni registra autorización para identificar al autor del testimonio.
```