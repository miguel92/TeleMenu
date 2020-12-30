from flask import Flask, render_template, request, redirect, url_for, session
from models import ConnectFirebase, Usuario, Menu, Pedido, Restaurante
import firebase


class Login():
    def get(request):
        url = ['sign_up.html', None]
        firebase = ConnectFirebase().firebase

        if request.method == 'POST':
            correo = request.form['correo']
            password = request.form['pass']
            next = request.args.get('next', None)

            if next:
                url[0] = 'next'

            auth = firebase.auth()
            # Log the user in
            try:
                user = auth.sign_in_with_email_and_password(correo, password)
                user = auth.refresh(user['refreshToken'])
                user_id = user['idToken']

                db = firebase.database()
                user_by_id = db.child("Usuarios").order_by_child("correo").equal_to(correo).get().val()
                clave = list(user_by_id)[0]

                session['user'] = clave
                session['rol'] = user_by_id[clave]['rol']

                if session['rol'] == "restaurante":
                    res = Restaurante().getRestauranteByCorreo(correo, firebase)
                    res = list(res)[0]
                    session['id_restaurante'] = res
                else:
                    session['id_restaurante'] = None

                url[0] = 'wb.html'
            except:
                message = "Correo o password invalidos"
                url[1] = message;
        return url

    def checkUser(self, perfil):
        firebase = ConnectFirebase().firebase
        db = firebase.database()
        correo = perfil['profile']['du']
        user_by_id = db.child("Usuarios").order_by_child("correo").equal_to(correo).get().val()

        if user_by_id == []:
            print("usuario no existe")
            existe = False
        return existe

    ## CRUD de USUARIOS


## C de usuarios desde registro


class Registro():
    def get(request):
        url = ['register.html', None]
        firebase = ConnectFirebase().firebase

        if request.method == 'POST':
            nombre = request.form['nombre']
            correo = request.form['correo']
            id = request.form['id']
            direccion = request.form['direccion']
            telefono = request.form['telefono']

            next = request.args.get('next', None)

            tipoUsuario = request.form['tipoUsuario']

            if next:
                url[0] = 'next'

            # Log the user in
            try:
                data = {"Nombre": nombre, "user_id": id, "correo": correo, "direccion": direccion, "telefono": telefono,
                        "rol": "cliente"}

                if tipoUsuario == 'restaurante':
                    data['rol'] = "restaurante"
                    descripcion = request.form['descripcion']
                    nombreRes = request.form['nombreRestaurante']

                    # AQUI VA LA PARTE DEL LOGO -> HAMZA

                    data2 = {"Nombre": nombreRes, "correo": correo, "descripcion": descripcion,
                             "logo": "urlPlaceholder", "direccion": direccion, "telefono": telefono}
                    Restaurante.crearRestaurante(data2, firebase)

                Usuario.crearUsuario(data, firebase)
                url[0] = 'wb.html'

            except:
                message = "Se ha producido un error"
                url[1] = message

        return url


## RUD de usuarios

class AdminUsuarios():
    @staticmethod
    def getListaUsuarios():
        firebase = ConnectFirebase().firebase
        return Usuario().listarUsuarios(firebase)

    def getUsuario(id_usuario):
        firebase = ConnectFirebase().firebase
        return Usuario().getUsuario(id_usuario, firebase)

    def update(request, id_usuario):
        firebase = ConnectFirebase().firebase
        url = ['admin/editarUsuario.html', "defecto"]

        if request.method == 'POST':
            Nombre = request.form['nombre']
            direccion = request.form['direccion']
            telefono = request.form['telefono']

            data = {"Nombre": Nombre, "direccion": direccion, "telefono": telefono}
            datos = Usuario().updateUsuario(id_usuario, data, firebase)
            return datos

    def delete(id_usuario):
        firebase = ConnectFirebase().firebase
        Usuario().deleteUsuario(id_usuario, firebase)


class AdminRestaurantes():
    @staticmethod
    def getLista():
        firebase = ConnectFirebase().firebase
        return Restaurante.getRestaurantes(firebase)

    @staticmethod
    def get(id_restaurante):
        firebase = ConnectFirebase().firebase
        return Restaurante.get_restaurante(id_restaurante, firebase)

    def update(request, id_restaurante):
        firebase = ConnectFirebase().firebase
        url = ['admin/editarRestaurante.html', "defecto"]

        if request.method == 'POST':
            Nombre = request.form['nombre']
            correo = request.form['correo']
            descripcion = request.form['descripcion']
            direccion = request.form['direccion']
            # logo = request.form['logo']
            telefono = request.form['telefono']

            # data = {"Nombre": Nombre, "correo": correo, descripcion: "descripcion",
            #        "direccion": direccion, "logo": logo, "telefono": telefono}
            data = {"Nombre": Nombre, "correo": correo, descripcion: "descripcion",
                    "direccion": direccion, "telefono": telefono}
            datos = Restaurante.update_restaurante(id_restaurante, data, firebase)
            return datos

    def delete(id_usuario):
        firebase = ConnectFirebase().firebase
        Usuario().deleteUsuario(id_usuario, firebase)


