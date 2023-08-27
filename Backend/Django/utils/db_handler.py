from pymongo import MongoClient
from neo4j import GraphDatabase


def get_neo4j_driver():
    NEO4J_URI = "neo4j://localhost:7687"
    NEO4J_USER = "daniel"
    NEO4J_PASSWORD = "daniel1995"

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return driver

def get_recommend_faculty(university, professor, target_school):
    driver = get_neo4j_driver()
    DATABASE_NAME = "academicworld"
    query = f"MATCH (zilles:FACULTY {{name: '{professor}'}})-[:AFFILIATION_WITH]->(uiuc:INSTITUTE {{name: '{university}'}}), (cmu_faculty:FACULTY)-[:AFFILIATION_WITH]->(cmu:INSTITUTE {{name: '{target_school}'}}), path = shortestPath((zilles)-[:INTERESTED_IN*]-(cmu_faculty)) WITH path WHERE length(path) > 1 RETURN path LIMIT 5"
    with driver.session(database=DATABASE_NAME) as session:
        result = session.run(query)
        professors = []
        for record in result:
            path = record['path']
            end_node = path.end_node
            professor_name = end_node['name']
            professors.append(professor_name)
        return professors

def get_mangodb_handle(db_name, host, port, username, password):

    client = MongoClient(host=host,
                      port=int(port),
                      username=username,
                      password=password
                     )
    db_handle = client[db_name]
    return db_handle

def get_top10_faculty(university, keyword):
    # Set your MongoDB connection details
    db_name = "academicworld"
    host = "localhost"  # or your remote server address
    port = 27017  # or your custom port
    username = "daniel"
    password = "wert66"

    # Get a handle to the specified MongoDB database
    db_handle = get_mangodb_handle(db_name, host, port, username, password)

    result = db_handle.faculty.aggregate([
        { "$match": { "affiliation.name": university } },
        { "$unwind": "$publications" },
        {
            "$lookup": {
                "from": "publications",
                "localField": "publications",
                "foreignField": "id",
                "as": "publication_info"
            }
        },
        { "$unwind": "$publication_info" },
        { "$unwind": "$publication_info.keywords" },
        { "$match": { "publication_info.keywords.name": { "$eq": keyword } } },
        {
            "$project": {
                "name": "$name",
                "KRC": {
                    "$multiply": [
                        "$publication_info.keywords.score",
                        "$publication_info.numCitations"
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": "$name",
                "total_KRC": { "$sum": "$KRC" }
            }
        },
        {
            "$sort": {
                "total_KRC": -1
            }
        },
        {
            "$limit": 10
        },
        {
            "$project": {
                "_id": 0,
                "name": "$_id",
                "KRC": "$total_KRC"
            }
        }
    ])

    return result
