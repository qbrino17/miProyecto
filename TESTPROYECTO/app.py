from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import pooling, errorcode
from contextlib import closing

app = Flask(__name__)

# Configuración del pool de conexiones MySQL
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "proyecto"
}

# Crear un pool de conexiones (5 conexiones máximo)
connection_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    **db_config
)

# ==================== RUTAS DE VISTAS ====================
@app.route("/")
def index():
    return render_template("inicio.html")

@app.route("/menu")
def menu():
    return render_template("menu.html")

@app.route("/perfil")
def perfil():
    return render_template("perfil.html")

@app.route("/auditoria")
def auditoria():
    return render_template("auditoria.html")

@app.route("/inicio")
def inicio():
    return render_template("inicio.html")

@app.route("/distritos")
def distritos():
    return render_template("distritos.html")

@app.route("/productos")
def productos():
    return render_template("productos.html")

@app.route("/proveedores")
def proveedores():
    return render_template("proveedores.html")

@app.route("/vendedores")
def vendedores():
    return render_template("vendedores.html")

@app.route("/clientes")
def clientes():
    return render_template("clientes.html")

@app.route("/ordenes_compra")
def ordenes_compra():
    return render_template("ordenes_compra.html")

@app.route("/facturas")
def facturas():
    return render_template("facturas.html")

@app.route("/abastecimientos")
def abastecimientos():
    return render_template("abastecimientos.html")


@app.route("/detalle_compras")
def detalle_compras():
    return render_template("detalle_compras.html")

@app.route("/detalle_facturas")
def detalle_facturas():
    return render_template("detalle_facturas.html")

@app.route("/reporte_vendedores")
def reporte_vendedores():
    return render_template("reporte_vendedores.html")


@app.route("/reporte_auditoria")
def reporte_auditoria():
    return render_template("reporte_auditoria.html")


#API AUDITORIA
@app.route("/api/auditoria", methods=["GET", "POST", "PUT", "DELETE"])
def api_auditoria():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)

        if request.method == "GET":
            pagina = int(request.args.get("pagina", 1))
            por_pagina = int(request.args.get("por_pagina", 5))
            offset = (pagina - 1) * por_pagina

            cursor.execute("SELECT COUNT(*) AS total FROM AUDITORIA")
            total = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT id, tabla_afectada, tipo_operacion, usuario, fecha, codigo_afectado
                FROM AUDITORIA
                ORDER BY id
                LIMIT %s OFFSET %s
            """, (por_pagina, offset))
            resultados = cursor.fetchall()

            return jsonify({
                "auditorias": resultados,
                "total_paginas": (total + por_pagina - 1) // por_pagina
            })

        elif request.method == "POST":
            data = request.get_json()
            cursor.execute("""
                INSERT INTO AUDITORIA (tabla_afectada, tipo_operacion, usuario, codigo_afectado)
                VALUES (%s, %s, %s, %s)
            """, (
                data.get("tabla_afectada"),
                data.get("tipo_operacion"),
                data.get("usuario", "admin"),  # Default a admin si no viene
                data.get("codigo_afectado")
            ))
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "PUT":
            data = request.get_json()
            cursor.execute("""
                UPDATE AUDITORIA
                SET tabla_afectada = %s,
                    tipo_operacion = %s,
                    usuario = %s,
                    codigo_afectado = %s
                WHERE id = %s
            """, (
                data.get("tabla_afectada"),
                data.get("tipo_operacion"),
                data.get("usuario", "admin"),
                data.get("codigo_afectado"),
                data.get("id")
            ))
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "DELETE":
            data = request.get_json()
            cursor.execute("DELETE FROM AUDITORIA WHERE id = %s", (data.get("id"),))
            conexion.commit()
            return jsonify({"success": True})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()

@app.route("/api/auditoria/reporte", methods=["GET"])
def api_auditoria_reporte():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)

        # Obtener parámetros de fecha
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")
        usuario = request.args.get("usuario")
        tipo_operacion = request.args.get("tipo_operacion")

        # Construir consulta SQL dinámica
        sql = "SELECT id, tabla_afectada, tipo_operacion, usuario, fecha, codigo_afectado FROM AUDITORIA WHERE 1=1"
        params = []

        if fecha_inicio:
            sql += " AND fecha >= %s"
            params.append(fecha_inicio)
        if fecha_fin:
            sql += " AND fecha <= %s"
            params.append(fecha_fin + " 23:59:59")  # Para incluir todo el día
        if usuario:
            sql += " AND usuario = %s"
            params.append(usuario)
        if tipo_operacion:
            sql += " AND tipo_operacion = %s"
            params.append(tipo_operacion)

        sql += " ORDER BY fecha DESC"

        cursor.execute(sql, params)
        resultados = cursor.fetchall()

        return jsonify({
            "success": True,
            "auditorias": resultados,
            "total_registros": len(resultados)
        })

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()            

# ==================== API DE DISTRITOS ====================
@app.route("/api/distritos", methods=["GET", "POST", "PUT", "DELETE"])
def api_distritos():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)

        if request.method == "GET":
            pagina = int(request.args.get("pagina", 1))
            por_pagina = int(request.args.get("por_pagina", 5))
            offset = (pagina - 1) * por_pagina

            cursor.execute("SELECT COUNT(*) AS total FROM DISTRITO")
            total = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COD_DIS, NOM_DIS
                FROM DISTRITO
                ORDER BY COD_DIS
                LIMIT %s OFFSET %s
            """, (por_pagina, offset))
            resultados = cursor.fetchall()

            return jsonify({
                "distritos": resultados,
                "total_paginas": (total + por_pagina - 1) // por_pagina
            })

        elif request.method == "POST":
            data = request.get_json()
            cursor.execute("""
                INSERT INTO DISTRITO (COD_DIS, NOM_DIS)
                VALUES (%s, %s)
            """, (data["COD_DIS"], data["NOM_DIS"]))
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "PUT":
            data = request.get_json()
            cursor.execute("""
                UPDATE DISTRITO
                SET NOM_DIS = %s
                WHERE COD_DIS = %s
            """, (data["NOM_DIS"], data["COD_DIS"]))
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "DELETE":
            data = request.get_json()
            cursor.execute("DELETE FROM DISTRITO WHERE COD_DIS = %s", (data["COD_DIS"],))
            conexion.commit()
            return jsonify({"success": True})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()

