from flask import Flask, request, render_template, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = ''
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''
app.config['MYSQL_PORT'] = 0
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# Configurar els socket només en distribucions linux
app.config['MYSQL_UNIX_SOCKET'] = '/opt/lampp/var/mysql/mysql.sock'

mysql = MySQL(app)

def crea_tables():
	with mysql.connection.cursor() as cur:
		cur.execute("""CREATE TABLE IF NOT EXISTS categoria (id_categoria INT AUTO_INCREMENT PRIMARY KEY, categoria VARCHAR(100) NOT NULL)""");
		cur.execute("""CREATE TABLE IF NOT EXISTS tasca (id_tasca INT AUTO_INCREMENT PRIMARY KEY, tasca VARCHAR(255) NOT NULL, id_categoria INT NOT NULL, FOREIGN KEY (id_categoria) REFERENCES categoria(id_categoria) ON DELETE CASCADE ON UPDATE CASCADE)""");
		mysql.connection.commit()

def mostra_tasques():
    tasques_categorias = {}
    with mysql.connection.cursor() as cur:
        cur.execute("""SELECT categoria.id_categoria AS id_categoria, categoria.categoria AS categoria, tasca.id_tasca AS id_tasca, tasca.tasca AS tasca FROM categoria LEFT JOIN tasca ON tasca.id_categoria = categoria.id_categoria ORDER BY categoria.id_categoria, tasca.id_tasca""")
        tasques = cur.fetchall()
        
    for fila in tasques:
        id_cat = fila['id_categoria']
        if id_cat not in tasques_categorias:
            tasques_categorias[id_cat] = {
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
    crea_tables()
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

    tasques = mostra_tasques()
    return render_template('index.html', tasques=tasques)

@app.route('/modificar_tasca/<int:id_tasca>', methods=['POST', 'GET'])
def modificar_tasca(id_tasca):
    if request.method == "POST":
        tasca = request.form.get('tasca')
        with mysql.connection.cursor() as cur:
            cur.execute("UPDATE tasca SET tasca = %s WHERE id_tasca = %s", (tasca, id_tasca))
            mysql.connection.commit()
        tasques = mostra_tasques()
        return redirect(url_for('index'))

@app.route('/eliminar_tasca/<int:id_tasca>')
def eliminar_tasca(id_tasca):
    with mysql.connection.cursor() as cur:
        cur.execute("DELETE FROM tasca WHERE id_tasca = %s", (id_tasca,))
        mysql.connection.commit()
    return index()

if __name__ == "__main__":
    app.run(debug=True)
