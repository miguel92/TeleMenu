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
from views import Login,Registro,AdminMenus, misPedidos, listarRestaurantes, AdminUsuarios, usuario
from flask import Flask,render_template, request, redirect, url_for,session
from models import ConnectFirebase, Pedido, Usuario
import folium
import unicodedata

# Python standard libraries
import json
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Third party libraries
from flask import Flask, redirect, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from oauthlib.oauth2 import WebApplicationClient
import requests

# Configuration
GOOGLE_CLIENT_ID = "724763817794-ggc2ttdiijonm72qd27s1fjkk3a0sglm.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "-FLrj22Pal8oD8X2u2HLfzw3"
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

app = Flask(__name__,static_url_path='/static')
app.secret_key = GOOGLE_CLIENT_SECRET

@app.route('/')
def root():
    return render_template('wb.html', datos=None)

@app.route('/searchLista')
def searchLista():
    restaurantes = listarRestaurantes.getListaRestaurantes()
    return render_template('searchLista.html', datos = restaurantes)

@app.route('/map')
def mapaRestaurantesCercanos():
    restaurantes = listarRestaurantes.getRestaurantesCercanosMapa()
    misCoord = usuario.getCoordDireccion()
    map = folium.Map(
        left='20%',
        width=700,
        height=500,
        location = [misCoord.latitude, misCoord.longitude],
        zoom_start = 15
    )
    
    
    for mark in restaurantes:
        lat = float(mark.geo_location['lat'])
        lng = float(mark.geo_location['lng'])
        lat_lng = (lat,lng)
        nombre = unicodedata.normalize('NFD', mark.name)
        nombre = nombre.encode("utf8").decode("ascii","ignore")
        key = listarRestaurantes.getKeyRestaurante(nombre)
        html = folium.Html('<div style="text-align:center"><h4>' + nombre + '</h4><a href="/listarMenusRestauranteWeb/' + key + '" class="btn btn-success enlaceMenusMapa" target="_top"><i class="fas fa-utensils"></i> Ver Menus</a></div>', script=True)
        folium.Marker(
            name = "hola",
            location=lat_lng,
            popup=folium.Popup(html, max_width=300, height=500),
            tooltip="Click aqui"
        ).add_to(map)
    return render_template('map.html',map=map._repr_html_())
@app.route('/pedidos')
def pedidos():
    return render_template('pedidos.html', datos=None)

@app.route('/pedidosPendientes')
def pedidosPendientes():
    pedidos = misPedidos.getMisPedidos("pendiente")
    return render_template('pedidosPendientes.html', datos=pedidos)

@app.route('/pedidosAnteriores')
def pedidosAnteriores():
    pedidos = misPedidos.getMisPedidos("terminado")
    pedidosLista = list(pedidos)
    if (pedidosLista.__len__() > 0):
        return render_template('pedidosAnteriores.html', datos=pedidos)
    else:
        return render_template('pedidosAnteriores.html', datos=None)

@app.route('/borrarPedido/<id_pedido>', methods=["GET", "POST"])
def borrarPedido(id_pedido):
    misPedidos.deletePedido(id_pedido)
    return redirect(url_for('pedidosAnteriores'))
 
@app.route('/listarMenusRestauranteWeb/<id_restaurante>', methods=["GET", "POST"])
def listarMenusRestauranteWeb(id_restaurante):
    menus = listarRestaurantes.getListaMenusRestaurante(id_restaurante)
    if (menus.__len__() > 0):
        pedido = request.get_json()
        if (pedido is not None):
            misPedidos.crearPedido(pedido, id_restaurante)
        
        return render_template('listaMenusRestaurante.html', datos=menus)
    else:
        return render_template('listaMenusRestaurante.html', datos=None)
    
       

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

# SE DESESTIMA C DE USUARIOS EN FAVOR DE OAUTH
#@app.route("/crearUsuario", methods=["GET", "POST"])
#def crear_usuario():
#    datos = AdminUsuarios().create(request)
#    
#    if datos[0]=="listarUsuarios.html":
#        return redirect(url_for('listarUsuarios'))
#    else:
#        return render_template(datos[0], datos = datos[1])

@app.route('/listarUsuarios')
def listarUsuarios():
    datos = AdminUsuarios.getListaUsuarios()
    return render_template('admin/listarUsuarios.html', datos = datos)
    
@app.route('/editarUsuario/<id_usuario>', methods=["GET", "POST"])
def editarUsuario(id_usuario):
    usuario = AdminUsuarios.getUsuario(id_usuario)
    datos = AdminUsuarios.update(request,id_usuario)
    
    if datos is not None:
        return redirect(url_for('listarUsuarios'))
    
    return render_template('admin/editarUsuario.html', datos = usuario)

    
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

@app.route('/listarMenusRestaurante')
def listarMenusRestaurante():
    menus = AdminMenus.getLista()
    return render_template('admin/listarMenus.html', datos = menus)

@app.route('/crearMenu',methods=["GET", "POST"])
def crearMenu():
    datos = AdminMenus().create(request)
    listaRes = listarRestaurantes.getListaRestaurantes()
    if datos[0]=="listarMenu.html":
        return redirect(url_for('listarMenu'))
    else:
        return render_template(datos[0], datos = datos[1], datos2=listaRes)

@app.route('/editarMenu/<id_menu>', methods=["GET", "POST"])
def editarMenu(id_menu):
    menus = AdminMenus.get(id_menu)
    datos = AdminMenus.update(request,id_menu)
    listaRes = listarRestaurantes.getListaRestaurantes()
    if datos is not None:
        return redirect(url_for('listarMenu'))
    
    return render_template('admin/editarMenu.html', datos = menus, datos2=listaRes)

@app.route('/borrarMenu/<id_menu>', methods=["GET", "POST"])
def borrarMenu(id_menu):
    AdminMenus.delete(id_menu)
    return redirect(url_for('listarMenu'))

@app.route('/loginGoogle', methods=["GET", "POST"])
def loginGoogle():
    perfil = request.get_json()
    print(perfil)
    existe = Login().checkUser(perfil)
    data = json.dumps({'redirect': existe})
    return data


# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.unauthorized_handler
def unauthorized():
    return "You must be logged in to access this content.", 403

# OAuth2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)


# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return Usuario.get(user_id)

@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in our db with the information provided
    # by Google
    firebase = ConnectFirebase().firebase
    db = firebase.database()
        
    user_by_id = db.child("Usuarios").order_by_child("correo").equal_to(users_email).get().val()
    
    session['nombre'] = users_name
    session['id'] = unique_id
    session['correo'] = users_email
     
       
    if user_by_id == []:
        print("usuario no existe")
        datosGoogle = {"id": unique_id ,"nombre" : users_name, "correo":users_email}
        session['nombre'] = users_name
        session['id'] = unique_id
        session['correo'] = users_email
        return redirect(url_for("show_register_form"))
    
    clave = list(user_by_id)[0]
    session['rol'] = user_by_id[clave]['rol']
    session['user'] = users_email
    user = Usuario(
        id_=unique_id, name=users_name, email=users_email, rol = user_by_id[clave]['rol']
    )
    
    login_user(user)
    
    # Send user back to homepage
    return redirect(url_for("root"))

@app.route("/salir")
@login_required
def salir():
    logout_user()
    session.pop('user',None)
    session.pop('rol',None)
    session.pop('id',None)
    session.pop('correo',None)
    session.clear()
    return redirect(url_for("root"))
def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

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
