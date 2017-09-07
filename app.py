from __future__ import print_function
import json
import os, sys, json, requests
from flask import Flask, request, make_response
from flask import jsonify
from flask.ext.pymongo import PyMongo
from pymessenger import Bot
from datetime import datetime as dt

import io

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

app = Flask(__name__)




# Client Access Token for accessing our API AI Bot TODO: CHANGE THIS
CLIENT_ACCESS_TOKEN = '668999a33db140fa8fe2a7abcc79c77b'

# This seems waste
PAGE_ACCESS_TOKEN = "EAABlZAhiLCzsBAEPENnZC43ODWjX1X4VT43TBjHP8dx8WC7W6kqVRLiRz5AljcmkxSk1rfD2ZA4dDdE149D8JIurZBM67Afl6MRFyZBmqH55mTbJTSbHAjKlHSQrHGITB129ekYkdLqGb2ZBJnN7vyEH4HjgPiXzZAO0yW9wj3WXwZDZD"

# An endpoint to ApiAi, an object used for making requests to a particular agent.
ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)


bot = Bot(PAGE_ACCESS_TOKEN)




class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

'''
@app.route('/')
def index():
    return 'Hello world!'
'''

@app.route('/', methods=['GET'])
def verify():
    print ("Hellow world")
	# Webhook verification
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == "hello":
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello world I am Charles", 200



# Handling HTTP POST when APIAI sends us a payload of messages that have
# have been sent to our bot. 
@app.route('/webhook', methods=['POST'])
def handle_message():
    data = request.get_json()
    print("Request:")
    print(json.dumps(data, indent=4))
    res = processRequest(data)

    res = json.dumps(res, indent=4, cls=JSONEncoder)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    print("Before final return")
    return r

    


def processRequest(req):
    print('hi')
    if req.get("result").get("action") == "sales.statistics":
        myCustomResult = getParameters(req)
        res = makeWebhookResult(myCustomResult)
    elif req.get("result").get("action") == "welcome.intent":
        res = showWelcomeIntent(req)
        ''' TODO REMOVE temp
        myCustomResult = getDummyParameters(req)
        res = makeWebhookResult(myCustomResult)
        '''
        return {}
    else:
        return {}
    return res
'''
This is a very temp function. It is used to just create a sample response in JSON format
'''
def makeWebhookResult(data):
    speech = data
    '''
    print("Response:")
    print(speech)
    '''
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "DDAsisstant"
    }
    
def itemSelected(app):
    # Get the user's selection
    param = app.getContextArgument('actions_intent_option','OPTION').value
    print ("There is no chance it comes here")

def showWelcomeIntent(resp):
    print ("Inside show welcome intent")     


    return "Hi I am Phillips Bot"


'''
This function is a controller function which parses the parameters and then returns the sales amount
'''
def parseUserParametersGetSalesAmount(userParameters):

    cities = parseUserRegion(userParameters)
    product = parseUserProduct(userParameters)
    period = parseUserPeriod(userParameters.get('period'))

    return getSalesAmount(period, cities, product)
'''
This function returns the sales for the specified productId, cities, period
TODO: Change query into an aggregation function of mongo db in order to expedite the process & lift load from python
'''
def getSalesAmount(period, cities, productId):
    print ("In get sales amount")


    salesRev = 0
    salesData = mongo.db.sales1
    startDate = period["startDate"]
    endDate = period["endDate"]
    '''
    If it is a single date else it is a range
    '''
    
    try: 
        for s in salesData.find({'pId': productId, 'city': {'$in':cities},'date': startDate}):
            print("The sales revenue is:"+s['salesRev'])
            salesRev = salesRev + int(s['salesRev'])
        
        print("The cumulative sales revenue is:" + str(salesRev))
        return str(salesRev)
        
    except Exception:
        print("Could not query database")
        return ''
    







