from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient  
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from.env file
import os  

app = Flask(__name__)  

# MongoDB connection setup  
client = MongoClient(os.getenv('MONGODB_URI'))  # Set your MongoDB URI as an environment variable  
db = client['github_webhooks']  
collection = db['events']  



@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')



@app.route('/webhook', methods=['POST'])  
def webhook():  
    data = request.json  
    action = data.get('action')  
    repository = data.get('repository')  
    ref = data.get('ref')  
    actor = data.get('actor')  
    timestamp = data.get('timestamp')  

    # Extract the branch name from ref  
    to_branch = ref.split('/')[-1] if ref else 'unknown'  

    # Prepare the document  
    document = {  
        'action': action,  
        'repository': repository,  
        'to_branch': to_branch,  
        'actor': actor,  
        'timestamp': timestamp  
    }  

    # Store in MongoDB  
    collection.insert_one(document)  

    return jsonify({'status': 'success'}), 200  

@app.route('/events', methods=['GET'])  
def get_events():  
    events = list(collection.find({}, {'_id': 0}))  # Exclude MongoDB ID  
    return jsonify(events), 200  

if __name__ == '__main__':  
    app.run(debug=True)