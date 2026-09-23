import os
from datetime import datetime, date, time
from flask import Flask, request, jsonify
from flask.json.provider import DefaultJSONProvider
import psycopg2
from psycopg2.extras import RealDictCursor

# ✅ Fix del bug "Object of type time is not JSON serializable"
class CustomJSONProvider(DefaultJSONProvider):
    @staticmethod
    def default(obj):
        if isinstance(obj, (date, time)):
            return obj.isoformat()
        return DefaultJSONProvider.default(obj)

app = Flask(__name__)
app.json = CustomJSONProvider(app)

def get_db():
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'database'),
        port=os.environ.get('DB_PORT', 5432),
        dbname=os.environ.get('DB_NAME', 'rrhh'),
        user=os.environ.get('DB_USER', 'rrhh_user'),
        password=os.environ.get('DB_PASSWORD', '')
    )

def calcular_estado(hora_prog, hora_real):
    """Lógica de negocio: PUNTUAL si llega a la hora o antes, ATRASO si después."""
    if not hora_prog or not hora_real:
        return 'INCOMPLETO'
    prog = datetime.strptime(hora_prog, '%H:%M').time()
    real = datetime.strptime(hora_real, '%H:%M').time()
    return 'PUNTUAL' if real <= prog else 'ATRASO'

def validar_marcacion(data):
    errores = []
    if not data.get('codigo_empleado'):
        errores.append('codigo_empleado es obligatorio')
    if not data.get('fecha'):
        errores.append('fecha es obligatoria')
    else:
        try:
            datetime.strptime(data['fecha'], '%Y-%m-%d')
        except ValueError:
            errores.append('fecha debe tener formato YYYY-MM-DD')

    for campo in ['hora_ingreso_real', 'hora_salida_real',
                  'hora_ingreso_programada', 'hora_salida_programada']:
        if data.get(campo):
            try:
                datetime.strptime(data[campo], '%H:%M')
            except ValueError:
                errores.append(f'{campo} debe tener formato HH:MM')

    if data.get('hora_ingreso_real') and data.get('hora_salida_real'):
        ing = datetime.strptime(data['hora_ingreso_real'], '%H:%M').time()
        sal = datetime.strptime(data['hora_salida_real'], '%H:%M').time()
        if sal < ing:
            errores.append('hora_salida_real no puede ser anterior a hora_ingreso_real')
    return errores

# ---------- ENDPOINTS ----------

@app.route('/api/marcaciones', methods=['POST'])
def crear_marcacion():
    data = request.get_json()
    errores = validar_marcacion(data)
    if errores:
        return jsonify({'errores': errores}), 400

    estado = calcular_estado(data.get('hora_ingreso_programada'), data.get('hora_ingreso_real'))

    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            INSERT INTO marcaciones (
                codigo_empleado, nombre_empleado, fecha,
                hora_ingreso_programada, hora_ingreso_real,
                hora_salida_programada, hora_salida_real,
                estado, observacion
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            data['codigo_empleado'], data.get('nombre_empleado', ''), data['fecha'],
            data.get('hora_ingreso_programada'), data.get('hora_ingreso_real'),
            data.get('hora_salida_programada'), data.get('hora_salida_real'),
            estado, data.get('observacion')
        ))
        nueva = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(nueva), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/marcaciones', methods=['GET'])
def listar_marcaciones():
    empleado = request.args.get('empleado')
    fecha = request.args.get('fecha')
    query = "SELECT * FROM marcaciones WHERE 1=1"
    params = []
    if empleado:
        query += " AND codigo_empleado = %s"
        params.append(empleado)
    if fecha:
        query += " AND fecha = %s"
        params.append(fecha)
    query += " ORDER BY fecha DESC, id DESC"

    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(query, params)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(rows), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/marcaciones/<int:id>', methods=['GET'])
def obtener_marcacion(id):
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM marcaciones WHERE id = %s", (id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return jsonify(row), 200
        return jsonify({'error': 'No encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/marcaciones/<int:id>', methods=['PUT'])
def actualizar_marcacion(id):
    data = request.get_json()
    errores = validar_marcacion(data)
    if errores:
        return jsonify({'errores': errores}), 400

    estado = calcular_estado(data.get('hora_ingreso_programada'), data.get('hora_ingreso_real'))

    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            UPDATE marcaciones SET
                codigo_empleado=%s, nombre_empleado=%s, fecha=%s,
                hora_ingreso_programada=%s, hora_ingreso_real=%s,
                hora_salida_programada=%s, hora_salida_real=%s,
                estado=%s, observacion=%s
            WHERE id=%s RETURNING *
        """, (
            data['codigo_empleado'], data.get('nombre_empleado', ''), data['fecha'],
            data.get('hora_ingreso_programada'), data.get('hora_ingreso_real'),
            data.get('hora_salida_programada'), data.get('hora_salida_real'),
            estado, data.get('observacion'), id
        ))
        actualizada = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if actualizada:
            return jsonify(actualizada), 200
        return jsonify({'error': 'No encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/marcaciones/<int:id>', methods=['DELETE'])
def eliminar_marcacion(id):
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM marcaciones WHERE id = %s RETURNING id", (id,))
        deleted = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        if deleted:
            return jsonify({'mensaje': 'Eliminado'}), 200
        return jsonify({'error': 'No encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)