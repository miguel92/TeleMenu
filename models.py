import pyrebase
import firebase
import time
import requests
from geopy.geocoders import Nominatim
from googleplaces import GooglePlaces, types, lang
import gmaps

class ConnectFirebase():
    config = {
                "apiKey": "AIzaSyAmaKAg407v6ga8aX6snP0J4NoyEXVtxAY",
                "authDomain": "telemenu-firebase.firebaseapp.com",
                "databaseURL": "https://telemenu-firebase-default-rtdb.europe-west1.firebasedatabase.app",
                "storageBucket": "telemenu-firebase.appspot.com"
            }
    firebase = None
    def __init__(self):
        self.firebase = pyrebase.initialize_app(self.config)
        
class Usuario():
    def crearUsuario(data,firebase):
        db = firebase.database()
        db.child("Usuarios").push(data)
    
    def consultarUsuario(user_id,firebase):
        db = firebase.database()
        user_by_id = db.child("Usuarios").order_by_child("user_id").equal_to(user_id).get()
        return users_by_id

    def listarUsuarios(self,firebase):
        db = firebase.database()
        usuarios = db.child("Usuarios").get().val()
        return usuarios
    
    def updateUsuario(self,id_usuario,data,firebase):
        db = firebase.database()
        return db.child("Usuarios").child(id_usuario).update(data)
    
    def deleteUsuario(self,id_usuario,firebase):
        db = firebase.database()
        db.child("Usuarios").child(id_usuario).remove()
    def getUsuario(self,id_usuario, firebase):
        db = firebase.database()
        usuario = db.child("Usuarios").order_by_key().equal_to(id_usuario).get().val()
        return usuario
    def getCoordDireccion(user_id, firebase):
        db = firebase.database()
        usuario = db.child("Usuarios").order_by_key().equal_to(user_id).get().val()
        usuarioLista = list(usuario.values())
        direccion = usuarioLista[0]['direccion']
        geolocator = Nominatim(user_agent="building-an-app-1")
        location = geolocator.geocode(direccion)
        return location

class Menu():
    def crearMenu(data,firebase):
        db = firebase.database()
        db.child("Menus").push(data)
    def listarMenus(self,firebase):
        db = firebase.database()
        menus = db.child("Menus").get().val()
        return menus
    def getMenu(self,id_menu,firebase):
        db = firebase.database()
        menu = db.child("Menus").order_by_key().equal_to(id_menu).get().val()
        return menu
    def updateMenu(self,id_menu,data,firebase):
        db = firebase.database()
        return db.child("Menus").child(id_menu).update(data)
    def deleteMenu(self,id_menu,firebase):
        db = firebase.database()
        db.child("Menus").child(id_menu).remove()
    def createMenu(self,data,firebase):
        db = firebase.database()
        db.child("Menus").push(data)
        