# ==================== API DE PRODUCTOS ====================
@app.route("/api/productos", methods=["GET", "POST", "PUT", "DELETE"])
def api_productos():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)

        if request.method == "GET":
            pagina = int(request.args.get("pagina", 1))
            por_pagina = int(request.args.get("por_pagina", 5))
            offset = (pagina - 1) * por_pagina

            cursor.execute("SELECT COUNT(*) AS total FROM PRODUCTO")
            total = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COD_PRO, DES_PRO, PRE_PRO, SAC_PRO, SMI_PRO, UNI_PRO, LIN_PRO, IMP_PRO
                FROM PRODUCTO
                ORDER BY COD_PRO
                LIMIT %s OFFSET %s
            """, (por_pagina, offset))
            productos = cursor.fetchall()

            return jsonify({
                "productos": productos,
                "total_paginas": (total + por_pagina - 1) // por_pagina
            })

        elif request.method == "POST":
            data = request.get_json()
            cursor.execute("""
                INSERT INTO PRODUCTO (COD_PRO, DES_PRO, PRE_PRO, SAC_PRO, SMI_PRO, UNI_PRO, LIN_PRO, IMP_PRO)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data["COD_PRO"],
                data["DES_PRO"],
                data["PRE_PRO"],
                data["SAC_PRO"],
                data["SMI_PRO"],
                data["UNI_PRO"],
                data["LIN_PRO"],
                data["IMP_PRO"]
            ))
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "PUT":
            data = request.get_json()
            cursor.execute("""
                UPDATE PRODUCTO
                SET DES_PRO = %s,
                    PRE_PRO = %s,
                    SAC_PRO = %s,
                    SMI_PRO = %s,
                    UNI_PRO = %s,
                    LIN_PRO = %s,
                    IMP_PRO = %s
                WHERE COD_PRO = %s
            """, (
                data["DES_PRO"],
                data["PRE_PRO"],
                data["SAC_PRO"],
                data["SMI_PRO"],
                data["UNI_PRO"],
                data["LIN_PRO"],
                data["IMP_PRO"],
                data["COD_PRO"]
            ))
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "DELETE":
            data = request.get_json()
            cursor.execute("DELETE FROM PRODUCTO WHERE COD_PRO = %s", (data["COD_PRO"],))
            conexion.commit()
            return jsonify({"success": True})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()

@app.route("/api/productos/count")
def count_productos():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS total FROM PRODUCTO")
        total = cursor.fetchone()["total"]
        return jsonify({"total": total})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()

