# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_render_template]
import datetime
from views import Humano
from views import Login,Registro,AdminMenus, AdminUsuarios

from flask import Flask,render_template, request, redirect, url_for,session
from models import ConnectFirebase

app = Flask(__name__,static_url_path='/static')
app.secret_key = 'esto-es-una-clave-muy-secreta'
@app.route('/')
def root():
    usuarios = ["adasd",
                   "manuel",
                   "pepe",
                   ]
    usuario = Humano.hola()
    return render_template('wb.html', datos=usuario)

@app.route('/search')
def search():
    return render_template('search.html', busqueda = None)

@app.route("/signup", methods=["GET", "POST"])
def show_signup_form():
    datos= Login.get(request)
    
    if datos[0]=="wb.html":
        return redirect(url_for('root'))
    elif datos[0] =='next':
        return redirect(next)
    else:
        return render_template(datos[0],datos=datos[1])
    
@app.route("/register", methods=["GET", "POST"])
def show_register_form():
    datos = Registro.get(request)
    return render_template(datos[0],datos=datos[1])

@app.route("/crearUsuario", methods=["GET", "POST"])
def crear_usuario():
    
    
    datos = AdminUsuarios().create(request)
    
    if datos[0]=="listarUsuarios.html":
        return redirect(url_for('listarUsuarios'))
    else:
        return render_template(datos[0], datos = datos[1])

@app.route('/listarUsuarios')
def listarUsuarios():
    datos = AdminUsuarios.getListaUsuarios()
    return render_template('admin/listarUsuarios.html', datos = datos)
    
@app.route('/borrarUsuario/<id_usuario>', methods=["GET", "POST"])
def borrarUsuario(id_usuario):
    AdminUsuarios.delete(id_usuario)
    return redirect(url_for('listarUsuarios'))

    
@app.route('/admin')
def admin():
    return render_template('admin/main.html', busqueda = None)

@app.route('/logout')
def logout():

    session.pop('user_id',None)
    session.pop('rol',None)
    session.clear()
    
    return redirect(url_for('root'))

@app.route('/listarMenu')
def listarMenu():
    menus = AdminMenus.getLista()
    return render_template('admin/listarMenus.html', datos = menus)

@app.route('/crearMenu',methods=["GET", "POST"])
def crearMenu():
    datos = AdminMenus().create(request)
    
    if datos[0]=="listarMenu.html":
        return redirect(url_for('listarMenu'))
    else:
        return render_template(datos[0], datos = datos[1])

@app.route('/editarMenu/<id_menu>', methods=["GET", "POST"])
def editarMenu(id_menu):
    menus = AdminMenus.get(id_menu)
    datos = AdminMenus.update(request,id_menu)
    
    if datos is not None:
        return redirect(url_for('listarMenu'))
    
    return render_template('admin/editarMenu.html', datos = menus)

@app.route('/borrarMenu/<id_menu>', methods=["GET", "POST"])
def borrarMenu(id_menu):
    AdminMenus.delete(id_menu)
    return redirect(url_for('listarMenu'))

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python38_render_template]
