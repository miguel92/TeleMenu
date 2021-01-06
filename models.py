import json
import time

import pyrebase
import requests
from flask_login import UserMixin
from geopy.geocoders import Nominatim
from googleplaces import GooglePlaces, types


class ConnectFirebase:
    config = {
        "apiKey": "AIzaSyAmaKAg407v6ga8aX6snP0J4NoyEXVtxAY",
        "authDomain": "telemenu-firebase.firebaseapp.com",
        "databaseURL": "https://telemenu-firebase-default-rtdb.europe-west1.firebasedatabase.app",
        "storageBucket": "telemenu-firebase.appspot.com"
    }
    firebase = None

    def __init__(self):
        self.firebase = pyrebase.initialize_app(self.config)


class Usuario(UserMixin):
    def __init__(self, id_=None, name=None, email=None, rol=None):
        self.id = id_
        self.name = name
        self.email = email
        self.rol = rol

    def crearUsuario(data, firebase):
        db = firebase.database()
        db.child("Usuarios").push(data)

    @staticmethod
    def consultarUsuario(user_id, firebase):
        db = firebase.database()
        user_by_id = db.child("Usuarios").order_by_child("user_id").equal_to(user_id).get().val()
        return user_by_id

    def listarUsuarios(self, firebase):
        db = firebase.database()
        usuarios = db.child("Usuarios").get().val()
        return usuarios

    def updateUsuario(self, id_usuario, data, firebase):
        db = firebase.database()
        return db.child("Usuarios").child(id_usuario).update(data)

    @staticmethod
    def deleteUsuario(id_usuario, firebase):
        db = firebase.database()
        user = db.child("Usuarios").child(id_usuario)
        user.remove()

    def getUsuario(self, id_usuario, firebase):
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

    @staticmethod
    def get(user_id):
        firebase = ConnectFirebase().firebase
        db = firebase.database()
        user = db.child("Usuarios").order_by_child("user_id").equal_to(user_id).get().val()

        if not user:
            return None
        clave = list(user)[0]
        user = Usuario(
            id_=user[clave]['user_id'], name=user[clave]['Nombre'], email=user[clave]['correo'], rol=user[clave]['rol']
        )
        return user


class Menu():
    def crearMenu(data, firebase):
        db = firebase.database()
        db.child("Menus").push(data)

    def listarMenus(self, firebase):
        db = firebase.database()
        menus = db.child("Menus").get().val()
        return menus

    def getMenu(self, id_menu, firebase):
        db = firebase.database()
        menu = db.child("Menus").order_by_key().equal_to(id_menu).get().val()
        return menu

    def updateMenu(self, id_menu, data, firebase):
        db = firebase.database()
        return db.child("Menus").child(id_menu).update(data)

    def deleteMenu(self, id_menu, firebase):
        db = firebase.database()
        db.child("Menus").child(id_menu).remove()

    def createMenu(self, data, firebase):
        db = firebase.database()
        db.child("Menus").push(data)


class Pedido():
    def getPedidos(user_id, firebase, estado):
        db = firebase.database()
        # cliente = db.child("Pedidos").order_by_child("Cliente").equal_to(user_id)
        pedidos = db.child("Pedidos").order_by_child("Estado").equal_to(estado).get().val()
        return pedidos

    @staticmethod
    def getPedidosRestaurante(id_restaurante, firebase, estado):
        db = firebase.database()
        # all_pedidos = db.child("Pedidos").order_by_child("Restaurante").equal_to(id_restaurante).get().val()
        all_pedidos = db.child("Pedidos").order_by_child("Restaurante").equal_to('-MP_HyYBcG1CYrUW8YS0').get().val()
        pedidos = {}
        for key, value in all_pedidos.items():
            if value['Estado'] == estado:
                pedidos[key] = value
        return pedidos

    def deletePedido(self, id_pedido, firebase):
        db = firebase.database()
        db.child("Pedidos").child(id_pedido).remove()

    def crearPedido(self, pedido, firebase, id_restaurante, user_id):
        db = firebase.database()
        now = time.strftime("%d/%m/%y")
        hora = time.strftime("%I:%M:%S")
        data = {"Cliente": user_id, "Estado": "Pendiente", "Fecha": now, "Hora": hora, "Pedido": pedido['pedido'],
                "Restaurante": id_restaurante}
        db.child("Pedidos").push(data)