@app.route("/api/productos/por-linea")
def productos_por_linea():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                LIN_PRO as linea,
                COUNT(*) as cantidad
            FROM PRODUCTO
            GROUP BY LIN_PRO
            ORDER BY LIN_PRO
        """)
        
        resultados = cursor.fetchall()
        
        lineas = {
            'labels': [],
            'cantidad': []
        }
        
        for item in resultados:
            lineas['labels'].append(f"Línea {item['linea']}")
            lineas['cantidad'].append(item['cantidad'])
        
        return jsonify(lineas)
        
    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()    

# ==================== API DE PROVEEDORES ====================
@app.route("/api/proveedores", methods=["GET", "POST", "PUT", "DELETE"])
def api_proveedores():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)

        if request.method == "GET":
            pagina = int(request.args.get("pagina", 1))
            por_pagina = int(request.args.get("por_pagina", 5))
            offset = (pagina - 1) * por_pagina

            cursor.execute("SELECT COUNT(*) AS total FROM PROVEEDOR")
            total = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COD_PRV, RSO_PRV, DIR_PRV, TEL_PRV, COD_DIS, REP_PRO
                FROM PROVEEDOR
                ORDER BY COD_PRV
                LIMIT %s OFFSET %s
            """, (por_pagina, offset))
            resultados = cursor.fetchall()

            return jsonify({
                "proveedores": resultados,
                "total_paginas": (total + por_pagina - 1) // por_pagina
            })

        elif request.method == "POST":
            data = request.get_json()
            cursor.execute("""
                INSERT INTO PROVEEDOR (COD_PRV, RSO_PRV, DIR_PRV, TEL_PRV, COD_DIS, REP_PRO)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                data["COD_PRV"],
                data["RSO_PRV"],
                data["DIR_PRV"],
                data["TEL_PRV"],
                data["COD_DIS"],
                data["REP_PRO"]
            ))
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "PUT":
            data = request.get_json()
            cursor.execute("""
                UPDATE PROVEEDOR
                SET RSO_PRV = %s,
                    DIR_PRV = %s,
                    TEL_PRV = %s,
                    COD_DIS = %s,
                    REP_PRO = %s
                WHERE COD_PRV = %s
            """, (
                data["RSO_PRV"],
                data["DIR_PRV"],
                data["TEL_PRV"],
                data["COD_DIS"],
                data["REP_PRO"],
                data["COD_PRV"]
            ))
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "DELETE":
            data = request.get_json()
            cursor.execute("DELETE FROM PROVEEDOR WHERE COD_PRV = %s", (data["COD_PRV"],))
            conexion.commit()
            return jsonify({"success": True})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()

@app.route("/api/proveedores/count")
def count_proveedor():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS total FROM PROVEEDOR")
        total = cursor.fetchone()["total"]
        return jsonify({"total": total})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()

@app.route("/api/proveedores/lista", methods=["GET"])
def api_proveedores_lista():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT COD_PRV, NOM_PRV 
            FROM PROVEEDOR 
            ORDER BY NOM_PRV
        """)
        proveedores = cursor.fetchall()
        
        return jsonify(proveedores)
    
    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()