class AdminMenus():
    @staticmethod
    def getLista():
        firebase = ConnectFirebase().firebase
        return Menu().listarMenus(firebase)

    def get(id_menu):
        firebase = ConnectFirebase().firebase
        return Menu().getMenu(id_menu, firebase)

    def update(request, id_menu):
        firebase = ConnectFirebase().firebase
        url = ['admin/editarMenu.html', "defecto"]

        if request.method == 'POST':
            nombre = request.form['nombrePlato']
            precio = request.form['precio']
            ingredientes = request.form['ingredientes']
            tipoPlato = request.form['tipoPlato']

            # FOTO DEL PLATO PARTE DE HAMZA

            if session['id_restaurante']:
                id_res = session['id_restaurante']
            else:
                id_res = request.form['idRestaurante']

            if request.form['fotoPlato'] is None:
                urlFoto = "img/menu_placeholder2.jpg"
            else:
                urlFoto = request.form['fotoPlato']

            data = {"Nombre": nombre, "Ingredientes": ingredientes, "Tipo": tipoPlato, "Precio": precio,
                    "Foto": urlFoto, "Restaurante": id_res}
            datos = Menu().updateMenu(id_menu, data, firebase)
            return datos

    def delete(id_menu):
        firebase = ConnectFirebase().firebase
        Menu().deleteMenu(id_menu, firebase)

    def create(self, request):
        firebase = ConnectFirebase().firebase
        url = ['admin/crearMenu.html', None]

        if request.method == 'POST':
            nombre = request.form['nombrePlato']
            precio = request.form['precio']
            ingredientes = request.form['ingredientes']
            tipoPlato = request.form['tipoPlato']

            # FOTO DEL PLATO PARTE DE HAMZA

            if session['id_restaurante']:
                id_res = session['id_restaurante']
            else:
                id_res = request.form['idRestaurante']

            if request.form['fotoPlato'] == "":
                urlFoto = "img/menu_placeholder2.jpg"
            else:
                urlFoto = request.form['fotoPlato']

            data = {"Nombre": nombre, "Ingredientes": ingredientes, "Tipo": tipoPlato, "Precio": precio,
                    "Foto": urlFoto, "Restaurante": id_res}

            try:
                Menu().createMenu(data, firebase)
                if session['rol'] == 'restaurante':
                    url[0] = 'listarMenusRestaurante.html'
                else:
                    url[0] = 'listarMenu.html'

            except:
                message = "No se ha podido crear"
                url[1] = message
        return url


class misPedidos():
    @staticmethod
    def getMisPedidos(user_id, estado):
        firebase = ConnectFirebase().firebase
        pedido = Pedido.getPedidos(user_id, firebase, estado)
        return pedido

    @staticmethod
    def getPedidosRestaurante(id_restaurante, estado):
        firebase = ConnectFirebase().firebase
        pedido = Pedido.getPedidosRestaurante(id_restaurante, firebase, estado)
        return pedido

    @staticmethod
    def deletePedido(id_pedido):
        firebase = ConnectFirebase().firebase
        Pedido().deletePedido(id_pedido, firebase)

    def crearPedido(pedido, id_restaurante):
        user_id = session['user']
        firebase = ConnectFirebase().firebase
        Pedido().crearPedido(pedido, firebase, id_restaurante, user_id)


class listarRestaurantes():
    @staticmethod
    def get_restaurante(id_restaurante):
        firebase = ConnectFirebase().firebase
        restaurante = Restaurante.get_restaurante(id_restaurante, firebase)
        return restaurante

    @staticmethod
    def delete_restaurante(id_restaurante):
        firebase = ConnectFirebase().firebase
        Restaurante.delete_restaurante(id_restaurante, firebase)

    @staticmethod
    def update_restaurante(id_restaurante):
        firebase = ConnectFirebase().firebase
        Restaurante.update_restaurante(id_restaurante, firebase)

    @staticmethod
    def getListaRestaurantes():
        firebase = ConnectFirebase().firebase
        restaurantes = Restaurante.getRestaurantes(firebase)
        return restaurantes

    def getListaRestaurantesBusqueda(request):
        firebase = ConnectFirebase().firebase
        texto = request.form['inputSearch']
        return Restaurante.getRestaurantesBusqueda(texto, firebase)

    @staticmethod
    def getListaMenusRestaurante(id_restaurante):
        firebase = ConnectFirebase().firebase
        menus = Restaurante.getMenusRestaurante(id_restaurante, firebase)
        return menus

    @staticmethod
    def getRestaurantesCercanosMapa():
        user_id = session['user']
        firebase = ConnectFirebase().firebase
        return Restaurante.getRestaurantesCercanosMapa(user_id, firebase)

    @staticmethod
    def getKeyRestaurante(nombre):
        firebase = ConnectFirebase().firebase
        return Restaurante.getKeyRestaurante(firebase, nombre)

    @staticmethod
    def get_restaurante_by_correo(correo):
        firebase = ConnectFirebase().firebase
        return Restaurante.getRestauranteByCorreo(correo, firebase)

    @staticmethod
    def get_weather_pollution_for_restaurante(restaurante):
        return Restaurante.get_weather_pollution_for_restaurante(restaurante)


class usuario():
    @staticmethod
    def get_usuario(id_user):
        firebase = ConnectFirebase().firebase
        return Usuario.consultarUsuario(id_user, firebase)

    def getCoordDireccion(self):
        user_id = session['user']
        firebase = ConnectFirebase().firebase
        return Usuario.getCoordDireccion(user_id, firebase)
