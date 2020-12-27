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
from views import Login,Registro,AdminMenus, misPedidos, listarRestaurantes, usuario
from flask import Flask,render_template, request, redirect, url_for,session
from models import ConnectFirebase, Pedido
import folium
import unicodedata

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