@app.route("/api/productos/lista", methods=["GET"])
def api_productos_lista():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT COD_PRO, DES_PRO 
            FROM PRODUCTO 
            ORDER BY DES_PRO
        """)
        productos = cursor.fetchall()
        
        return jsonify(productos)
    
    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()


# ==================== API DE VENDEDORES ====================
@app.route("/api/vendedores/count")
def count_vendedores():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS total FROM VENDEDOR")
        total = cursor.fetchone()["total"]
        return jsonify({"total": total})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()

@app.route("/api/vendedores", methods=["GET", "POST", "PUT", "DELETE"])
def api_vendedores():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)

        if request.method == "GET":
            pagina = int(request.args.get("pagina", 1))
            por_pagina = int(request.args.get("por_pagina", 5))
            offset = (pagina - 1) * por_pagina

            cursor.execute("SELECT COUNT(*) AS total FROM VENDEDOR")
            total = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COD_VEN, NOM_VEN, APE_VEN, SUE_VEN, FIN_VEN, TIP_VEN, COD_DIS
                FROM VENDEDOR
                ORDER BY COD_VEN
                LIMIT %s OFFSET %s
            """, (por_pagina, offset))
            vendedores = cursor.fetchall()

            return jsonify({
                "vendedores": vendedores,
                "total_paginas": (total + por_pagina - 1) // por_pagina
            })

        elif request.method == "POST":
            data = request.get_json()
            cursor.execute("""
                INSERT INTO VENDEDOR (COD_VEN, NOM_VEN, APE_VEN, SUE_VEN, FIN_VEN, TIP_VEN, COD_DIS)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data["COD_VEN"],
                data["NOM_VEN"],
                data["APE_VEN"],
                data["SUE_VEN"],
                data.get("FIN_VEN", None),
                data.get("TIP_VEN", None),
                data["COD_DIS"]
            ))
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "PUT":
            data = request.get_json()
            cursor.execute("""
                UPDATE VENDEDOR
                SET NOM_VEN = %s,
                    APE_VEN = %s,
                    SUE_VEN = %s,
                    FIN_VEN = %s,
                    TIP_VEN = %s,
                    COD_DIS = %s
                WHERE COD_VEN = %s
            """, (
                data["NOM_VEN"],
                data["APE_VEN"],
                data["SUE_VEN"],
                data.get("FIN_VEN", None),
                data.get("TIP_VEN", None),
                data["COD_DIS"],
                data["COD_VEN"]
            ))
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "DELETE":
            data = request.get_json()
            cursor.execute("DELETE FROM VENDEDOR WHERE COD_VEN = %s", (data["COD_VEN"],))
            conexion.commit()
            return jsonify({"success": True})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()

@app.route("/api/vendedores/lista", methods=["GET"])
def api_vendedores_lista():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT COD_VEN, NOM_VEN 
            FROM VENDEDOR 
            ORDER BY NOM_VEN
        """)
        vendedores = cursor.fetchall()
        
        return jsonify(vendedores)
    
    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()

# ============ API PARA VENDEDORES CON MENOS VENTAS (ACTUALIZADO) =============
@app.route("/api/vendedores/peores", methods=["GET"])
def api_vendedores_peores():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        limit = int(request.args.get("limit", 5))
        
        cursor.execute("""
            SELECT v.COD_VEN, 
                   CONCAT(v.NOM_VEN, ' ', v.APE_VEN) AS nombre_completo,
                   COALESCE(SUM(df.CAN_VEN * df.PRE_VEN), 0) AS total_ventas
            FROM VENDEDOR v
            LEFT JOIN FACTURA f ON v.COD_VEN = f.COD_VEN
            LEFT JOIN DETALLE_FACTURA df ON f.NUM_FAC = df.NUM_FAC
            GROUP BY v.COD_VEN
            ORDER BY total_ventas ASC
            LIMIT %s
        """, (limit,))
        
        resultados = cursor.fetchall()
        return jsonify({"vendedores": resultados})
    
    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    finally:
        if cursor: cursor.close()
        if conexion: conexion.close()


# ==================== API DE CLIENTES =========================================================================================================================================================
@app.route("/api/clientes", methods=["GET", "POST", "PUT", "DELETE"])
def api_clientes():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)

        if request.method == "GET":
            pagina = int(request.args.get("pagina", 1))
            por_pagina = int(request.args.get("por_pagina", 5))
            offset = (pagina - 1) * por_pagina

            cursor.execute("SELECT COUNT(*) AS total FROM CLIENTE")
            total = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT COD_CLI, RSO_CLI, DIR_CLI, TLF_CLI, RUC_CLI, COD_DIS, FEC_REG, TIP_CLI, CON_CLI
                FROM CLIENTE
                ORDER BY COD_CLI
                LIMIT %s OFFSET %s
            """, (por_pagina, offset))
            resultados = cursor.fetchall()

            return jsonify({
                "clientes": resultados,
                "total_paginas": (total + por_pagina - 1) // por_pagina
            })

        elif request.method == "POST":
            data = request.get_json()
            cursor.execute("""
                INSERT INTO CLIENTE (COD_CLI, RSO_CLI, DIR_CLI, TLF_CLI, RUC_CLI, COD_DIS, FEC_REG, TIP_CLI, CON_CLI)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data["COD_CLI"],
                data["RSO_CLI"],
                data["DIR_CLI"],
                data["TLF_CLI"],
                data["RUC_CLI"],
                data["COD_DIS"],
                data["FEC_REG"],
                data["TIP_CLI"],
                data["CON_CLI"]
            ))
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "PUT":
            data = request.get_json()
            cursor.execute("""
                UPDATE CLIENTE
                SET RSO_CLI = %s,
                    DIR_CLI = %s,
                    TLF_CLI = %s,
                    RUC_CLI = %s,
                    COD_DIS = %s,
                    FEC_REG = %s,
                    TIP_CLI = %s,
                    CON_CLI = %s
                WHERE COD_CLI = %s
            """, (
                data["RSO_CLI"],
                data["DIR_CLI"],
                data["TLF_CLI"],
                data["RUC_CLI"],
                data["COD_DIS"],
                data["FEC_REG"],
                data["TIP_CLI"],
                data["CON_CLI"],
                data["COD_CLI"]
            ))
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "DELETE":
            data = request.get_json()
            cursor.execute("DELETE FROM CLIENTE WHERE COD_CLI = %s", (data["COD_CLI"],))
            conexion.commit()
            return jsonify({"success": True})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()