class Pedido():
    def getPedidos(user_id,firebase,estado):
        db = firebase.database()
        pedidos = db.child("Pedidos").order_by_child("Cliente").equal_to(user_id).get().val()
        pedidosEstado = {}
        for key, value in pedidos.items():
            if (value['Estado'] == estado):
                pedidosEstado[key] = value
        return pedidosEstado
    def deletePedido(self,id_pedido,firebase):
        db = firebase.database()
        db.child("Pedidos").child(id_pedido).remove()
    def crearPedido(self,pedido, firebase, id_restaurante, user_id, direccion):
        db = firebase.database()
        now = time.strftime("%d/%m/%y")
        hora = time.strftime("%I:%M:%S")
        total = list(pedido)[0]
        coordenadas = Usuario.getCoordDireccion(user_id, firebase)
        coordenadas = [coordenadas.latitude, coordenadas.longitude]
        data = {"Cliente": user_id, "Estado": "Pendiente", "Fecha":now, "Hora": hora,"Pedido":pedido, "Restaurante": id_restaurante, "Coordenadas": coordenadas, "Direccion": direccion}
        db.child("Pedidos").push(data)
    def getPedidosRestaurante(self,user_id, firebase):
        db = firebase.database()
        usuario = db.child("Usuarios").order_by_key().equal_to(user_id).get().val()
        correoRestaurante = list(usuario.values())[0]['correo']
        restaurante = db.child("Restaurantes").order_by_child("correo").equal_to(correoRestaurante).get().val()
        id_restaurante = list(restaurante.keys())[0]
        pedidos = db.child("Pedidos").order_by_child("Restaurante").equal_to(id_restaurante).get().val()
        return pedidos;
    def actualizarEstadoPedido(self,id_pedido, firebase):
        db = firebase.database()
        pedido = db.child("Pedidos").child(id_pedido).update({"Estado" : "Terminado"})
    def anadirPedidocesta(self,pedido, firebase):
        db = firebase.database()
        db.child("Cesta").push(pedido)
    def getPedidosCesta(self, firebase):
        db = firebase.database()
        pedidosCesta = db.child("Cesta").get().val()
        if (pedidosCesta is not None) :
            pedidoCesta = {}
            cont=2
            total=0.0
            for pedido in pedidosCesta:
                if pedidoCesta.get(pedidosCesta[pedido]['pedido']['Nombre']) is not None:  
                    total = total + float(pedidosCesta[pedido]['pedido']['Precio'])   
                    pedidoCesta[pedidosCesta[pedido]['pedido']['Nombre']]= pedidosCesta[pedido]['pedido']['Precio'] + ' x ' + str(cont)
                    cont=cont+1
                else:
                    pedidoCesta[pedidosCesta[pedido]['pedido']['Nombre']] = pedidosCesta[pedido]['pedido']['Precio']
                    total = total +float(pedidosCesta[pedido]['pedido']['Precio'])
                    pedidoCesta['Restaurante'] = pedidosCesta[pedido]['pedido']['Restaurante']
            pedidoCesta['Total'] = total
            return pedidoCesta
        else:
            return None
    def borrarCesta(self, firebase):
        db = firebase.database()
        db.child("Cesta").remove()
    def getTotal(pedido):
        total=0.0
        for key in pedido:
            if key != 'Restaurante' and key != 'id': 
                total = total + float(pedido[key])
        return total
      
class Restaurante():
    def crearRestaurante(data,firebase):
        db = firebase.database()
        db.child("Restaurantes").push(data)
    def getRestaurantes(firebase):
        db = firebase.database()
        restaurantes = db.child("Restaurantes").get().val()
        return restaurantes
    def getRestaurantesBusqueda(texto, firebase):
        db = firebase.database()
        todosRestaurantes = db.child("Restaurantes").get().val()
        busquedaRestaurantes = []
        for key, value in datos.items():
            if value['Nombre'] in texto:
                busquedaRestaurantes.append([value['Nombre'], value['Descripcion']])
            elif value['Descripcion'] in texto:
                busquedaRestaurantes.append([value['Nombre'], value['Descripcion']])
        return busquedaRestaurantes
    def getMenusRestaurante(id_restaurante, firebase):
        db = firebase.database()
        menus = db.child("Menus").order_by_child("Restaurante").equal_to(id_restaurante).get().val()
        return menus
    def getRestauranteByCorreo(self,correo, firebase):
        db = firebase.database()
        res = db.child("Restaurantes").order_by_child("correo").equal_to(correo).get().val()
        return res    
    def getRestaurantesCercanosMapa(user_id, firebase):
        db = firebase.database()
        usuario = db.child("Usuarios").order_by_key().equal_to(user_id).get().val()
        usuarioLista = list(usuario.values())
        direccion = usuarioLista[0]['direccion']
        geolocator = Nominatim(user_agent="building-an-app-1")
        location = geolocator.geocode(direccion)
        
        api_key = 'AIzaSyD-xb4MI_tuLrsw8jQaivU5_QcgiYJLWGg'
        
        google_places = GooglePlaces(api_key)
        query_result = google_places.nearby_search(
                lat_lng={'lat': location.latitude, 'lng': location.longitude}, keyword='Restaurante',
                radius=200, types=[types.TYPE_RESTAURANT])
        
        return query_result.places
    def getKeyRestaurante(firebase, nombre):
        db = firebase.database()
        restaurante = db.child("Restaurantes").order_by_child("Nombre").equal_to(nombre).get().val()
        if (len(restaurante)>0):
            restauranteKey = list(restaurante.keys())[0]
            return restauranteKey
        else:
            return None
