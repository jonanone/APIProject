from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import cgi
from database_helper import db_init, get_restaurants, add_restaurant
from database_helper import get_restaurant, edit_restaurant, delete_restaurant

session = db_init()


class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Hello World
            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "Hello!"
                output += "<form method='POST' enctype='multipart/form-data' \
                       action='/hello'><h2>What would you like me to say?</h2>\
                       <input name='message' type='text'><input type='submit' \
                       value='Submit'></form>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            # Hola Mundo
            if self.path.endswith("/hola"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "&#16Hola! <a href='/hello'>\
                           Back to Hello</a>"
                output += "<form method='POST' enctype='multipart/form-data' \
                       action='/hello'><h2>What would you like me to say?</h2>\
                       <input name='message' type='text'><input type='submit' \
                       value='Submit'></form>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            # List restaurants
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurants = get_restaurants(session)

                output = ""
                output += "<html><body>"
                output += "<h1>Restaurants</h1>"
                output += "<a href='restaurants/new'>Add new restaurant</a>"
                output += "<ul>"
                for restaurant in restaurants:
                    output += "<li>"
                    output += "<p>" + restaurant.name + "</p>"
                    output += "<div><a href='restaurant/" + str(restaurant.id) + "/edit'>Edit</a></div>"
                    output += "<div><a href='restaurant/" + str(restaurant.id) + "/delete'>Delete</a></div>"
                    output += "</li>"
                output += "</ul>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            # Add new restaurant
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h1>Make a new restaurant</h1>"
                output += "<form method='POST' enctype='multipart/form-data' \
                       action='/restaurants/new'><input name='name' \
                       type='text'><input type='submit' value='Create'></form>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            # Edit a given restaurant
            if self.path.endswith("/edit"):
                restaurant_id = self.path.split('/')[2]
                restaurant = get_restaurant(session, restaurant_id)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h1>Edit a restaurant</h1>"
                output += "<h2> %s </h2>" % restaurant.name
                output += "<form method='POST' enctype='multipart/form-data' \
                       action='/restaurants/" + restaurant_id + "/edit'><input name='name' \
                       type='text'><input type='submit' value='Save'></form>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            # Delete a given restaurant
            if self.path.endswith("/delete"):
                restaurant_id = self.path.split('/')[2]
                restaurant = get_restaurant(session, restaurant_id)
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = ""
                output += "<html><body>"
                output += "<h1>Are you sure you want to delete %s  restaurant?</h1>" % restaurant.name
                output += "<form method='POST' enctype='multipart/form-data' \
                       action='/restaurants/" + restaurant_id + "/delete'> \
                       <input type='submit' value='Delete'></form> \
                       <a href='/restaurants'>No, go back to restaurants</a>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            # Say hello
            if self.path.endswith("/hello"):
                self.send_response(301)
                self.end_headers()

                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message')

                output = ""
                output += "<html><body>"
                output += "<h2> Okay, how about this: </h2>"
                output += "<h1> %s </h1>" % messagecontent[0]

                output += "<form method='POST' enctype='multipart/form-data' \
                           action='/hello'><h2>What would you like me to say?</h2>\
                           <input name='message' type='text'><input type='submit' \
                           value='Submit'></form>"
                output += "</body></html>"
                self.wfile.write(output)
                print output

            # Add new restaurant POST
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    data = {}
                    for field in fields:
                        data[field] = fields.get(field)[0]
                    new_restaurant = add_restaurant(session, data)
                    print new_restaurant.name + ' added.'
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
                print output

            # Edit a given restaurant POST
            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    data = {}
                    for field in fields:
                        data[field] = fields.get(field)[0]
                    restaurant_id = self.path.split('/')[2]
                    edited_restaurant = edit_restaurant(session, restaurant_id, data)
                    print edited_restaurant.name + ' edited.'
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
                print output

            # Delete a given restaurant POST
            if self.path.endswith("/delete"):
                restaurant_id = self.path.split('/')[2]
                restaurant_deleted = delete_restaurant(session, restaurant_id)
                if restaurant_deleted:
                    print 'Restaurant deleted.'
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
                print output

        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webserverHandler)
        print "Web server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()


if __name__ == '__main__':
    main()
