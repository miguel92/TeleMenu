from flask import Flask, render_template, request, redirect, url_for, session
from models import ConnectFirebase, Usuario, Menu, Pedido, Restaurante, ComentarioModelo
import firebase,os
from auth_img import Flickr
import flickr_api, requests,json
from pyasn1_modules.rfc2459 import id_pe

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
                    session['direccion'] = user_by_id[clave]['direccion']

                    if session['rol'] == "restaurante":
                        res = Restaurante().getRestauranteByCorreo(correo,firebase)
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

                    if request.files['logoRestaurante'].filename == '':
                        urlFoto = "img/res_placeholder.jpg"
                    else:
                        urlFoto = Imagen().subirImagen(request,'logoRestaurante',request.form['entorno'])
                
                    data2 = {"Nombre": nombreRes, "correo": correo, "descripcion": descripcion,
                             "logo": urlFoto, "direccion": direccion, "telefono": telefono}
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
            telefono = request.form['telefono']

            if request.files['logoRestaurante'].filename == '':
                urlFoto = "img/res_placeholder.jpg"
            else:
                urlFoto = Imagen().subirImagen(request,'logoRestaurante',request.form['entorno'])
                
            data = {"Nombre": Nombre, "correo": correo, "descripcion": descripcion,
                    "direccion": direccion, "telefono": telefono, "logo": urlFoto}
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

            if session.get('id_restaurante'):
                id_res = session['id_restaurante']
            else:
                id_res = request.form['idRestauranteValue']
  
            if request.files['fotoPlato'].filename != '':
                urlFoto = Imagen().subirImagen(request,'fotoPlato',request.form['entorno'])
            else:
                urlFoto = request.form["fotoActual"]

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

            if session.get('id_restaurante'):
                id_res = session['id_restaurante']
            else:
                id_res = request.form['idRestaurante']

            if request.files['fotoPlato'].filename == '':
                urlFoto = "img/menu_placeholder2.jpg"
            else:
                urlFoto = Imagen().subirImagen(request, 'fotoPlato', request.form['entorno'])

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
    def getMisPedidos(estado):
        user_id = session['user']
        firebase = ConnectFirebase().firebase
        pedido = Pedido.getPedidos(user_id, firebase, estado)
        return pedido
    '''
    @staticmethod
    def getPedidosRestaurante(id_restaurante):
        firebase = ConnectFirebase().firebase
        pedido = Pedido.getPedidosRestaurante(id_restaurante, firebase)
        return pedido
    '''
    @staticmethod
    def deletePedido(id_pedido):
        firebase = ConnectFirebase().firebase
        Pedido().deletePedido(id_pedido, firebase)

    def crearPedido(pedido, id_restaurante):
        user_id = session['user']
        direccion = session['direccion']
        firebase = ConnectFirebase().firebase
        Pedido().crearPedido(pedido, firebase, id_restaurante, user_id, direccion)
    def getPedidosRestaurante():
        id_restaurante = session['user']
        firebase = ConnectFirebase().firebase
        return Pedido().getPedidosRestaurante(id_restaurante, firebase)
    def actualizarEstadoPedido(id_pedido):
        firebase = ConnectFirebase().firebase
        Pedido().actualizarEstadoPedido(id_pedido, firebase)
    def anadirPedidocesta(pedido):
        firebase = ConnectFirebase().firebase
        Pedido().anadirPedidocesta(pedido, firebase)
    def getPedidosCesta():
        firebase = ConnectFirebase().firebase
        return Pedido().getPedidosCesta(firebase)
    def borrarCesta():
        firebase = ConnectFirebase().firebase
        Pedido().borrarCesta(firebase)
        

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

    def getCoordDireccion():
        user_id = session['user']
        firebase = ConnectFirebase().firebase
        return Usuario().getCoordDireccion(user_id, firebase)
