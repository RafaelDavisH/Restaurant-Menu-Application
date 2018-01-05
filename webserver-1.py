#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
import cgi

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind=create_engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.endswith("/restaurants"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            restaurantList = session.query(Restaurant).all()
            output = ""
            output += "<html><body>"
            output += "<h1>Restaurant List</h1>"
            for restaurant in restaurantList:
                output += "<h3> %s </h3>" % restaurant.name
                output += '''<p><a href="%s/edit">Edit</a></p>''' % restaurant.id
                output += '''<p><a href="%s/delete">Delete</a></p>''' % restaurant.id
                output += "<div style='height:25px;width:100%;'></div>"
                output += "\n"
            output += "<h3>Add a new Restaurant <a href='/newRestaurant'> Here</a></h3>"
            output += "</body></html>"
            self.wfile.write(output)
            print output
            return

        if self.path.endswith("/newRestaurant"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            output = ""
            output += "<html><body>"
            output += "<h3>Add new Restaurant Name</h3>"
            output += '''<form method='Post' enctype='multipart/form-data' action='/newRestaurant'><input name='restaurant' type='text'><input type='submit' placeholder='Restaurant Name'value='Create'></form>'''
            output += "<br>"
            output += "<p>Back to the <a href = '/restaurants'> Restaurant list</a></p>"
            output += "</body></html>"
            self.wfile.write(output)
            print output
            return

        else:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            self.send_response(301)
            self.send_header('Contect-type', 'text/hmtl')
            self.end_headers()

            ctype, pdict = cgi.parse_header(self.headers.getheader('Content-type'))
            if ctype == 'multipart/form-data':
                fields=cgi.parse_multipart(self.rfile, pdict)

                messagecontent = fields.get('restaurant')
                addRestaurant = Restaurant(name = messagecontent[0])
                session.add(addRestaurant)
                session.commit()
                output = ""
                output += "<html><body>"
                output += "<h2> A new Restaurant was added!</h2>"
                output += "<h1> %s </h1>" % messagecontent[0]
                output += '''<form method='Post' enctype='multipart/form-data' action='/newRestaurant'><input name='restaurant' type='text'><input type='submit' placeholder ='restaurant name' value='Create'></form>'''
                output += "<br>"
                output += "<p>Back to the <a href = '/restaurants'> Restaurant list</a></p>"
                output += "</body></html>"
                self.wfile.write(output)
                print output

        except:
            pass

def main():
    try:
        port = 8000
        server = HTTPServer(('', port), WebServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()

    except KeyboardInterrupt:
        print " ^C entered, stopping web server..."
        server.socket.close()

if __name__ == '__main__':
    main()
