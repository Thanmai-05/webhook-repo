from flask import Flask, request, jsonify, render_template  
from pymongo import MongoClient  
from dotenv import load_dotenv  
import os  
from datetime import datetime  

load_dotenv()  # Load environment variables from .env file  

app = Flask(__name__)  

# MongoDB connection setup  
client = MongoClient(os.getenv('MONGODB_URI'))  # Set your MongoDB URI as an environment variable  
db = client['github_webhooks']  
collection = db['events']  

@app.route('/', methods=['GET'])  
def index():  
    return render_template('index.html')  

@app.route('/webhook', methods=['POST'])  
def webhook():  
    data = request.json  
    action = data.get('action')  
    repository = data.get('repository', {}).get('full_name', 'unknown repository')  
    actor = data.get('sender', {}).get('login', 'unknown actor')  
    timestamp = datetime.utcnow().isoformat() + "Z"  # Use current UTC time in ISO format  

    # Handle 'push' event
    if 'ref' in data and action == 'push':  
        to_branch = data['ref'].split('/')[-1]  # Extract branch name  
        document = {  
            'event': 'push',  
            'repository': repository,  
            'to_branch': to_branch,  
            'actor': actor,  
            'timestamp': timestamp  
        }  
    # Handle 'pull_request' events (including merge)
    elif 'pull_request' in data and action in ['opened', 'closed', 'reopened', 'merged']:  
        from_branch = data['pull_request']['head']['ref']  
        to_branch = data['pull_request']['base']['ref']  
        event_type = 'pull_request' if action != 'merged' else 'merge'  # Distinguish between pull request and merge  
        
        document = {  
            'event': event_type,  # Store as either 'pull_request' or 'merge'  
            'repository': repository,  
            'from_branch': from_branch,  
            'to_branch': to_branch,  
            'actor': actor,  
            'timestamp': timestamp,  
            'action': action  # Store the specific action like 'opened', 'closed', 'merged'
        }  
    else:  
        return jsonify({'status': 'ignored', 'reason': 'unsupported event type'}), 200  

    # Store event in MongoDB  
    collection.insert_one(document)  
    return jsonify({'status': 'success'}), 200  

@app.route('/events', methods=['GET'])  
def get_events():  
    events = list(collection.find({}, {'_id': 0}))  # Exclude MongoDB ID  
    return jsonify(events), 200  

if __name__ == '__main__':  
    app.run(debug=True)