class Imagen():
    def subirImagen(self,request,campo,entorno):
            f = request.files[campo];
            cliente = Flickr().autenticacionFlickr()
            if entorno =='localhost':
                f.save('tmp_img/' +f.filename)
                foto = flickr_api.upload(photo_file='tmp_img/' + f.filename, title=f.filename)
                os.remove('tmp_img/' + f.filename)
            else:
                f.save('/tmp/' +f.filename)
                foto = flickr_api.upload(photo_file='/tmp/' + f.filename, title=f.filename)
                os.remove('/tmp/' + f.filename)
            url = self.getImagen(foto.id)
            return url
    def getImagen(self,id_foto):
            api_key = 'ad53b2717df3f7c91bddf3e9a38ecc29'
            user_id = "191734611@N08"
             
            url = self.get_requestURL_people(user_id,api_key,endpoint="getPhotos")
            strlist = requests.get(url).content
            json_data = json.loads(strlist)
            
            url = None
            encontrado = False;
            contador = 0;
            
            while (contador < len(json_data["photos"]["photo"])) and (encontrado == False):
                pic = json_data["photos"]["photo"][contador]
                print(pic['id'])
                if pic["id"] == id_foto :
                    url = self.get_photo_url(pic["farm"],pic['server'], pic["id"], pic["secret"])
                    encontrado = True
                contador = contador +1
               
            return url 
    def get_photo_url(self,farmId,serverId,Id,secret):
        return (("https://farm" + str(farmId) + 
                ".staticflickr.com/" + serverId + 
                "/" + Id + '_' + secret + ".jpg"))
    def get_requestURL_people(self,user_id,api_key,endpoint="getPhotos"):
        user_id = user_id.replace("@","%40")
        url_upto_apikey = ("https://api.flickr.com/services/rest/?method=flickr.people." + 
                           endpoint + 
                           "&api_key=" +  api_key +  
                           "&user_id=" +  user_id +
                           "&format=json&nojsoncallback=1")
        return(url_upto_apikey)        

class Comentario():
    def crearComentario(self, request, id_restaurante):
        firebase = ConnectFirebase().firebase
        url = ['crearMenu.html', None]

        if request.method == 'POST':
            comentario = request.form['text']
            clasificacion = request.form['contadorEstrellas']

            nombre = session['nombre']
            correo = session['user']

            if request.files['fotoComentario'].filename == '':
                urlFoto = "img/menu_placeholder2.jpg"
            else:
                urlFoto = Imagen().subirImagen(request, 'fotoComentario', request.form['entorno'])

            data = {"Clasificacion": clasificacion,"Foto": urlFoto, "Restaurante": id_restaurante, "Texto": comentario, "Usuario": nombre, "Correo": correo}
            
            try:            
                ComentarioModelo().crearComentario(data, firebase)
                url[0] = 'comentarioRealizado.html'
            except:
                message = "No se ha podido crear"
                url[1] = message
        return url
    def getValoracionMedia(id_restaurante):
        firebase = ConnectFirebase().firebase
        return ComentarioModelo().getValoracionMedia(id_restaurante, firebase)
    def getComentarios(self, id_restaurante):
        firebase = ConnectFirebase().firebase
        return ComentarioModelo().getComentarios(id_restaurante, firebase)
    
class AdminValoraciones():
    @staticmethod
    def getListaValoraciones():
        firebase = ConnectFirebase().firebase
        return ComentarioModelo().getAllComentarios(firebase)

    def get(id_valoracion):
        firebase = ConnectFirebase().firebase
        return ComentarioModelo().getValoracion(id_valoracion, firebase)

    def update(request, id_valoracion):
        firebase = ConnectFirebase().firebase
        url = ['admin/editarValoracion.html', "defecto"]
        update = None
        if request.method == 'POST':
            comentario = request.form['text']
            clasificacion = request.form['contadorEstrellas']
            nombre = request.form['nombreUsuario']
            user_id = session['id']
            correo = session['user']

            if request.files['fotoComentario'].filename != '':
                urlFoto = Imagen().subirImagen(request,'fotoComentario',request.form['entorno'])
            else:
                urlFoto = request.form["fotoActual"]

            data = {"Clasificacion": clasificacion,"Foto": urlFoto, "Texto": comentario, "Usuario": nombre, "Correo": correo}
            
            try:            
                update = ComentarioModelo().updateComentario(id_valoracion, data, firebase)
                 
            except:
                message = "No se ha podido crear"
                
        return update

    def delete(id_valoracion):
        firebase = ConnectFirebase().firebase
        ComentarioModelo().deleteValoracion(id_valoracion, firebase)
