# Guion — Pitch MediRuta
**Data Science con Python 2026-I — Universidad del Pacífico**
**Slot #8 — Miércoles 24 junio, 08:45am**
**Duración: 7–10 minutos**

---

> **Cómo usar este guion:**
> - Las líneas en cursiva son lo que dices en voz alta.
> - Los `[corchetes]` son instrucciones de escenario — no los lees.
> - Los tiempos son referencias, no alarmas. Si el demo toma 30 segundos más, no importa.
> - Habla despacio. La gente tarda en leer las diapositivas mientras te escucha.

---

## SLIDE 1 — Título / One-liner
`[00:00 — 00:30]`

*"Buenos días. Soy Evelyn Sarmiento, economía 2026-I.*

*En mayo de este año me dieron un diagnóstico de cáncer de tiroides. Tenía que ir al INEN — el Instituto Nacional de Enfermedades Neoplásicas — y no tenía idea de qué hacer, a dónde ir, qué llevar, ni con quién hablar.*

*Eso es lo que resuelve MediRuta."*

`[pausa de 2 segundos — deja que caiga]`

---

## SLIDE 2 — El Problema
`[00:30 — 01:30]`

*"El INEN atiende a decenas de miles de pacientes oncológicos al año. Pero llegar por primera vez es un caos.*

*Las colas empiezan a las dos de la mañana. Hay filas de cinco cuadras desde las cuatro. El propio Ministro de Salud dijo — y cito — 'cuando un paciente de regiones viene a Lima, termina al final de la cola, a sufrir o morir, porque el INEN está saturado'.*

*Y eso es solo para entrar. Adentro, el hospital tiene módulos: tienes que saber exactamente a cuál te corresponde ir, con qué documentos, y con qué estudios previos. Si te falta uno solo, te mandan a casa. Con el mismo diagnóstico. El mismo miedo. Y otro día perdido.*

*Además, nadie te explica qué cubre tu seguro. SIS, EsSalud, privado — ¿qué entra, qué no, cuánto cuesta? Ninguna ventanilla te lo dice antes de que llegues.*

*Y el 52% de los cánceres en Perú se diagnostican en estadio avanzado. Parte de ese número son semanas perdidas navegando un sistema que nadie te explica."*

---

## SLIDE 3 — Cómo lo resuelven hoy (sin MediRuta)
`[01:30 — 02:00]`

*"¿Cómo resuelve esto la gente hoy? Preguntando en la ventanilla — que abre lunes a viernes en horario de oficina. Grupos de WhatsApp de pacientes — información no verificada. Familiares que ya pasaron por el proceso — si es que tienes uno. O tramitadores informales que cobran entre cincuenta y doscientos soles por orientarte y que a veces tampoco saben.*

*Yo lo viví. Y decidí construir lo que me hubiera gustado tener."*

---

## SLIDE 4 — La Solución
`[02:00 — 02:45]`

*"MediRuta es una app web con cuatro módulos.*

*El primero: escribes tu diagnóstico en lenguaje normal — o subes una foto de tu hoja de referencia — y el sistema te dice exactamente a qué módulo del INEN ir, qué documentos llevar, y qué estudios te van a pedir.*

*El segundo: un directorio de 159 médicos reales del INEN, con cargo verificado, extraídos del Portal de Transparencia del Estado. Filtrables por módulo.*

*El tercero: preguntas para hacerle al oncólogo en tu primera consulta. Organizadas por categoría. Llegas preparada, no desbordada.*

*El cuarto: buscas un medicamento — o subes la foto de tu receta — y el sistema te dice si lo cubre el SIS, si está en el EsSalud, y si está en el petitorio nacional de medicamentos esenciales.*

*Todo gratis para el paciente. Todo en tiempo real."*

---

## SLIDE 5 — Demo en vivo
`[02:45 — 04:30]`

`[Abrir mediruta.streamlit.app en el navegador — ya debe estar abierto en una pestaña]`

*"Déjenme mostrarlo. Voy a escribir mi diagnóstico real: microcarcinoma papilar de tiroides."*

`[Escribir en Tab 1]`

