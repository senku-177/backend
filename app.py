# Filename - server.py

# Import flask and datetime module for showing date and time
from flask import Flask,request,jsonify,Blueprint
from flask_cors import CORS
from pymongo import MongoClient
from bson import json_util
import jwt
import json
import uuid
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv('SECRET_KEY')
database_url = os.environ.get('DATABASE_URL')

print(key)
x = datetime.datetime.now()

# Initializing flask app
app = Flask(__name__)

client = MongoClient(database_url)
db = client["netropolis"]

api_bp = Blueprint('api', __name__)


CORS(app, origins='*')


@api_bp.before_request
def Authorisation_middleware():  # Corrected function name
    authorization_header = request.headers.get('Authorization')
    print(authorization_header)
    if authorization_header:
        token = authorization_header.split(' ', 1)
        print("Token: ", token[1])
        user = jwt.decode(token[1], key, algorithms=["HS256"])
        print(user)
        request.user = user


def parse_json(data):
	return json.loads(json_util.dumps(data))

@app.route('/health/', methods=['GET'])
def health():
	return jsonify({"message" : "ok"}), 200

# Route for seeing a data
@app.route('/login',methods=['POST'])
def login():
	data= request.json
	email=data.get('email')
	password= data.get('password')
	
	encoded= jwt.encode({"userid":email},key,algorithm="HS256")
	if email and password:
		collections= db["user-list"]
		user=collections.find_one({"email":email})
		if not user:
			return jsonify({"message":"no such user"}),401
		else:
			
			if user["password"]==password:
				
				return jsonify({"message":"successful","token":encoded,"userid":email,"role":user["role"]}),200
			
			else:
				return jsonify({"message":"password mismatch"}),401


@app.route('/register',methods=['POST'])
def register():
	data=request.json
	email=data.get("email")
	password=data.get("password")
	name=data.get("name")
	city=data.get("age")
	age=data.get("age")
	state= data.get("state")

	if email and password:
		collections=db["user-list"]
		user=collections.find_one({"email":email})
		if not user:
			collections.insert_one({"name":name,"email":email,"password":password,"age":age,"city":city,"state":state ,"role":data.get("role"),"RegisteredQuests":[]})
			return jsonify({"message":"login successful"}),200
		else:
			return jsonify({"message":"user exists"}),400

@app.route('/QuestRegister',methods=['POST'])
def TaskRegister():
	
	data=request.json
	
	email=data.get("email")
	TaskName=data.get("TaskName")
	PersonName=data.get("PersonName")
	Details=data.get("Details")
	City=data.get("City")
	State=data.get("State")
	Reward=data.get("Reward")
	Duration=data.get("Duration")
	ContactDetails=data.get("Contact")
	print(email)

	if TaskName and City and State:
		unique_id = str(uuid.uuid4())
		print("Quest Register Progess",data)
		collections=db["Task-list"]
		collections.insert_one({"id":unique_id,"email":email,"TaskName":TaskName, "PersonName":PersonName,"City":City,"State":State, "Reward":Reward,"Duration":Duration,"ContactDetails":ContactDetails,"Details":Details})
		return jsonify({"message":"Successfull Registration"}),200
	else:
		return jsonify({"message":"registration failed"}),400


@app.route("/QuestRegisterPage_state",methods=["GET"])
def StateFetch():
	collections=db["Task-list"]
	
	states=collections.distinct("State")
	states=sorted(states)
	print(states)

	return jsonify(states),200


@app.route("/QuestRegisterPage_cities",methods=["POST"])
def CityFetch():
	data= request.json
	state= data.get("state")
	
	collections = db["Task-list"]
	entries = collections.aggregate([
        { "$match": { "State": state } },
        { "$group": { "_id": "$City", "entries": { "$push": "$$ROOT" } } }
    ])
	entries_list = list(entries)

	
	entries_list=parse_json(entries_list)
	print(entries_list)
	return jsonify(entries_list), 200


	
@app.route("/QuestRegister_Quest",methods=["POST"])
def QuestRegister():
	
	data=request.json
	print(data)
	collections=db["Quest-List"]
	unique_id = str(uuid.uuid4())


	
	
	collections.insert_one({"QuestId":unique_id,"QuestName":data.get("QuestName"),"itinerary":data.get("itinerary"),"charges":data.get("charges"),"details":data.get("details"),"length":data.get("length"),"tasks":data.get("tasks"),"state":data.get("state")})
	
	return jsonify({"mesesage":"succesful"}),200


@api_bp.route("/Dashboard_getUser",methods=['GET'])
def fetchUser():
	user = request.user
	collections=db["user-list"]
	a=collections.find_one({"email":user.get("userid")})
	
	
	a= parse_json(a)
	print(a)
	return jsonify(a),200

@api_bp.route("/Dashboard_quests",methods=["POST"])
def fetchQuests():
	data=request.json
	print("data",data)
	collections=db["Quest-List"]
	entries=collections.find({"state":data.get("State")})
	entries=parse_json({entries})
	print(entries)
	return jsonify(entries),200

@api_bp.route("/Dashboard_quests",methods=["GET"])
def fetchQuestsAll():
	
	collections=db["Quest-List"]
	entries=collections.find({})
	entries=parse_json({entries})
	print(entries)
	return jsonify(entries),200


@app.route("/search",methods=["GET"])
def search_entries():
    keyword = request.args.get('keyword')
    collection=db["Quest-List"]
    results = collection.find({'$or': [
    {'QuestName': {'$regex': keyword, '$options': 'i'}},
    {'details': {'$regex': keyword, '$options': 'i'}},
	{'itenenary':{'$regex':keyword,'$options':'i'}},
    
]})
    print(results)
    entries = results
    print(entries)
    entries=parse_json({entries})
    return jsonify(entries),200

@api_bp.route("/questId",methods=["GET"])
def fetchQuest():
	keyword=request.args.get('keyword')
	print(keyword)
	collection=db["Quest-List"]
	result= collection.find({"QuestId":keyword})
	print(result)
	result= parse_json({result})
	return jsonify(result),200

@api_bp.route("/joinQuest",methods=["GET"])
def JoinQuest():
	keyword=request.args.get("keyword")
	print(keyword)
	userlist=db["user-list"]
	print(request.user)
	user=userlist.find_one({"email":request.user.get("userid")})
	if user:
		
		
		if user['RegisteredQuests'].count(keyword)==0:
			user['RegisteredQuests'].append(keyword)
			print(user)
	
			userlist.update_one({'email': request.user.get("userid")}, {'$set': {'RegisteredQuests': user['RegisteredQuests']}})

			return jsonify({'message': 'User updated successfully'}),200
		else:
			print("2000")
			return jsonify({'error': 'User not found'}), 404

	else:
		return jsonify({'error': 'User not found'}), 404


@api_bp.route("/Dashboard_myquests",methods=["GET"])
def fetchMyQuests():
	collection=db['user-list']
	user=collection.find_one({'email':request.user.get('userid')})
	if user:
		QuestList=db["Quest-List"]
		print(user['RegisteredQuests'])
		myQuests=[]
		i =0
		for id in user['RegisteredQuests']:
			print(id)
			Quest=QuestList.find_one({"QuestId":id})
			myQuests.append(Quest)
		print(myQuests)
		result = parse_json(tuple(myQuests))
		return jsonify(result),200
	else:
		return jsonify({'error': 'User not found'}), 404
app.register_blueprint(api_bp)
# Running app
if __name__ == '__main__':
	app.run(debug=True)
