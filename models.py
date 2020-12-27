import pyrebase

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