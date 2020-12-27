import pyrebase
import firebase
import time

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
    def deleteUsuario(self,id_usuario,firebase):
        db = firebase.database()
        db.child("Usuarios").child(id_usuario).remove()
    def getUsuario(self,id_usuario, firebase):
        db = firebase.database()
        usuario = db.child("Usuarios").order_by_key().equal_to(id_usuario).get().val()
        return usuario
    

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
        #cliente = db.child("Pedidos").order_by_child("Cliente").equal_to(user_id)
        pedidos = db.child("Pedidos").order_by_child("Estado").equal_to(estado).get().val()
        return pedidos
    def deletePedido(self,id_pedido,firebase):
        db = firebase.database()
        db.child("Pedidos").child(id_pedido).remove()
    def crearPedido(self,pedido, firebase, id_restaurante, user_id):
        db = firebase.database()
        now = time.strftime("%d/%m/%y")
        hora = time.strftime("%I:%M:%S")
        data = {"Cliente": user_id, "Estado": "Pendiente", "Fecha":now, "Hora": hora,"Pedido":pedido['pedido'], "Restaurante": id_restaurante}
        db.child("Pedidos").push(data)
        
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