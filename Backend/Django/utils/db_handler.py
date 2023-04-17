from pymongo import MongoClient

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