def parseUserPeriod(period):
    '''print ("Period at index 0 is:" + period[0])'''
    '''print ("trying to get date at index 0" + period[0].get('date'))'''
    if period.get('date') != None:
        return parseDate(period.get('date'))
    elif period.get('date-period') != None:
        return parseDateRange(period.get('date-period'))
    else:
        return {"startDate": "", "endDate": ""}
                                     
def parseDateRange(datePeriod):
    print("Inside Parse for Date Period")
    startDate = datePeriod.split('/')[0]
    print ("The start date is:" + startDate)
    endDate = datePeriod.split('/')[1]
    print ("The end date is:" + endDate)
    
    return {"startDate": startDate, "endDate": endDate}
    

def parseDate(date):
    print("Inside Parse for Date")
    
    return {"startDate": date, "endDate": ""}

'''
Returns an array of cities (even if it is a single city)
'''
def parseUserRegion(parameters):
    if parameters.get('sys.geo-city-us') != None:
        return [parameters.get('sys.geo-city-us')]
    elif parameters.get('sys.geo-state-us') != None:
        return parseState(parameters.get('sys.geo-state-us'))
    elif parameters.get('region') != None:
        return parseRegion(parameters.get('region'))
    else:
        return getDefaultRegion()















def createImage():
    image = Image.open('profile.jpg')
    image.show()



def getParameters(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("city")
    print("The city is:")
    print(city)
    '''
    duration = parameters.get("Duration")
    print("The duration is:")
    print(duration)
    sales = queryData(city, duration)
    '''
    period = parameters.get("period")
    print("The period is:")
    print(period)
    sales = parsePeriod(period, city)
    print("The sales are:")
    print(sales)
    
    '''return "The sales data for " + city + "and duration" + duration + "is 12345"'''
    return "The sales data for " + city + " and duration is " + sales
    '''return "abcd"'''




# Sending a message back through Messenger.
def send_message(sender_id, message_text):
    print('in send msg')
    r = requests.post("https://api.api.ai/v1/",
 
        
 
        headers={"Content-Type": "application/json"},
 
        data=json.dumps({
        "recipient": {"id": sender_id},
        "message": {"text": message_text}
    }))



# Takes a string of natural language text, passes it to ApiAI, returns a
# response generated by an ApiAI bot.
def parse_natural_text(user_text):
    print('hi there!')
    # Sending a text query to our bot with text sent by the user.
    request = ai.text_request()
    request.query = user_text
 
    # Receiving the response.
    response = json.loads(request.getresponse().read().decode('utf-8'))
    responseStatus = response['status']['code']
    if (responseStatus == 200):
        # Sending the textual response of the bot.
        return (response['result']['fulfillment']['speech'])
 
    else:
        return ("Sorry, I couldn't understand that question")
 
    # NOTE:
    # At the moment, all messages sent to ApiAI cannot be differentiated,
    # they are processed as a single conversation regardless of concurrent
    # conversations. We need to perhaps peg a session id (ApiAI) to a recipient
    # id (Messenger) to fix this.
 
    # request.session_id = "<SESSION ID, UNIQUE FOR EACH USER>"
 
# Sends the message in segments delimited by a period.
def send_message_staggered(sender_id, message_text):
    print('staggered') 
    sentenceDelimiter = ". "
    messages = message_text.split(sentenceDelimiter)
   
    for message in messages:
        send_message(sender_id, message)

@app.route('/add')

def add():
    
    sale = mongo.db.sales
    sale.insert({'city' : 'Mumbai', 'date': 'June', 'amount' : '1900'})
    return 'Added Sales row'

@app.route('/query')
def query():
    sale = mongo.db.sales
    output = []
    for s in sale.find({'city': 'Pune'}):
        output.append({'city' : s['city'], 'date' : s['date'], 'amount': s['amount']})
    return jsonify({'output':output})

if __name__ == "__main__":
    app.run()
    '''app.run(debug = True, port = 80)'''
    
'''
End of file!!!!
'''
