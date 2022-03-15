import mysql.connector
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import re

with open("D:\SEM II\CC\Tema 2\private.json") as json_file:
    data = json.load(json_file)
    user = data["user"]
    password = data["password"]

cnx = mysql.connector.connect(user=user, password=password,
                              host='127.0.0.1',
                              database='employees')


def getEmployees():
    mycursor = cnx.cursor()
    mycursor.execute("SELECT * FROM employees")
    myresult = mycursor.fetchall()
    types = ["id", "birth-date", "first-name", "last-name", "sex", "hire-date"]
    list = []
    for employee in myresult:
        list.append(dict(zip(types, employee)))
    return json.dumps(list, indent=4, sort_keys=True, default=str)


def addEmployee(employee):
    mycursor = cnx.cursor()
    sql_command = "INSERT INTO employees(birth_date, first_name, last_name, gender, hire_date) VALUES(%s, %s, %s, %s, %s)"
    mycursor.execute(sql_command, employee)
    cnx.commit()


def updateEmployee(employee):
    mycursor = cnx.cursor()
    sql_command = "UPDATE employees SET birth_date = %s ,first_name = %s, last_name= %s, gender= %s, hire_date= %s WHERE id = %s "
    mycursor.execute(sql_command, employee)
    cnx.commit()


def updateSalary(salary):
    mycursor = cnx.cursor()
    sql_command = "UPDATE salaries SET value = %s ,date = %s WHERE employee_id = %s "
    mycursor.execute(sql_command, salary)
    cnx.commit()


def getEmployeeById2(id):
    mycursor = cnx.cursor()
    sql_command = "SELECT * FROM employees WHERE id=%s"
    mycursor.execute(sql_command, (id,))
    emp = mycursor.fetchall()
    print(emp)
    temp = list(emp[0])
    salaries = getSalaries(id)
    idk = ["salary_id", "value", "date"]
    list2 = []
    for salary in salaries:
        list2.append(dict(zip(idk, salary)))
    temp.append(list2)
    lista = []
    lista.append(tuple(temp))
    print(lista)
    return lista

def getEmployeeById(id):
    mycursor = cnx.cursor()
    sql_command = "SELECT * FROM employees WHERE id=%s"
    mycursor.execute(sql_command, (id,))
    emp = mycursor.fetchall()
    return emp


def deleteEmployee(id):
    mycursor = cnx.cursor()
    sql_command = "DELETE FROM employees WHERE id=%s"
    mycursor.execute(sql_command, (id,))
    cnx.commit()


def deleteSalary(id):
    mycursor = cnx.cursor()
    sql_command = "DELETE FROM salaries WHERE employee_id=%s"
    mycursor.execute(sql_command, (id,))
    cnx.commit()


def checkEmployee(employee):
    mycursor = cnx.cursor()
    sql_command = "SELECT id FROM employees WHERE birth_date=%s AND first_name=%s AND last_name=%s AND gender=%s AND hire_date=%s"
    mycursor.execute(sql_command, employee)
    emp = mycursor.fetchall()
    if emp == []:
        return True
    else:
        return False


def getSalaries(id):
    mycursor = cnx.cursor()
    sql = "SELECT salary_id, value, date FROM salaries WHERE employee_id=%s"
    mycursor.execute(sql, (id,))
    myresult = mycursor.fetchall()
    return myresult

def addSalary(salary):
    mycursor = cnx.cursor()
    sql_command = "INSERT INTO salaries(employee_id, value, date) VALUES(%s, %s, %s)"
    mycursor.execute(sql_command, salary)
    cnx.commit()