@app.route("/api/clientes/count")
def count_clientes():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS total FROM CLIENTE")
        total = cursor.fetchone()["total"]
        return jsonify({"total": total})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()

@app.route("/api/clientes/lista", methods=["GET"])
def api_clientes_lista():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT COD_CLI, RSO_CLI 
            FROM CLIENTE 
            ORDER BY RSO_CLI
        """)
        clientes = cursor.fetchall()
        
        return jsonify(clientes)
    
    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()

# ==================== API DE ORDENES DE COMPRA  ===============================================================================================================================

@app.route("/api/ordenes_compra", methods=["GET", "POST", "PUT", "DELETE"])
def api_ordenes_compra():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)

        if request.method == "GET":
            pagina = int(request.args.get("pagina", 1))
            por_pagina = int(request.args.get("por_pagina", 5))
            offset = (pagina - 1) * por_pagina

            # Obtener el total de registros
            cursor.execute("SELECT COUNT(*) AS total FROM ORDEN_COMPRA")
            total = cursor.fetchone()["total"]

            # Obtener las órdenes de compra paginadas
            cursor.execute("""
                SELECT NUM_OCO, FEC_OCO, COD_PRV, FAT_OCO, EST_OCO
                FROM ORDEN_COMPRA
                ORDER BY NUM_OCO
                LIMIT %s OFFSET %s
            """, (por_pagina, offset))
            ordenes = cursor.fetchall()

            return jsonify({
                "ordenes": ordenes,
                "total_paginas": (total + por_pagina - 1) // por_pagina
            })

        elif request.method == "POST":
            data = request.get_json()
            cursor.execute("""
                INSERT INTO ORDEN_COMPRA (NUM_OCO, FEC_OCO, COD_PRV, FAT_OCO, EST_OCO)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                data["NUM_OCO"],
                data["FEC_OCO"],
                data["COD_PRV"],
                data["FAT_OCO"],
                data["EST_OCO"]
            ))
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "PUT":
            data = request.get_json()
            cursor.execute("""
                UPDATE ORDEN_COMPRA
                SET FEC_OCO = %s,
                    COD_PRV = %s,
                    FAT_OCO = %s,
                    EST_OCO = %s
                WHERE NUM_OCO = %s
            """, (
                data["FEC_OCO"],
                data["COD_PRV"],
                data["FAT_OCO"],
                data["EST_OCO"],
                data["NUM_OCO"]
            ))
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "DELETE":
            data = request.get_json()
            cursor.execute("DELETE FROM ORDEN_COMPRA WHERE NUM_OCO = %s", (data["NUM_OCO"],))
            conexion.commit()
            return jsonify({"success": True})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()


