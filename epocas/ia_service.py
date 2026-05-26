"""
epocas/ia_service.py
Servicio de generación de eventos históricos con Groq.
"""
import json
import re
from groq import Groq
from django.conf import settings


def _cliente():
    return Groq(api_key=settings.GROQ_API_KEY)


PROMPT_SISTEMA = """Eres un historiador experto. Cuando te den el título de un evento histórico,
su año y la época a la que pertenece, generas un JSON completo con toda la información.

REGLAS ESTRICTAS:
- Responde SOLO con el JSON, sin texto extra, sin markdown, sin explicaciones.
- Las coordenadas deben ser precisas al nivel de ciudad o región, NUNCA calles.
- Los puntos del mapa deben ser lugares reales con coordenadas reales.
- El campo "descripcion" debe ser detallado (mínimo 300 palabras): contexto, causas, desarrollo, consecuencias.
- El campo "resumen" máximo 280 caracteres.
- Los campos "tipo" de puntos solo pueden ser: batalla, ciudad, frente, ruta, zona, otro
- Los campos "bando" solo pueden ser: aliados, enemigos, neutral, otro
- Los campos "tipo" de líneas solo pueden ser: frente, ruta, retirada, naval, otro
- Las zonas y líneas usan arrays de [lat, lng].
- Genera entre 3 y 8 puntos, 0-3 zonas, 0-3 líneas según corresponda al evento.

ESTRUCTURA EXACTA:
{
  "titulo": "string",
  "anio": número,
  "mes": número o null,
  "icono": "emoji",
  "resumen": "string máx 280 chars",
  "descripcion": "string detallado",
  "puntos_mapa": [
    {
      "nombre": "string",
      "descripcion": "string",
      "tipo": "batalla|ciudad|frente|ruta|zona|otro",
      "bando": "aliados|enemigos|neutral|otro",
      "latitud": número,
      "longitud": número,
      "orden": número
    }
  ],
  "zonas_mapa": [
    {
      "nombre": "string",
      "descripcion": "string",
      "bando": "aliados|enemigos|neutral|otro",
      "coordenadas": [[lat,lng], [lat,lng], ...],
      "orden": número
    }
  ],
  "lineas_mapa": [
    {
      "nombre": "string",
      "descripcion": "string",
      "tipo": "frente|ruta|retirada|naval|otro",
      "bando": "aliados|enemigos|neutral|otro",
      "coordenadas": [[lat,lng], [lat,lng], ...],
      "orden": número
    }
  ]
}"""


def generar_evento(titulo, anio, epoca_nombre, mes=None):
    """
    Llama a Groq y devuelve un dict con toda la información del evento.
    Lanza una excepción si algo falla.
    """
    cliente = _cliente()

    prompt_usuario = (
        f"Evento: {titulo}\n"
        f"Año: {anio}\n"
        f"Mes: {mes if mes else 'desconocido'}\n"
        f"Época: {epoca_nombre}\n"
        f"Genera el JSON completo para este evento histórico."
    )

    respuesta = cliente.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": PROMPT_SISTEMA},
            {"role": "user",   "content": prompt_usuario},
        ],
        temperature=0.4,
        max_tokens=4000,
    )

    texto = respuesta.choices[0].message.content.strip()

    # Limpiar posibles backticks de markdown
    texto = re.sub(r'^```(?:json)?\s*', '', texto)
    texto = re.sub(r'\s*```$', '', texto)

    datos = json.loads(texto)
    return datos

# ── Pega esto al final de epocas/ia_service.py ──────────────────────────────

PROMPT_EPOCA = """Eres un historiador experto. Cuando te den el nombre de una época histórica
generas un JSON completo con toda la información de la época y sus eventos principales.

REGLAS ESTRICTAS:
- Responde SOLO con el JSON, sin texto extra, sin markdown, sin explicaciones.
- Si no te dan años, investígalos tú mismo con tu conocimiento histórico y colócalos en el JSON.
- Si te dan especificaciones del profesor, tenlas en cuenta para los eventos y la descripción.
- Genera entre 5 y 8 eventos históricos importantes de esa época.
- Cada evento debe tener mapa con coordenadas reales a nivel de ciudad/región, NUNCA calles.
- El campo "descripcion" de cada evento mínimo 300 palabras.
- El campo "resumen" de cada evento máximo 280 caracteres.
- El campo "descripcion_epoca" mínimo 2 oraciones, máximo 3. Es el texto de la tarjeta del home.
- El color_hex debe ser un color hexadecimal que represente visualmente la época.
- Los campos "tipo" de puntos: batalla, ciudad, frente, ruta, zona, otro
- Los campos "bando": aliados, enemigos, neutral, otro
- Los campos "tipo" de líneas: frente, ruta, retirada, naval, otro

ESTRUCTURA EXACTA:
{
  "nombre": "string",
  "anio_inicio": número,
  "anio_fin": número,
  "descripcion_epoca": "string 2-3 oraciones para la tarjeta del home",
  "icono": "emoji que represente la época",
  "color_hex": "#RRGGBB",
  "eventos": [
    {
      "titulo": "string",
      "anio": número,
      "mes": número o null,
      "icono": "emoji",
      "resumen": "string máx 280 chars",
      "descripcion": "string detallado mín 300 palabras",
      "orden": número,
      "puntos_mapa": [
        {
          "nombre": "string",
          "descripcion": "string",
          "tipo": "batalla|ciudad|frente|ruta|zona|otro",
          "bando": "aliados|enemigos|neutral|otro",
          "latitud": número,
          "longitud": número,
          "orden": número
        }
      ],
      "zonas_mapa": [
        {
          "nombre": "string",
          "descripcion": "string",
          "bando": "aliados|enemigos|neutral|otro",
          "coordenadas": [[lat,lng], [lat,lng]],
          "orden": número
        }
      ],
      "lineas_mapa": [
        {
          "nombre": "string",
          "descripcion": "string",
          "tipo": "frente|ruta|retirada|naval|otro",
          "bando": "aliados|enemigos|neutral|otro",
          "coordenadas": [[lat,lng], [lat,lng]],
          "orden": número
        }
      ]
    }
  ]
}"""


def generar_epoca_completa(nombre, anio_inicio=None, anio_fin=None, descripcion_extra=None):
    """
    Llama a Groq y devuelve un dict con la época completa + todos sus eventos.
    Los años y la descripción extra son opcionales.
    """
    cliente = _cliente()

    partes = [f"Época: {nombre}"]
    if anio_inicio and anio_fin:
        partes.append(f"Años: {anio_inicio} – {anio_fin}")
    else:
        partes.append("Años: investígalos tú mismo según tu conocimiento histórico.")
    if descripcion_extra:
        partes.append(f"Especificaciones del profesor: {descripcion_extra}")
    partes.append("Genera el JSON completo con la época y todos sus eventos históricos principales.")

    prompt_usuario = "\n".join(partes)

    respuesta = cliente.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": PROMPT_EPOCA},
            {"role": "user",   "content": prompt_usuario},
        ],
        temperature=0.4,
        max_tokens=8000,
    )

    texto = respuesta.choices[0].message.content.strip()
    texto = re.sub(r'^```(?:json)?\s*', '', texto)
    texto = re.sub(r'\s*```$', '', texto)

    datos = json.loads(texto)
    return datos