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
        try:
            if self.path.endswith("/restaurants/newRestaurant"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h3>Add new Restaurant Name</h3>"
                output += '''<form method='Post' enctype='multipart/form-data' action='restaurants/newRestaurant'><input name='newRestaurantName' type='text' placeholder='Restaurant Name'> <input type='submit' value='Create'></form>'''
                output += "<br>"
                output += "<p>Back to the <a href = '/restaurants'> Restaurant list</a></p>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

            if self.path.endswith("/edit"):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(
                    id=restaurantIDPath).one()
                if myRestaurantQuery != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = "<html><body>"
                    output += "<h1>"
                    output += myRestaurantQuery.name
                    output += "</h1>"
                    output += '''<form method='Post' enctype='multipart/form-data' action='/restaurants/%s/edit'>''' % restaurantIDPath
                    output += '''<input name='newRestaurantName' type='text'placeholder='%s'>''' % myRestaurantQuery.name
                    output += ''' <input type='submit' value='Rename'></form>'''
                    output += "<br>"
                    output += "<p>Back to the <a href = '/restaurants'> Restaurant list</a></p>"
                    output += "</body></html>"
                    self.wfile.write(output)
                    print output

            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(
                    id=restaurantIDPath).one()
                if myRestaurantQuery != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = "<html><body>"
                    output += "<h1>"
                    output += "Are you sure you want to delete %s ?" % myRestaurantQuery.name
                    output += "</h1>"
                    output += '''<form method='Post' enctype='multipart/form-data' action='/restaurants/%s/delete'>''' % restaurantIDPath
                    output += ''' <input type='submit' value='Delete'></form>'''
                    output += "<br>"
                    output += "<p>Back to the <a href = '/restaurants'> Restaurant list</a></p>"
                    output += "</body></html>"
                    self.wfile.write(output)
                    print output


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
                    output += '''<p><a value='restaurant.name' href=' /restaurants/%s/edit'>Edit</a></p>''' % restaurant.id
                    output += '''<p><a href="/restaurants/%s/delete">Delete</a></p>''' % restaurant.id
                    output += "<div style='height:25px;width:100%;'></div>"
                    output += "\n"
                output += "<h3>Add a new Restaurant <a href='restaurants/newRestaurant'> Here</a></h3>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return


        except IOError:
            self.send_error(404, "File Not Found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
                    restaurantIDPath = self.path.split("/")[2]

                    myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                    if myRestaurantQuery != []:
                        myRestaurantQuery.name = messagecontent[0]
                        session.add(myRestaurantQuery)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Contect-type', 'text/hmtl')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()

            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                if myRestaurantQuery != []:
                    session.delete(myRestaurantQuery)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Contect-type', 'text/hmtl')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()


            if self.path.endswith("/restaurants/newRestaurant"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields=cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')

                newRestaurant = Restaurant(name = messagecontent[0])
                session.add(newRestaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type','text/html; charset=utf-8')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h2> New Restaurant was added!</h2>"
                output += "<h1> %s </h1>" % messagecontent[0]
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
