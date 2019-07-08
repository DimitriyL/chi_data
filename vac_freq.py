import csv
import sqlite3

# connecting to the database
connection = sqlite3.connect('per_capita.db')

# cursor
crs = connection.cursor()

# sql command to create the preliminary table
sql_command = """CREATE TABLE prelim_pop (
community CHAR PRIMARY KEY,
population REAL
);
"""
crs.execute (sql_command)
sql_command = """CREATE TABLE prelim_quan (
community CHAR PRIMARY KEY,
quantity REAL
);
"""
crs.execute (sql_command)
sql_command = """CREATE TABLE prelim_pov (
community CHAR PRIMARY KEY,
poverty REAL,
income REAL,
hardship REAL
);
"""
crs.execute (sql_command)
sql_command = """CREATE TABLE per_capita (
community CHAR PRIMARY KEY,
population REAL,
quantity REAL,
poverty REAL,
income REAL,
hardship REAL,
per_cap REAL
);
"""
crs.execute (sql_command)
connection.commit()

vacancies = csv.DictReader (open ('vacant.csv', 'rU') )
population = csv.DictReader (open ('community_pop_2010.csv', 'rU') )
income = csv.DictReader (open ('income.csv', 'rU') )

filenames = ['Community', 'Population', 'Quantity', 'Per Capita']

def test (readable):
    for line in readable:
        print (line ['Community'])

def convert ():
    for line in vacancies:
        line['Community'] = line['Community'].lower()

def simplifyNum (string):
    newstr = string.replace(',', '')
    return newstr

def insert():
    for line in population:
        sql_command = "INSERT INTO prelim_pop (community, population) VALUES ("
        sql_command += '"' + line['Community'].lower() + '"' + ','
        sql_command += '' + simplifyNum(line['2010']) + ');'
        #print(sql_command)
        crs.execute (sql_command)

    sql_command = "INSERT INTO per_capita (community, population) SELECT community, population FROM prelim_pop;"
    crs.execute (sql_command)

    for line in vacancies:
        sql_command = "INSERT INTO prelim_quan (community, quantity) VALUES ("
        sql_command += '"' + line['Community'].lower() + '"' + ','
        sql_command += '' + simplifyNum(line['Quantity']) + ');'
        #print(sql_command)
        crs.execute (sql_command)

        sql_command = "UPDATE per_capita SET quantity = "
        sql_command += '' + simplifyNum(line['Quantity']) + ' WHERE community = '
        sql_command += '"' + simplifyNum(line['Community']).lower() + '";'
        #print(sql_command)
        crs.execute (sql_command)

        #sql_command = "INSERT INTO per_capita (quantity) SELECT quantity FROM prelim_quan WHERE community = "
        #sql_command += '"' + line['Community'].lower() + '";'
        #crs.execute(sql_command)

    for line in income:
        sql_command = "INSERT INTO prelim_pov (community, poverty, income, hardship) VALUES ("
        sql_command += '"' + line['Community'].lower() + '",'
        sql_command += '' + simplifyNum(line['PERCENT HOUSEHOLDS BELOW POVERTY']) + ','
        sql_command += '' + simplifyNum(line['Income']) + ','
        sql_command += '' + simplifyNum(line['Hardship']) + ');'
        #print(sql_command)
        crs.execute (sql_command)

        sql_command = "UPDATE per_capita SET poverty = "
        sql_command += '' + simplifyNum(line['PERCENT HOUSEHOLDS BELOW POVERTY']) + ' WHERE community = '
        sql_command += '"' + simplifyNum(line['Community']).lower() + '";'
        #print(sql_command)
        crs.execute (sql_command)

        sql_command = "UPDATE per_capita SET income = "
        sql_command += '' + simplifyNum(line['Income']) + ' WHERE community = '
        sql_command += '"' + simplifyNum(line['Community']).lower() + '";'
        #print(sql_command)
        crs.execute (sql_command)

        sql_command = "UPDATE per_capita SET hardship = "
        sql_command += '' + simplifyNum(line['Hardship']) + ' WHERE community = '
        sql_command += '"' + simplifyNum(line['Community']).lower() + '";'
        #print(sql_command)
        crs.execute (sql_command)

    connection.commit()

insert()

def calculate ():
    crs.execute("SELECT * FROM per_capita;")
    rows = crs.fetchall()

    for row in rows:
        # note that this is per 100 residents
        val = (row[2] / row[1]) * 100 # row[2] is quantity, row[1] is population

        sql_command = "UPDATE per_capita SET per_cap = "
        sql_command += str(val) + ' WHERE community = ' + '"' + row[0] + '"' + ';'
        #print (sql_command)
        crs.execute(sql_command)

    connection.commit()

calculate()


def newFile (readable):
    with open ('per_capita.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