class Restaurante():
    def crearRestaurante(data, firebase):
        db = firebase.database()
        db.child("Restaurantes").push(data)

    @staticmethod
    def delete_restaurante(id_restaurante, firebase):
        db = firebase.database()
        rest = db.child("Restaurantes").child(id_restaurante)
        email = rest.get().val()['correo']
        menus = Restaurante.getMenusRestaurante(id_restaurante, firebase)
        for menu in menus:
            Menu.deleteMenu(menu, firebase)
        user = db.child("Usuarios").order_by_child("correo").equal_to(email)
        if user.get().val():
            user.remove()
        db.child("Restaurantes").child(id_restaurante).remove()

    def getRestaurantes(firebase):
        db = firebase.database()
        restaurantes = db.child("Restaurantes").get().val()
        return restaurantes

    @staticmethod
    def update_restaurante(id_restaurante, data, firebase):
        db = firebase.database()
        return db.child("Restaurantes").child(id_restaurante).update(data)

    @staticmethod
    def getRestaurantesBusqueda(texto, firebase):
        db = firebase.database()
        todosRestaurantes = db.child("Restaurantes").get().val()
        busquedaRestaurantes = []
        for key, value in todosRestaurantes.items():
            if value['Nombre'] in texto:
                busquedaRestaurantes.append([value['Nombre'], value['Descripcion']])
            elif value['Descripcion'] in texto:
                busquedaRestaurantes.append([value['Nombre'], value['Descripcion']])
        return busquedaRestaurantes

    @staticmethod
    def get_restaurante(id_restaurante, firebase):
        db = firebase.database()
        restaurante = db.child("Restaurantes").child(id_restaurante).get().val()
        return restaurante

    @staticmethod
    def getMenusRestaurante(id_restaurante, firebase):
        db = firebase.database()
        menus = db.child('Menus').order_by_child('Restaurante').equal_to(id_restaurante).get().val()
        return menus

    @staticmethod
    def getRestauranteByCorreo(correo, firebase):
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
            radius=30, types=[types.TYPE_RESTAURANT])

        return query_result.places

    def getKeyRestaurante(firebase, nombre):
        db = firebase.database()
        restaurante = db.child("Restaurantes").order_by_child("Nombre").equal_to(nombre).get().val()
        restauranteKey = list(restaurante.keys())[0]
        return restauranteKey

    """
    Search the weather and level of pollution for a restaurant.
    :param nombre: Name of the restaurant.
    :param firebase: Database.
    :return: Dictionary with weather and pollution parameters.
    """

    @staticmethod
    def get_weather_pollution_for_restaurante(rest):
        # Initialize database and obtain location of restaurant
        if rest.get('direccion') is None:
            return None
        direccion = rest['direccion']
        geolocator = Nominatim(user_agent="building-an-app-1")
        location = geolocator.geocode(direccion)

        # API key for OpenWeatherMap API
        api_key = 'c53b5713196b91c9a3a5a93ee20a04f4'

        # URLs for weather and pollution
        base_url_weather = "http://api.openweathermap.org/data/2.5/weather?"
        base_url_pollution = "http://api.openweathermap.org/data/2.5/air_pollution?"
        # Attribute the URLs
        url_position = "lat={}&lon={}".format(location.latitude, location.longitude)
        url_api = "appid={}".format(api_key)
        url_language = "lang=es"

        # Obtaining the data for weather and pollution. Then converting them into Dictionaries
        weather_data = requests.get(base_url_weather + url_position + "&" + url_api + "&" + url_language +
                                    '&units=metric').json()
        pollution_data = requests.get(base_url_pollution + url_position + "&" + url_api).json()

        # Obtaining the important data from the data of weather_data and pollution_data
        dict_data = {'weather': {}, 'pollution': {}}
        dict_data['weather']['description'] = weather_data['weather'][0]['description']
        dict_data['weather']['temperature'] = weather_data['main']['temp']
        dict_data['weather']['humidity'] = weather_data['main']['humidity']
        dict_data['pollution']['air_quality'] = Restaurante.__obtain_pollution_air_quality(
            pollution_data['list'][0]['main']['aqi'])
        dict_data['pollution']['components'] = pollution_data['list'][0]['components']

        return dict_data

    """
    Private method to obtain the description for air quality.
    :param aqi: Integer value of air quality.
    :return: Description of the air quality
    """

    @staticmethod
    def __obtain_pollution_air_quality(aqi):
        descripcion = ['Buena', 'Razonable', 'Moderada', 'Mala', 'Muy mala']
        return descripcion[aqi - 1]
