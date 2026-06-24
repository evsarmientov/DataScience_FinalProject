# Guion — MediRuta
**7 minutos exactos · Slot #8 · Miércoles 24 junio · 08:45am**

> Habla despacio. Hay cronómetro al frente.
> `[corchetes]` = instrucciones, no las lees en voz alta.

---

## SLIDE 1 — Portada · [0:00–0:20]

*"Buenos días. Soy Evelyn Sarmiento.*

*MediRuta le dice al paciente oncológico exactamente a qué módulo del INEN ir, qué documentos llevar y qué estudios tener listos — antes de salir de casa."*

`[pausa 2 segundos]`

---

## SLIDE 2 — El Problema · [0:20–1:20]

*"En mayo de este año recibí un diagnóstico de cáncer de tiroides. Tenía que ir al INEN y no sabía nada — a qué módulo ir, qué llevar, con quién hablar.*

*Las colas empiezan a las dos de la mañana. El propio Ministro de Salud dijo — cito — 'cuando un paciente de regiones viene a Lima, termina al final de la cola, a sufrir o morir'.*

*Si te falta un solo documento, te mandan a casa. Con el mismo diagnóstico. El mismo miedo. Otro día perdido.*

*Y nadie te explica qué cubre tu seguro. SIS, EsSalud, privado — ¿qué entra, qué no, cuánto cuesta? Ninguna ventanilla te lo dice.*

*El 52% de los cánceres en Perú se diagnostican en estadio avanzado. Parte de ese número son semanas perdidas navegando un sistema que nadie explica.*

*Construí MediRuta para que nadie pase por lo mismo."*

---

## SLIDE 3 — La Solución · [1:20–2:00]

*"La app tiene cuatro módulos.*

*Uno: ingresas tu diagnóstico, el sistema te dice el módulo del INEN, los documentos que necesitas y los estudios que te van a pedir — incluyendo cuánto cuesta cada procedimiento según tu seguro.*

*Dos: directorio de 159 médicos reales del INEN, extraídos del Portal de Transparencia del Estado.*

*Tres: preguntas preparadas para hacerle al oncólogo en tu primera consulta.*

*Cuatro: buscas un medicamento y ves si lo cubre el SIS o EsSalud.*

*Lo más fácil es verlo."*

---

## SLIDE 4 — Demo · [2:00–5:30]

`[cambiar al navegador — mediruta.streamlit.app abierto]`

*"Escribo mi diagnóstico real: microcarcinoma papilar de tiroides."*

`[escribir y hacer clic en Ver mi ruta]`

*"Módulo 1 — Cabeza, Cuello y Tórax. Me muestra los documentos que tengo que llevar, traídos en tiempo real desde el portal oficial del INEN. Y los estudios que me va a pedir el especialista."*

`[bajar a la sección del tarifario]`

*"Acá está lo nuevo. Busco 'biopsia'."*

`[escribir biopsia y buscar]`

*"Biopsia de médula ósea: SIS paga S/18.63, EsSalud S/59, privado S/94. Esto viene del Tarifario Institucional del INEN 2024 — resolución jefatural oficial del Estado Peruano. Extrajimos y estructuramos 1,120 procedimientos. Antes nadie le comunicaba estos costos al paciente."*

`[ir a Tab 2]`

*"Tab 2 — filtro por Módulo 1. Médicos reales con cargo verificado, fuente oficial por la Ley de Transparencia."*

`[ir a Tab 3]`

*"Tab 3 — genero las preguntas para el oncólogo. El paciente llega preparado, no desbordado."*

`[volver a slides]`

---

## SLIDE 5 — Mercado y Modelo · [5:30–6:30]

*"El mercado: 72,827 nuevos diagnósticos de cáncer al año en Perú. Incluyendo familias, más de 550,000 personas en el sistema oncológico.*

*Tres líneas de ingresos. El paciente siempre accede gratis a lo esencial. Para funciones de acompañamiento — preguntas, medicamentos, guía de seguros — hay un plan premium de S/9.90 al mes.*

*Las instituciones — INEN, EsSalud, IRENEs — pagan S/499 al mes por integrarlo en su portal. El ciclo de venta en salud pública es largo, 12 a 18 meses — siendo honestos.*

*Y publicidad segmentada: EPS privadas en la guía de seguros, farmacias en el buscador de medicamentos. El usuario ya está en el flujo.*

*Break-even mixto: entre 18 y 24 meses."*

---

## SLIDE 6 — Tracción y Ask · [6:30–7:00]

*"La app está en producción. Cinco usuarios reales — dos familiares de pacientes oncológicos activos del INEN y del IREN La Libertad. Uno me dijo: 'esa información nos tomó semanas descubrirla. Está todo ahí.'*

*159 médicos verificados. 1,120 procedimientos del Tarifario 2024 integrados hoy. Mi diagnóstico real clasifica correctamente en el sistema. Commits distribuidos en once días.*

*Pedimos S/30,000 para doce meses: operaciones, legal, módulo institucional, expansión a IRENEs.*

*Milestone: 10,000 usuarios más un contrato institucional firmado.*"

`[pausa — mirar al jurado, no a la pantalla]`

*"MediRuta no cambia el sistema de salud del Perú.*

*Hace una sola cosa: le dice al paciente, en segundos, lo que antes le tomaba semanas descubrir.*

*En oncología, las semanas importan.*

*Gracias."*

---

## Preguntas frecuentes

**"¿No es peligroso dar información médica con IA?"**
> "MediRuta no diagnostica ni recomienda tratamientos. Le dice al paciente a qué módulo ir y qué documentos llevar. Es orientación logística. El disclaimer aparece desde el primer segundo."

**"¿Por qué pagaría el paciente premium si tiene lo esencial gratis?"**
> "Lo esencial te lleva al hospital. El premium te acompaña durante el tratamiento: preguntas para el oncólogo, seguimiento de medicamentos, costos por seguro. Es para quien ya está en proceso, no solo para la primera visita."

**"¿Cómo consigues contratos institucionales si el ciclo es de 12–18 meses?"**
> "Empezamos con un piloto gratuito en admisión del INEN. Su incentivo está alineado: menos rechazados por falta de documentos es menos carga operativa. El B2C gratuito construye tracción mientras el B2B se cierra."

**"¿Por qué no lo hace el INEN directamente?"**
> "El INEN tardó meses en actualizar su portal web. Nosotros desplegamos en once días y actualizamos datos automáticamente. La velocidad es el moat."

**"¿Qué pasa con los datos del paciente?"**
> "No almacenamos nada. Cada sesión es efímera. No hay base de datos de pacientes."
