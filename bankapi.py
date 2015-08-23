#Leszek Dubicki
#Student ID: x14125439
# Flask bank API prototype created for Web Services and API Development module


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
    'account_id': 1,
    'customer_id': 1,
    'type': '1',
    'status': 1
    },
    {'id': 2,
    'number': '4565364585963679',
    'account_id': 2,
    'customer_id': 2,
    'type': '1',
    'status': 1
    }
    ]
accounts = [
    {'id': 1,
    'number': '000000000000000000001111',
    'customer_id': 1,
    'balance': 3000.
        },
    {'id': 2,
    'number': '000000000000000000001112',
    'customer_id': 2,
    'balance': 30000.
        }
    ]

transactions = [
    {'id': 1,
    'type': 0, #transaction type tells if it's card transaction (0) or directly to another account (1)
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
            return None 
    def getFields(self, tableName):
        #returns all fields for give table name
        if tableName in self.tables:
            return self.tables[tableName][0].keys()
        else:
            return None

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
    def findIndex(self, tableName, item_id):
        #finds index in list of record for given
        item_id = int(item_id) #just in case
        index = None 
        for i in range(0, len(self.tables[tableName])):
            if int(self.tables[tableName][i]['id']) == item_id:
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
        newid = self.nextId[tableName]
        self.nextId[tableName] +=1
        return newid
    def addFields(self, tableName, field_id):
        #add all necessary fields to a record:
        fields = self.getFields(tableName)
        i = self.findIndex(tableName, field_id)
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
            return {'error': "no table" + tableName} #error code for no_table, 0 is no error
        missingFields = self.checkMandFields(tableName, record)
        if len(missingFields)>0:
            #we don't have enough fields, need to update
            return {'missingFields': missingFields, 'error': 2}
        #now we can create a unique record, let's add a new id to the record:
        newid = self.newId(tableName)
        record['id'] = newid
        self.tables[tableName].append(record)
        self.addFields(tableName, newid)
        #find created record:
        index = self.findIndex(tableName, newid)
        #return full record:
        return self.tables[tableName][index]
    def update(self, tableName, record):
        #creates record in table:
        t = self.getTable(tableName)
        if not t:
            return {'error': "no table" + tableName} #error code for no_table, 0 is no error
        #now we can update record
        i = self.findIndex(tableName, int(record['id']))
        if i == None:
            return {'error':"no record with given id: "+str(record['id'])}

        for F in self.tables[tableName][i]:
            if F in record:
                self.tables[tableName][i][F] = record[F]
        return self.tables[tableName][i] #return complete record.
    def delete(self, tableName, item_id):
        #creates record in table:
        t = self.getTable(tableName)
        if not t:
            return {'error': "no table" + tableName} #error code for no_table, 0 is no error
        #now we can DELETE record
        i = self.findIndex(tableName, item_id)
        if i == None:
            return {'error':"no record with given id: "+str(item_id)}
        record = self.tables[tableName][i]
        #delete list element:
        self.tables[tableName].__delitem__(i)
        return record
    def checkBalance(self, account_id):
        accountIndex = self.findIndex('accounts', account_id)
        return self.tables['accounts'][accountIndex]['balance']
    def cardTransaction(self, data):
        transactionType = 0 #card transaction
        #it's for both withdrawl and lodgement
        #find index of card
        if not 'card_id' in data:
            return {'error':'no card_id given'}
        else:
            card_id = int(data['card_id'])
            cardIndex = self.findIndex('cards', card_id)
            if cardIndex == None:
                return {'error':'no card with id: '+str(card_id)}

        #find index of account
        account_id = self.tables['cards'][cardIndex]['account_id']
        accountIndex = self.findIndex('accounts', account_id)
        if accountIndex == None:
            return {'error':'no account with id: '+str(account_id)}

        if not 'amount' in data:
            return {'error':'no amount given'}
        else:
            balance = self.checkBalance(account_id)
            print balance
            if balance < -1*float(data['amount']):
                return {'error':'insufficient funds'}
            else:
                #update the account
                self.tables['accounts'][accountIndex]['balance'] += data['amount']
        #add record to transactions and update proper account balance:
        return self.create('transactions', {'type':transactionType, 'account_id':account_id, 'to_account_id': card_id, 'amount':data['amount']})
    def accountTransaction(self, data):
        transactionType = 1 #not card transaction
        #find index of an account
        if not 'to_account_id' in data:
            return {'error':'no to_account_id given'}
        else:
            to_account_id = int(data['to_account_id'])
            toAccountIndex = self.findIndex('accounts', to_account_id)
            if toAccountIndex == None:
                return {'error':'no account with id: '+str(to_account_id)}

        #find index of account
        if not 'account_id' in data:
            return {'error':'no account_id given'}
        else:
            account_id = data['account_id']
            accountIndex = self.findIndex('accounts', account_id)
            if accountIndex == None:
                return {'error':'no account with id: '+str(account_id)}

        if not 'amount' in data:
            return {'error':'no amount given'}
        else:
            balance = self.checkBalance(account_id)
            if balance < data['amount']:
                return {'error':'insufficient funds'}
            else:
                #update the account
                self.tables['accounts'][accountIndex]['balance'] += data['amount']
        #add record to transactions and update proper account balance:
        return self.create('transactions', {'type':transactionType, 'account_id':account_id, 'to_account_id': to_account_id, 'amount':data['amount']})




#webapp part:
DB = database(customers, accounts, cards, transactions, mandatoryFields)

runFlask = False #added for testing in no-flask environment 
if not runFlask:
    print DB.cardTransaction({'card_id':1, 'amount': -2000})
    exit()

from flask import Flask, jsonify, request
from flask.ext.httpauth import HTTPBasicAuth

app = Flask(__name__)
auth = HTTPBasicAuth()

#define username and password:
@auth.get_password
def get_password(username):
    if username == 'superuser':
        return 'webapi'
    return None

#define response in case of unauthorized access:
@auth.error_handler
def unauthorized():
    return jsonify({'error': 'Unauthorized access'})

@app.route('/bank/api/v1.0/<string:table_name>', methods = ['GET'])
@auth.login_required
def get_tables(table_name):
    #return records for given table and for given id:
    return jsonify({table_name:DB.getTable(table_name)})

@app.route('/bank/api/v1.0/<string:table_name>/<int:id>', methods = ['GET'])
@auth.login_required
def get_records(table_name,id):
    #return records for given table and for given id:
    record = DB.find(table_name,'id',id)
    return jsonify({table_name:record})

#@app.route('/bank/api/v1.0/customers', methods = ['POST'])
@app.route('/bank/api/v1.0/<string:table_name>', methods = ['POST'])
@auth.login_required
def create_resource(table_name):
    record = {}
    if table_name in ["transactions"]:
        #not allowed to edit transactions directly
        return jsonify({'error':'this table can not be modified directly'}), 410
    fields = DB.getFields(table_name)
    for F in fields:
        if F in request.json:
            record[F] = request.json[F]
    record = DB.create(table_name, record)
    return jsonify({DB.recordName(table_name):record}), 201

@app.route('/bank/api/v1.0/lodgement', methods = ['POST'])
@auth.login_required
def add_lodgement():
    #getting data:
    data = request.json
    data['amount'] = float(data['amount'])
    if data['amount'] < 0:
        return jsonify({'error':'amount must be greater than 0'}), 510
    record = DB.cardTransaction(data)
    return jsonify({'transaction':record}), 201

@app.route('/bank/api/v1.0/withdrawl', methods = ['POST'])
@auth.login_required
def add_withdrawl():
    #getting data:
    data = request.json
    data['amount'] = float(data['amount'])
    if data['amount'] < 0:
        return jsonify({'error':'amount must be greater than 0'}), 510

    record = DB.cardTransaction(data)
    return jsonify({'transaction':record}), 201

@app.route('/bank/api/v1.0/transfer', methods = ['POST'])
@auth.login_required
def add_transfer():
    #getting data:
    data = request.json
    data['amount'] = float(data['amount'])
    if data['amount'] < 0:
        return jsonify({'error':'amount must be greater than 0'}), 510

    record = DB.accountTransaction(data)
    return jsonify({'transaction':record}), 201

#route for updating a record
@app.route('/bank/api/v1.0/<string:table_name>', methods = ['PUT'])
@auth.login_required
def update_resource(table_name):
    record = {}
    fields = DB.getFields(table_name)
    for F in fields:
        if F in request.json:
            record[F] = request.json[F]
        #record["id"] = 1
        #there must be an 'id' field in record
        #record = request.json
    if not 'id' in record:
        return jsonify({'error':"no id in record"}), 410
    else:
        record = DB.update(table_name, record)
        return jsonify({DB.recordName(table_name):record})

@app.route('/bank/api/v1.0/<string:table_name>/<int:id>', methods = ['PUT'])
@auth.login_required
def update_resource_by_id(table_name, id):
    index = DB.findIndex(table_name, id)
    if index == None:
        return {"error":"id not found: " + str(id)}
    record = {"id": DB.tables[table_name][index]["id"]}
    fields = DB.getFields(table_name)
    for F in fields:
        if F in request.json:
            record[F] = request.json[F]
        #record["id"] = 1
        #there must be an 'id' field in record
        #record = request.json
    if not 'id' in record:
        return jsonify({'error':"no id in record"}), 410
    else:
        record = DB.update(table_name, record)
        return jsonify({DB.recordName(table_name):record})


@app.route('/bank/api/v1.0/<string:table_name>/<int:id>', methods = ['DELETE'])
@auth.login_required
def delete_resource_by_id(table_name, id):
    return jsonify({"deleted" : DB.delete(table_name, id)})


@app.route('/')
def home():
    HTML = '<p>Welcome in bankapi project main page!</p>'
    HTML += "<p>The API has the following resources available through GET method:</p>"
    HTML += "<p></p>"
    HTML += "<p></p>"
    HTML += "<p></p>"
    HTML += "<p>For security reasons all requests must contain username and password, for the presentation purposes username: superuser with password webapi is available</p>"
    return HTML


if __name__ == "__main__":
    app.run()