*"El clasificador identifica Módulo 1 — Cabeza, Cuello y Tórax. Me muestra los documentos que tengo que llevar, traídos en tiempo real desde el portal del INEN. Y me genera los estudios que me va a pedir el especialista: ecografía de cuello, cintigrafía tiroidea, TSH, T4 libre."*

`[Ir a Tab 2]`

*"En el directorio médico, filtro por Módulo 1 y veo los especialistas de ese módulo con su cargo verificado. No es una lista inventada — viene del PDF de transparencia institucional del INEN, por la Ley 27806."*

`[Ir a Tab 3]`

*"Y aquí, el sistema me genera las preguntas que debería hacerle al oncólogo. ¿Cuáles son mis opciones de tratamiento? ¿Cuánto tiempo dura? ¿Puedo seguir trabajando? Preguntas que cuando te dan un diagnóstico no sabes ni cómo formular."*

`[Ir a Tab 4]`

*"Y si busco levotiroxina — un medicamento que se usa en mi caso — me dice que está cubierto por el SIS, que está en el PNUME, y me enlaza directo a DIGEMID."*

---

## SLIDE 6 — Why Now / Tecnología
`[04:30 — 05:00]`

*"Este producto no era posible hace tres años. Lo que lo hace posible hoy:*

*Claude API con visión: puedo hacer OCR de una hoja médica manuscrita por menos de un centavo. El directorio médico del INEN vive en un PDF — pdfplumber lo extrae automáticamente. Y hay un dato clave: el INEN publicó este año su tarifario institucional 2024 — mil doscientos procedimientos oncológicos con costos exactos por tipo de seguro. SIS, EsSalud, privado. Es un documento oficial del Estado que nadie le estaba explicando al paciente. Ya lo tenemos.*

*La combinación de datos abiertos, LLMs baratos y herramientas de despliegue rápido hicieron posible construir esto en once días."*

---

## SLIDE 7 — Mercado
`[05:00 — 05:25]`

*"El mercado es claro. 72,827 nuevos diagnósticos de cáncer por año en Perú, según Globocan. Incluyendo familias y cuidadores, son más de 550,000 personas en contacto activo con el sistema oncológico cada año.*

*El mercado institucional directo: INEN más cinco IRENEs regionales. Seis instituciones. A quinientos soles al mes, son 36,000 soles al año — y eso es solo el punto de entrada.*

*Latinoamérica tiene sistemas públicos de salud con la misma fricción. Colombia, México, Argentina — la misma desorientación, la misma oportunidad."*

---

## SLIDE 8 — Modelo de negocio
`[05:25 — 06:00]`

*"Tres líneas de ingresos.*

*Primera: el paciente tiene acceso gratis a lo esencial. Si quiere las preguntas para el oncólogo, el buscador de medicamentos y la guía de seguros — eso es premium, nueve con noventa al mes. Conversión esperada: uno o dos por ciento. No mucho, pero a diez mil usuarios son entre cien y doscientos clientes pagando.*

*Segunda: las instituciones — INEN, EsSalud, clínicas — pagan por integrar MediRuta en su propio portal. Cuatrocientos noventa y nueve soles al mes el plan básico. Ciclo de venta en salud pública: doce a dieciocho meses. No es ingreso inmediato, pero es recurrente y de alto margen.*

*Tercera: publicidad segmentada. EPS privadas como Rímac o Pacífico anuncian en la guía de seguros. Farmacias anuncian en el buscador de medicamentos. El usuario ya está en el flujo — el anunciante llega en el momento exacto.*

*Break-even mixto realista: dieciocho a veinticuatro meses."*

---

## SLIDE 9 — Tracción
`[06:00 — 06:30]`

*"¿Qué tenemos hasta ahora?*

*La app está en vivo — mediruta.streamlit.app — sin instalación, desde el día del deploy.*

*Cinco usuarios reales. Tres generales, dos familiares de pacientes oncológicos activos del INEN y del IREN La Libertad. Uno me dijo: 'esa información nos tomó semanas descubrirla. Está todo ahí'.*

*Dos usuarios identificaron de forma independiente el mismo problema de UX — lo corregí en la versión 1.1. Dos usuarios sugirieron expandir a los IRENEs regionales sin que se les preguntara. Ya está en el roadmap.*

