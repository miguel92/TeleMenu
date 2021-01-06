import flickr_api

client_username = 'jose.moreno.martin.jimenez.2015@gmail.com'
flickr_api.set_keys(api_key = 'ad53b2717df3f7c91bddf3e9a38ecc29', api_secret = '89adc58e69713600')

class Flickr():
    def autenticacionFlickr(self):
        flickr_api.set_auth_handler("flickr_credentials.dat")
        user = flickr_api.test.login()
        return user;
    
    def crearFicheroCredenciales(self):
        a = flickr_api.auth.AuthHandler() # creates a new AuthHandler object
        perms = "write" # set the required permissions
        url = a.get_authorization_url(perms)
        
        print(url)
        verifier = input("Verifier code: ")
        
        a.set_verifier(verifier)
        a.save("flickr_credentials.dat")


