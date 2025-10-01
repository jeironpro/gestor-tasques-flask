from flask import Flask, request, render_template, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

# Aquestes dades haurien d'estar en un fitxer apart "database.py" o ".env"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'gestor_tasques'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Aquesta funció hauria d'estar en un fitxer apart "database.py"
def crea_tables():
	with mysql.connection.cursor() as cur:
		cur.execute("""CREATE TABLE IF NOT EXISTS categoria (id_categoria INT AUTO_INCREMENT PRIMARY KEY, categoria VARCHAR(100) NOT NULL)""");
		cur.execute("""CREATE TABLE IF NOT EXISTS tasca (id_tasca INT AUTO_INCREMENT PRIMARY KEY, tasca VARCHAR(255) NOT NULL, id_categoria INT NOT NULL, FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria) ON DELETE CASCADE ON UPDATE CASCADE)""");
		mysql.connection.commit()

# Agafar els dades de la base de dades que es mostressin en el template
def mostra_tasques():
    tasques_categorias = {}
    with mysql.connection.cursor() as cur:
        cur.execute("""SELECT categoria.id_categoria AS id_categoria, categoria.categoria AS categoria, tasca.id_tasca AS id_tasca, tasca.tasca AS tasca FROM categoria LEFT JOIN tasca ON tasca.id_categoria = categoria.id_categoria ORDER BY categoria.id_categoria, tasca.id_tasca""")
        tasques = cur.fetchall()
        
    for fila in tasques:
        id_cat = fila['id_categoria']
        if id_cat not in tasques_categorias:
            tasques_categorias[id_cat] = {
                'id_categoria': fila['id_categoria'],
                'nom': fila['categoria'],
                'tasques': []
            }
        if fila['id_tasca'] is not None:
            tasques_categorias[id_cat]['tasques'].append({
                'id': fila['id_tasca'],
                'tasca': fila['tasca']
            })
    return tasques_categorias.values()

@app.route('/', methods=['POST', 'GET'])
def index():
    crea_tables() # Crear les tables si no existeixen

    if request.method == "POST":
        categoria = request.form.get('categoria')
        tasca = request.form.get('tasca')

        with mysql.connection.cursor() as cur:
            cur.execute("SELECT id_categoria FROM categoria WHERE categoria = %s", (categoria,))
            categoria_exist = cur.fetchone()

            if not categoria_exist:
                cur.execute("INSERT INTO categoria (categoria) VALUES (%s)", (categoria,))
                mysql.connection.commit()
                cur.execute("SELECT id_categoria FROM categoria WHERE categoria = %s", (categoria,))
                categoria_exist = cur.fetchone()

            cur.execute("INSERT INTO tasca (tasca, id_categoria) VALUES (%s, %s)",(tasca, categoria_exist['id_categoria']))
            mysql.connection.commit()

    tasques = mostra_tasques() # Cridar a la funció que retorna els dades a mostrar
    return render_template('index.html', tasques=tasques)

@app.route('/modificar_tasca/<int:id_tasca>', methods=['POST', 'GET'])
def modificar_tasca(id_tasca):
    if request.method == "POST":
        tasca = request.form.get('tasca')
        with mysql.connection.cursor() as cur:
            cur.execute("UPDATE tasca SET tasca = %s WHERE id_tasca = %s", (tasca, id_tasca))
            mysql.connection.commit()
        return redirect(url_for('index'))

@app.route('/eliminar_tasca/<int:id_tasca>')
def eliminar_tasca(id_tasca):
    with mysql.connection.cursor() as cur:
        cur.execute("DELETE FROM tasca WHERE id_tasca = %s", (id_tasca,))
        mysql.connection.commit()
    return redirect(url_for('index'))

@app.route('/eliminar_categoria/<int:id_categoria>')
def eliminar_categoria(id_categoria):
    with mysql.connection.cursor() as cur:
        cur.execute("DELETE FROM categoria WHERE id_categoria = %s", (id_categoria,))
        mysql.connection.commit()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True) # debug = True perquè no esta a producció