*159 médicos verificados. Mi propio diagnóstico clasifica correctamente en el sistema. Commits distribuidos en once días — no un solo push el último día."*

---

## SLIDE 10 — Roadmap
`[06:30 — 07:00]`

*"En tres meses: verificación de colegiatura médica CMP, primer piloto gratuito con el área de admisión del INEN, mil usuarios activos.*

*En seis meses: el módulo de seguros. Ya tenemos el tarifario. El paciente ingresa su diagnóstico y ve cuánto le cuesta cada procedimiento según su seguro. También expandimos a los IRENEs regionales — dos usuarios nos lo pidieron explícitamente.*

*En doce meses: cinco hospitales integrados, chatbot de WhatsApp, cobertura de EPS privadas, veinte mil usuarios, y seed round."*

---

## SLIDE 11 — El Ask
`[07:00 — 07:30]`

*"Pedimos treinta mil soles — algo así como ocho mil dólares — para doce meses de runway.*

*Doce mil en operaciones y API. Ocho mil en revisión legal — esto es salud, y hay que hacerlo bien. Ocho mil en el desarrollo del módulo institucional y el módulo de seguros. Dos mil en adquisición inicial de usuarios.*

*El milestone que desbloquea la siguiente ronda: diez mil usuarios activos y un contrato institucional firmado. Con eso vamos a UTEC Ventures, Wayra o NXTP.*

*El producto ya existe. Los datos ya los tenemos. Solo necesitamos tiempo para que los ciclos de venta se cierren."*

---

## CIERRE
`[07:30 — 07:45]`

*"MediRuta no cambia el sistema de salud del Perú. No construye más hospitales ni forma más oncólogos.*

*Hace una sola cosa: elimina la fricción del primer contacto. Le dice al paciente, en segundos, lo que antes le tomaba semanas descubrir.*

*Y en oncología, las semanas importan.*

*Gracias."*

`[pausa — esperar preguntas]`

---

## Preguntas frecuentes y cómo responderlas

**"¿No es peligroso que la IA dé información médica?"**
> *"MediRuta no diagnostica ni recomienda tratamientos. Le dice al paciente a qué módulo del INEN ir, qué documentos llevar y qué preguntas hacerle al médico. Es orientación logística, no atención clínica. El disclaimer es visible desde el primer segundo que entras a la app."*

**"¿Por qué el paciente premium pagaría si ya tiene lo esencial gratis?"**
> *"Lo esencial te hace llegar al hospital. El premium te acompaña durante el proceso — preguntas para el oncólogo, seguimiento de medicamentos, guía de costos por seguro. Es para el paciente que ya está en tratamiento, no solo para la primera visita."*

**"¿Cómo consigues los primeros contratos institucionales si el ciclo es de 12–18 meses?"**
> *"Empezamos con un piloto gratuito. El área de admisión del INEN tiene un incentivo directo: menos pacientes rechazados por falta de documentos = menos re-ingresos = menos carga operativa. El interés está alineado. El B2C gratuito construye la tracción mientras el B2B se cierra."*

**"¿Por qué no lo copia el INEN directamente?"**
> *"Pueden. Pero el INEN tardó meses en actualizar su portal web. Nosotros desplegamos en once días, iteramos con usuarios reales en horas, y mantenemos datos actualizados automáticamente. La velocidad es el moat, no el secreto."*

**"¿Qué pasa con la privacidad de los datos del paciente?"**
> *"No almacenamos ningún dato del paciente. El diagnóstico que se escribe en la app no se guarda en ningún servidor nuestro. Cada sesión es efímera. No hay base de datos de pacientes."*

**"¿Solo INEN? ¿Por qué no empezar con un hospital más fácil?"**
> *"El INEN es el caso más doloroso y el más justificable — es el único instituto oncológico especializado del país. Si funciona aquí, donde el problema es más grave, funciona en cualquier otro hospital. Y la founder es paciente activa del INEN — eso no es un dato menor."*

---

*Repositorio: github.com/evsarmientov/DataScience_FinalProject*
*App: mediruta.streamlit.app*
*Evelyn Valeria Sarmiento Vasquez — ev.sarmientov@alum.up.edu.pe*