class ServiceHandler(BaseHTTPRequestHandler):

    def set_and_get_header(self, type):
        if (type == "post"):
            self.send_response(201)
        else:
            self.send_response(200)
        self.send_header('Content-type', 'text/json')
        length = int(self.headers['Content-Length'])
        content = self.rfile.read(length)
        data = json.loads(content)
        self.end_headers()
        self.wfile.write("OK".encode())
        return data

    def get_header(self):
        length = int(self.headers['Content-Length'])
        content = self.rfile.read(length)
        data = json.loads(content)
        return data

    # GET Method Defination
    def do_GET(self):
        # defining all the headers

        if (self.path == "/employees"):
            if getEmployees():
                self.send_response(200)
                self.send_header('Content-type', 'text/json')
                self.end_headers()
                self.wfile.write(getEmployees().encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/json')
                error = "NOT FOUND!"
                self.end_headers()
                self.wfile.write(bytes(error, 'utf-8'))
        elif (re.search("^/employees/[0-9]*\Z", self.path) != None):
            print(self.path[11:])
            if not getEmployeeById(self.path[11:]):
                self.send_response(404)
                self.send_header('Content-type', 'text/json')
                error = "NOT FOUND!"
                self.end_headers()
                self.wfile.write(bytes(error, 'utf-8'))
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/json')
                self.end_headers()
                result = getEmployeeById2(self.path[11:])

                types = ["id", "birth-date", "first-name", "last-name", "sex", "hire-date", "salaries"]
                list = []
                for employee in result:
                    list.append(dict(zip(types, employee)))



                self.wfile.write(json.dumps(list, indent=4, sort_keys=True, default=str).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/json')
            error = "NOT FOUND!"
            self.end_headers()
            self.wfile.write(bytes(error, 'utf-8'))

    # POST method defination
    def do_POST(self):

        if (self.path == "/employees"):
            body = self.get_header()
            employee = []
            employee.append(body["birth_date"])
            employee.append(body["first_name"])
            employee.append(body["last_name"])
            employee.append(body["gender"])
            employee.append(body["hire_date"])
            if checkEmployee(employee):
                addEmployee(employee)
                self.send_response(201)
                self.send_header('Content-type', 'text/json')
                self.end_headers()
                self.wfile.write("OK".encode())
            else:
                self.send_response(409)
                self.send_header('Content-type', 'text/json')
                error = "Conflict!"
                self.end_headers()
                self.wfile.write(bytes(error, 'utf-8'))

        elif (re.search("^/employees/[0-9]+/salary\Z", self.path) != None):
            if not getEmployeeById(self.path[11:]):
                self.send_response(404)
                self.send_header('Content-type', 'text/json')
                error = "NOT FOUND!"
                self.end_headers()
                self.wfile.write(bytes(error, 'utf-8'))
            else:
                body = self.set_and_get_header("post")
                salary = []
                salary.append(re.findall("[0-9]+", self.path)[0])
                salary.append(body["salary"])
                salary.append(body["date"])
                addSalary(salary)
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/json')
            error = "Bad Request!"
            self.end_headers()
            self.wfile.write(bytes(error, 'utf-8'))

    # PUT method Defination
    def do_PUT(self):
        if (self.path == "/employees"):
            self.send_response(405)
            self.send_header('Content-type', 'text/json')
            error = "Method Not Allowed!"
            self.end_headers()
            self.wfile.write(bytes(error, 'utf-8'))
        elif (re.search("^/employees/[0-9]*\Z", self.path) != None):
            if not getEmployeeById(self.path[11:]):
                self.send_response(404)
                self.send_header('Content-type', 'text/json')
                error = "NOT FOUND!"
                self.end_headers()
                self.wfile.write(bytes(error, 'utf-8'))
            else:
                body = self.set_and_get_header("put")
                employee = []
                employee.append(body["birth_date"])
                employee.append(body["first_name"])
                employee.append(body["last_name"])
                employee.append(body["gender"])
                employee.append(body["hire_date"])
                employee.append(int(self.path[11:]))
                updateEmployee(employee)
        elif (re.search("^/employees/[0-9]+/salary\Z", self.path) != None):
            if not getEmployeeById(self.path[11:]):
                self.send_response(404)
                self.send_header('Content-type', 'text/json')
                error = "NOT FOUND!"
                self.end_headers()
                self.wfile.write(bytes(error, 'utf-8'))
            else:
                body = self.set_and_get_header("put")
                salary = []
                salary.append(body["salary"])
                salary.append(body["date"])
                salary.append(re.findall("[0-9]+", self.path)[0])
                updateSalary(salary)
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/json')
            error = "Bad Request!"
            self.end_headers()
            self.wfile.write(bytes(error, 'utf-8'))

    # DELETE method defination
    def do_DELETE(self):
        if (self.path == "/employees"):
            self.send_response(405)
            self.send_header('Content-type', 'text/json')
            error = "Method Not Allowed!"
            self.end_headers()
            self.wfile.write(bytes(error, 'utf-8'))
        elif (re.search("^/employees/[0-9]*\Z", self.path) != None):
            if not getEmployeeById(self.path[11:]):
                self.send_response(404)
                self.send_header('Content-type', 'text/json')
                error = "NOT FOUND!"
                self.end_headers()
                self.wfile.write(bytes(error, 'utf-8'))
            else:
                deleteEmployee(self.path[11:])
                self.send_response(200)
                self.send_header('Content-type', 'text/json')
                self.end_headers()
                self.wfile.write("Employee deleted!".encode())
        elif (re.search("^/employees/[0-9]+/salary\Z", self.path) != None):
            if not getEmployeeById(self.path[11:]):
                self.send_response(404)
                self.send_header('Content-type', 'text/json')
                error = "NOT FOUND!"
                self.end_headers()
                self.wfile.write(bytes(error, 'utf-8'))
            else:
                deleteSalary(re.findall("[0-9]+", self.path)[0])
                self.send_response(200)
                self.send_header('Content-type', 'text/json')
                self.end_headers()
                self.wfile.write("Salary deleted!".encode())
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/json')
            error = "Bad Request!"
            self.end_headers()
            self.wfile.write(bytes(error, 'utf-8'))


# Server Initialization
server = HTTPServer(('127.0.0.1', 8080), ServiceHandler)
server.serve_forever()