# ==================== API DE FACTURA  ====================
@app.route("/api/facturas", methods=["GET", "POST", "PUT", "DELETE"])
def api_facturas():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)

        if request.method == "GET":
            pagina = int(request.args.get("pagina", 1))
            por_pagina = int(request.args.get("por_pagina", 5))
            offset = (pagina - 1) * por_pagina

            # Obtener el total de registros
            cursor.execute("SELECT COUNT(*) AS total FROM FACTURA")
            total = cursor.fetchone()["total"]

            # Obtener las facturas paginadas con información de cliente y vendedor
            cursor.execute("""
                SELECT f.NUM_FAC, f.FEC_FAC, f.COD_CLI, c.RSO_CLI AS NOM_CLI, 
                       f.FEC_CAN, f.EST_FAC, f.COD_VEN, v.NOM_VEN, f.POR_IGV
                FROM FACTURA f
                LEFT JOIN CLIENTE c ON f.COD_CLI = c.COD_CLI
                LEFT JOIN VENDEDOR v ON f.COD_VEN = v.COD_VEN
                ORDER BY f.NUM_FAC
                LIMIT %s OFFSET %s
            """, (por_pagina, offset))
            facturas = cursor.fetchall()

            return jsonify({
                "facturas": facturas,
                "total_paginas": (total + por_pagina - 1) // por_pagina
            })

        elif request.method == "POST":
            data = request.get_json()
            cursor.execute("""
                INSERT INTO FACTURA (NUM_FAC, FEC_FAC, COD_CLI, FEC_CAN, EST_FAC, COD_VEN, POR_IGV)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data["NUM_FAC"],
                data["FEC_FAC"],
                data["COD_CLI"],
                data["FEC_CAN"] if data["FEC_CAN"] else None,  # Fecha de cancelación puede ser nula
                data["EST_FAC"],
                data["COD_VEN"],
                data["POR_IGV"]
            ))
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "PUT":
            data = request.get_json()
            cursor.execute("""
                UPDATE FACTURA
                SET FEC_FAC = %s,
                    COD_CLI = %s,
                    FEC_CAN = %s,
                    EST_FAC = %s,
                    COD_VEN = %s,
                    POR_IGV = %s
                WHERE NUM_FAC = %s
            """, (
                data["FEC_FAC"],
                data["COD_CLI"],
                data["FEC_CAN"] if data["FEC_CAN"] else None,
                data["EST_FAC"],
                data["COD_VEN"],
                data["POR_IGV"],
                data["NUM_FAC"]
            ))
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "DELETE":
            data = request.get_json()
            cursor.execute("DELETE FROM FACTURA WHERE NUM_FAC = %s", (data["NUM_FAC"],))
            conexion.commit()
            return jsonify({"success": True})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()


@app.route("/api/facturas/por-estado", methods=["GET"])
def api_facturas_por_estado():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)

        # Consulta para contar facturas por estado
        cursor.execute("""
            SELECT 
                EST_FAC as estado,
                COUNT(*) as cantidad,
                CASE 
                    WHEN EST_FAC = 1 THEN 'Cancelada'
                    WHEN EST_FAC = 2 THEN 'Pagada'
                    WHEN EST_FAC = 3 THEN 'Anulada'
                    WHEN EST_FAC = 4 THEN 'Pendiente'
                    ELSE 'Desconocido'
                END as nombre_estado
            FROM FACTURA
            GROUP BY EST_FAC
            ORDER BY EST_FAC
        """)
        
        resultados = cursor.fetchall()
        
        # Procesar resultados para el gráfico
        estados = []
        cantidades = []
        colores = []
        
        for row in resultados:
            estados.append(row['nombre_estado'])
            cantidades.append(row['cantidad'])
            
            # Asignar colores según el estado
            if row['estado'] == 1:  # Cancelada
                colores.append('#ff5252')
            elif row['estado'] == 2:  # Pagada
                colores.append('#4caf50')
            elif row['estado'] == 3:  # Anulada
                colores.append('#9e9e9e')
            elif row['estado'] == 4:  # Pendiente
                colores.append('#ff9800')
            else:
                colores.append('#607d8b')
        
        return jsonify({
            "estados": estados,
            "cantidades": cantidades,
            "colores": colores
        })

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()
     

# ==================== API DE ABASTECIMIENTO  ====================
@app.route("/api/abastecimientos", methods=["GET", "POST", "PUT", "DELETE"])
def api_abastecimientos():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)

        if request.method == "GET":
            pagina = int(request.args.get("pagina", 1))
            por_pagina = int(request.args.get("por_pagina", 5))
            offset = (pagina - 1) * por_pagina

            # Obtener el total de registros
            cursor.execute("SELECT COUNT(*) AS total FROM ABASTECIMIENTO")
            total = cursor.fetchone()["total"]

            # Obtener los abastecimientos paginados con información de proveedor y producto
            cursor.execute("""
                SELECT a.COD_PRV, p.RSO_PRV, a.COD_PRO, r.DES_PRO, a.PRE_ABA
                FROM ABASTECIMIENTO a
                JOIN PROVEEDOR p ON a.COD_PRV = p.COD_PRV
                JOIN PRODUCTO r ON a.COD_PRO = r.COD_PRO
                ORDER BY a.COD_PRV, a.COD_PRO
                LIMIT %s OFFSET %s
            """, (por_pagina, offset))
            abastecimientos = cursor.fetchall()

            return jsonify({
                "abastecimientos": abastecimientos,
                "total_paginas": (total + por_pagina - 1) // por_pagina
            })

        elif request.method == "POST":
            data = request.get_json()
            cursor.execute("""
                INSERT INTO ABASTECIMIENTO (COD_PRV, COD_PRO, PRE_ABA)
                VALUES (%s, %s, %s)
            """, (
                data["COD_PRV"],
                data["COD_PRO"],
                data["PRE_ABA"]
            ))
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "PUT":
            data = request.get_json()
            cursor.execute("""
                UPDATE ABASTECIMIENTO
                SET PRE_ABA = %s
                WHERE COD_PRV = %s AND COD_PRO = %s
            """, (
                data["PRE_ABA"],
                data["COD_PRV"],
                data["COD_PRO"]
            ))
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "DELETE":
            data = request.get_json()
            cursor.execute("""
                DELETE FROM ABASTECIMIENTO 
                WHERE COD_PRV = %s AND COD_PRO = %s
            """, (data["COD_PRV"], data["COD_PRO"]))
            conexion.commit()
            return jsonify({"success": True})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()

# ==================== API DE DETALLE_COMPRA ====================
@app.route("/api/detalle_compras", methods=["GET", "POST", "PUT", "DELETE"])
def api_detalle_compras():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)

        if request.method == "GET":
            # Parámetros de paginación
            pagina = int(request.args.get("pagina", 1))
            por_pagina = int(request.args.get("por_pagina", 5))
            offset = (pagina - 1) * por_pagina
            
            # Parámetros de filtrado
            num_oco = request.args.get("num_oco")
            cod_pro = request.args.get("cod_pro")

            # Consulta base con joins
            query = """
                SELECT dc.NUM_OCO, dc.COD_PRO, p.DES_PRO, dc.CAN_DET, 
                       oc.FEC_OCO, oc.COD_PRV
                FROM DETALLE_COMPRA dc
                JOIN ORDEN_COMPRA oc ON dc.NUM_OCO = oc.NUM_OCO
                JOIN PRODUCTO p ON dc.COD_PRO = p.COD_PRO
            """
            params = []
            where_clauses = []

            # Filtros
            if num_oco:
                where_clauses.append("dc.NUM_OCO = %s")
                params.append(num_oco)
            if cod_pro:
                where_clauses.append("dc.COD_PRO = %s")
                params.append(cod_pro)

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            # Conteo total
            count_query = "SELECT COUNT(*) AS total FROM (" + query + ") AS subquery"
            cursor.execute(count_query, params)
            total = cursor.fetchone()["total"]

            # Consulta paginada
            query += " ORDER BY dc.NUM_OCO DESC, dc.COD_PRO LIMIT %s OFFSET %s"
            params.extend([por_pagina, offset])
            
            cursor.execute(query, params)
            detalles = cursor.fetchall()

            return jsonify({
                "detalles": detalles,
                "total_paginas": (total + por_pagina - 1) // por_pagina
            })

        elif request.method == "POST":
            data = request.get_json()
            # Verificar existencia de la orden y producto
            cursor.execute("SELECT NUM_OCO FROM ORDEN_COMPRA WHERE NUM_OCO = %s", (data["NUM_OCO"],))
            if not cursor.fetchone():
                return jsonify({"success": False, "error": "Orden no existe"}), 400
                
            cursor.execute("SELECT COD_PRO FROM PRODUCTO WHERE COD_PRO = %s", (data["COD_PRO"],))
            if not cursor.fetchone():
                return jsonify({"success": False, "error": "Producto no existe"}), 400

            cursor.execute("""
                INSERT INTO DETALLE_COMPRA (NUM_OCO, COD_PRO, CAN_DET)
                VALUES (%s, %s, %s)
            """, (
                data["NUM_OCO"],
                data["COD_PRO"],
                data["CAN_DET"]
            ))
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "PUT":
            data = request.get_json()
            cursor.execute("""
                UPDATE DETALLE_COMPRA
                SET CAN_DET = %s
                WHERE NUM_OCO = %s AND COD_PRO = %s
            """, (
                data["CAN_DET"],
                data["NUM_OCO"],
                data["COD_PRO"]
            ))
            if cursor.rowcount == 0:
                return jsonify({"success": False, "error": "Registro no encontrado"}), 404
                
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "DELETE":
            data = request.get_json()
            cursor.execute("""
                DELETE FROM DETALLE_COMPRA
                WHERE NUM_OCO = %s AND COD_PRO = %s
            """, (
                data["NUM_OCO"],
                data["COD_PRO"]
            ))
            if cursor.rowcount == 0:
                return jsonify({"success": False, "error": "Registro no encontrado"}), 404
                
            conexion.commit()
            return jsonify({"success": True})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conexion' in locals():
            conexion.close()

# ==================== API DE DETALLE_FACTURA ====================
@app.route("/api/detalle_facturas", methods=["GET", "POST", "PUT", "DELETE"])
def api_detalle_facturas():
    try:
        conexion = connection_pool.get_connection()
        cursor = conexion.cursor(dictionary=True)

        if request.method == "GET":
            # Paginación
            pagina = int(request.args.get("pagina", 1))
            por_pagina = int(request.args.get("por_pagina", 5))
            offset = (pagina - 1) * por_pagina
            
            # Filtros
            num_fac = request.args.get("num_fac")
            cod_pro = request.args.get("cod_pro")

            # Consulta con joins
            query = """
                SELECT df.NUM_FAC, df.COD_PRO, p.DES_PRO, df.CAN_VEN, df.PRE_VEN,
                       f.FEC_FAC, f.COD_CLI
                FROM DETALLE_FACTURA df
                JOIN FACTURA f ON df.NUM_FAC = f.NUM_FAC
                JOIN PRODUCTO p ON df.COD_PRO = p.COD_PRO
            """
            params = []
            where_clauses = []

            if num_fac:
                where_clauses.append("df.NUM_FAC = %s")
                params.append(num_fac)
            if cod_pro:
                where_clauses.append("df.COD_PRO = %s")
                params.append(cod_pro)

            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            # Conteo total
            count_query = "SELECT COUNT(*) AS total FROM (" + query + ") AS subquery"
            cursor.execute(count_query, params)
            total = cursor.fetchone()["total"]

            # Consulta paginada
            query += " ORDER BY df.NUM_FAC DESC, df.COD_PRO LIMIT %s OFFSET %s"
            params.extend([por_pagina, offset])
            
            cursor.execute(query, params)
            detalles = cursor.fetchall()

            return jsonify({
                "detalles": detalles,
                "total_paginas": (total + por_pagina - 1) // por_pagina
            })

        elif request.method == "POST":
            data = request.get_json()
            # Validar existencia
            cursor.execute("SELECT NUM_FAC FROM FACTURA WHERE NUM_FAC = %s", (data["NUM_FAC"],))
            if not cursor.fetchone():
                return jsonify({"success": False, "error": "Factura no existe"}), 400
                
            cursor.execute("SELECT COD_PRO FROM PRODUCTO WHERE COD_PRO = %s", (data["COD_PRO"],))
            if not cursor.fetchone():
                return jsonify({"success": False, "error": "Producto no existe"}), 400

            cursor.execute("""
                INSERT INTO DETALLE_FACTURA (NUM_FAC, COD_PRO, CAN_VEN, PRE_VEN)
                VALUES (%s, %s, %s, %s)
            """, (
                data["NUM_FAC"],
                data["COD_PRO"],
                data["CAN_VEN"],
                data["PRE_VEN"]
            ))
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "PUT":
            data = request.get_json()
            cursor.execute("""
                UPDATE DETALLE_FACTURA
                SET CAN_VEN = %s, PRE_VEN = %s
                WHERE NUM_FAC = %s AND COD_PRO = %s
            """, (
                data["CAN_VEN"],
                data["PRE_VEN"],
                data["NUM_FAC"],
                data["COD_PRO"]
            ))
            if cursor.rowcount == 0:
                return jsonify({"success": False, "error": "Registro no encontrado"}), 404
                
            conexion.commit()
            return jsonify({"success": True})

        elif request.method == "DELETE":
            data = request.get_json()
            cursor.execute("""
                DELETE FROM DETALLE_FACTURA
                WHERE NUM_FAC = %s AND COD_PRO = %s
            """, (
                data["NUM_FAC"],
                data["COD_PRO"]
            ))
            if cursor.rowcount == 0:
                return jsonify({"success": False, "error": "Registro no encontrado"}), 404
                
            conexion.commit()
            return jsonify({"success": True})

    except mysql.connector.Error as err:
        return jsonify({"success": False, "error": str(err)}), 500

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): conexion.close()

# ==================== INICIO DEL SERVIDOR ====================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
