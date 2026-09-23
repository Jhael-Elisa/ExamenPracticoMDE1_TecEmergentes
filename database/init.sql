CREATE TABLE IF NOT EXISTS marcaciones (
    id SERIAL PRIMARY KEY,
    codigo_empleado VARCHAR(20) NOT NULL,
    nombre_empleado VARCHAR(100),
    fecha DATE NOT NULL,
    hora_ingreso_programada TIME,
    hora_ingreso_real TIME,
    hora_salida_programada TIME,
    hora_salida_real TIME,
    estado VARCHAR(20),
    observacion TEXT
);