
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, jsonify, request

#In memory database:
mandatoryFields = {
    'customers': ['name', 'email'],
    'cards': ['number', 'customer_id'], #default type: 1
    'accounts': ['number', 'customer_id'],
    'transactions': ['to_account_id', 'type', 'account_id', 'amount']
    }
customers = [
    {'id': 1,
    'name': 'Richard Blabla',
    'email': 'richie@hehe.com'
    },
    {'id': 2,
    'name': 'John Blabla',
    'email': 'johnie@hehe.com'
    }]
cards = [
    {'id': 1,
    'number': '4565364585963678',
    'customer_id': 1,
    'type': '1',
    'status': 1
    }
    ]
accounts = [
    {'id': 1,
    'number': '000000000000000000001111',
    'customer_id': 1,
    'balance': 3000.
        }
    ]

transactions = [
    {'id': 1,
    'type': 0, #transaction type tells if it's card transaction or directly to another account
    #'card_id': 1, #foreign key - card used (None if no card was used)
    'account_id': 1,  #foreign key - account
    'to_account_id': 2,   #foreign key - account or card id to/from which the funds were moved
    'amount': 3000.
    }]

#End of database
#_____________________________________________________________________________

#Classes:
class database:
    #allows access to database
    #created to assure data integrity when changing and simplify access to the data.
    def __init__(self, customers, accounts, cards, transactions, mandatoryFields):
        #global customers, accounts, cards, transactions, mandatoryFields
        self.tables = {'customers':customers, 'transactions':transactions, 'cards':cards, 'accounts':accounts}
        self.mandatoryFields = mandatoryFields
        self.setNextId()
    def setNextId(self):
        #method to search all tables and find id's bigger than maximum's
        self.nextId = {}
        for t in self.tables:
            self.nextId[t] = 0
            for r in self.tables[t]:
                if r['id'] > self.nextId[t]:
                    self.nextId[t] = r['id']+1

    def getTable(self, tableName):
        if tableName in self.tables:
            return self.tables[tableName]
        else:
            return False
    def getFields(self, tableName):
        #returns all fields for give table name
        if tableName in self.tables:
            return self.tables[tableName][0].keys()
        else:
            return False

    def find(self, tableName, key, value):
        #finds a record in table
        t = self.getTable(tableName)
        if not t:
            return {'error':1} #error code for no_table, 0 is no error
        if not key in t[0]:
            return 2 #no field <key> in first record (which I assume is represetative)
        records = []
        for r in t:
            if r[key] == value:
                records.append(r)
        return records
    def findIndex(self, tableName, id):
        #finds index in list of record for given
        for i in range(0, len(self.tables[tableName])):
            if self.tables[tableName][i]['id']:
                index = i
                break
        return index
    def checkMandFields(self, tableName, record):
        #checking if all mandatory fields are present in record
        m = self.mandatoryFields[tableName]
        missingFields = []
        for f in record:
            if not f in m:
                missingFields.append(f)
        return missingFields
    def newId(self, tableName):
        id = self.nextId[tableName]
        self.nextId[tableName] +=1
        return id
    def addFields(self, tableName, id):
        #add all necessary fields to a record:
        fields = self.getFields(tableName)
        i = self.findIndex(tableName, id)
        for F in fields:
            if not F in self.tables[tableName][i]:
                self.tables[tableName][i][F] = None

    def recordName(self, tableName):
        #all tables are regular nouns
        return tableName[:-1]
def create(self, tableName, record):
        #creates record in table:
        t = self.getTable(tableName)
        if not t:
            return {'error': 1} #error code for no_table, 0 is no error
        missingFields = self.checkMandFields(tableName, record)
        if len(missingFields)>0:
            #we don't have enough fields, need to update
            return {'missingFields': missingFields, 'error': 2}
        #now we can create a unique record, let's add a new id to the record:
        id = self.newId(tableName)
        record['id'] = id
        self.tables[tableName].append(record)
        self.addFields(tableName, id)
def update(self, tableName, record):
        #creates record in table:
        t = self.getTable(tableName)
        if not t:
            return {'error': 1} #error code for no_table, 0 is no error
        #now we can update record
        i = self.findIndex(tableName, record['id'])
        for F in self.tables[tableName][i]:
            if F in record:
                self.tables[tableName][i][F] = record[F]
        return self.tables[tableName][i] #return complete record.


class Model:
    #base class for all models
    def __init__(self, record):
        self._record = record



#webapp part:
DB = database(customers, accounts, cards, transactions, mandatoryFields)
app = Flask(__name__)

#@app.route('/bank/api/v1.0/customers/')
#def get_customers():
#    return jsonify({'customers':DB.getTable('customers')})

#@app.route('/bank/api/v1.0/customers/<int:customer_id>', methods = ['GET'])
#def get_customer(customer_id):
#    #customer = [customer for customer in customers if customer['id'] == customer_id]
#    customer = DB.find('customers','id',customer_id)
#    return jsonify({'customer':customer})

@app.route('/bank/api/v1.0/<string:table_name>', methods = ['GET'])
def get_tables(table_name):
    #return records for given table and for given id:
    return jsonify({table_name:DB.getTable(table_name)})

@app.route('/bank/api/v1.0/<string:table_name>/<int:id>', methods = ['GET'])
def get_records(table_name,id):
    #return records for given table and for given id:
    record = DB.find(table_name,'id',id)
    return jsonify({table_name:record})

#@app.route('/bank/api/v1.0/customers', methods = ['POST'])
@app.route('/bank/api/v1.0/<string:table_name>', methods = ['POST'])
def create_resource(table_name):
    record = {}
    fields = DB.getFields(table_name)
    for F in fields:
        if F in request.json:
            record[F] = request.json[F]
    DB.create(table_name, record)
    return jsonify({DB.recordName(table_name):record}), 201

#route for updating a record
@app.route('/bank/api/v1.0/<string:table_name>', methods = ['PUT'])
def update_resource(table_name):
    record = {}
    fields = DB.getFields(table_name)
    for F in fields:
        #if F in request.json:
        #    record[F] = request.json[F]
        #there must be an 'id' field in record
        record = request.json
        if not 'id' in record:
            return jsonify({'error':"no id in record"}), 410
        else:
            record = DB.update(table_name, record)
            return jsonify({DB.recordName(table_name):record})


@app.route('/')
def home():
    return 'Welcome in bankapi project main page!'

if __name__ == "__main__":
    app.run()
