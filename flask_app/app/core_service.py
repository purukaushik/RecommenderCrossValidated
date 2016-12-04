from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from pymongo import MongoClient

# MONGODB CONFIGURATION
# MONGODB_HOST = 'localhost'
MONGODB_HOST = 'ec2-52-43-158-164.us-west-2.compute.amazonaws.com'
MONGODB_PORT = 27017
DB = 'dvproject'
PAGE_NO = 'pageNo'
COLLAB_FILTER = 'dbrelposts0'
COSINE_SIM = 'dbrelcosineposts0'
TOPICS = 'dbtopics0'
AGGREGATE = 'dbaggregate0'
METADATA = 'dbmetadata0'

# Flask INIT
app = Flask(__name__)
app.config.from_object(__name__)
CORS(app)

# MONGODB Connection
conn = MongoClient(host=app.config['MONGODB_HOST'], port=app.config['MONGODB_PORT'])


def get(algo, topic, list_topics=False):
    if algo == 'collabf':
        db_collection = conn[DB][COLLAB_FILTER]
    elif algo == 'cosine':
        db_collection = conn[DB][COSINE_SIM]
    else:
        return {}
    cursor = db_collection.find({"name": topic}, {"related_topics": 1})

    related_topics = [x.get("related_topics") for x in cursor]
    if list_topics:
        related_topics_list = [x.get('name') for x in related_topics[0]]

        return {"topic": topic,
                "related_topics_list": related_topics_list
                }
    return related_topics[0]


def getDescription(topic):    
    cursor = conn[DB][TOPICS].find({"name": topic}, {"description": 1})
    description = cursor[0].get("description")
    return description


def get_topics():
    db_collection = conn[DB][TOPICS]
    cursor = db_collection.find()
    topics = [topic.get("name") for topic in cursor]
    return {"topics": topics}


@app.route("/", strict_slashes=False)
def home():
    return Response(response="Not authorized to view this page.", status=200)


@app.route("/heartbeat", strict_slashes=False)
def heartbeat():
    return jsonify({
        "heartbeat": "success"
    })


@app.route("/topicslist", methods=["GET"], strict_slashes=False)
def list_topics():
    return jsonify(get_topics())


@app.route("/<algo>", methods=["GET"], strict_slashes=False)
def get_filter_data(algo):
    if len(request.args) != 0:

        topic = request.args.get('topic')
        if topic:
            topics_list = request.args.get('list')
            if topics_list:
                return jsonify(get(algo, topic, topics_list))
            else:
                return jsonify(get(algo, topic))
    return jsonify({})


@app.route("/related", methods=["GET"], strict_slashes=False)
def get_related_data():
    if len(request.args) != 0:
        topic = request.args.get('topic')
        if topic:
            return jsonify({
                "collabf": get("collabf", topic),
                "cosine": get("cosine", topic)
            })


@app.route("/description", methods=["GET"], strict_slashes=False)
def get_related_data():
    if len(request.args) != 0:
        topic = request.args.get('topic')
        if topic:
            return jsonify({
                "description": getDescription(topic)
            })


def question_list(topic, question_order):
    db_collection = conn[DB][AGGREGATE]
    cursor = db_collection.find({"Topic": topic})
    if question_order == 1:
        return  cursor.get("Score_Question_list")
    elif question_order == 2:
        return cursor.get("View_Question_list")
    elif question_order == 3:
        return cursor.get("Recent_Question_list")
    elif question_order == 4:
        return cursor.get("Bounty_Question_list")
    elif question_order == 5:
        return cursor.get("Most_Answer_Question_list")
    else:
        return [{"Question": "Error - Option not found."}]


@app.route("/recommendedQuestion", methods=["GET"], strict_slashes=False)
def get_question_list():
    if len(request.args) != 0:
        try:
            topic = request.args.get('topic')
            if topic:
                question_order = request.args.get('sortOrder')
                if question_order:
                    return jsonify({
                        "topic": topic,
                        "question": question_list(topic, question_order)
                    })
        except:
            print 'Error has occured when fetching the list of questions'



if __name__ == '__main__':
    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler

        file_handler = RotatingFileHandler(filename="app_debug.log")
        file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(file_handler)
    app.run(host='0.0.0.0', port=3000)
