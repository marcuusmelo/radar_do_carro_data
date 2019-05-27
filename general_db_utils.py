import os
from shutil import move
import subprocess
import pymongo

from db_credentials import get_db_credentials
from general_file_management import check_if_folder_exists_than_crete

def get_heroku_db():
    username, password = get_db_credentials()
    connection_uri = 'mongodb://{0}:{1}@ds127983.mlab.com:27983/heroku_n7zq8f93'
    client = pymongo.MongoClient(connection_uri.format(username, password))
    client.admin.command('ismaster')
    heroku_db = client['heroku_n7zq8f93']

    return heroku_db


def load_file_then_move(upload_key, collection, move_files=True):
    """
    upload key will have the format:
    /Users/name/folder/20190421_adsource_upload/filename.csv
    """
    base_upload_command = 'mongoimport -h ds127983.mlab.com:27983 -d heroku_n7zq8f93 -c {0} -u {1} -p {2} --file {3} --type csv --headerline'
    loaded_key = upload_key.replace('upload', 'loaded')
    check_if_folder_exists_than_crete(os.path.dirname(loaded_key))

    username, password = get_db_credentials()

    upload_command_final = base_upload_command.format(collection, username, password, upload_key)
    subprocess.call(upload_command_final.split())

    if move_files:
        move(upload_key, loaded_key)

    return loaded_key


def remove_duplicates_from_collection(collection_name, target_field):
    heroku_db = get_heroku_db()

    cursor = heroku_db[collection_name].aggregate(
        [
            {"$group": {"_id": "$" + target_field, "unique_ids": {"$addToSet": "$_id"}, "count": {"$sum": 1}}},
            {"$match": {"count": { "$gte": 2 }}}
        ]
    )

    response = []
    for doc in cursor:
        del doc["unique_ids"][0]
        for id in doc["unique_ids"]:
            response.append(id)

    heroku_db[collection_name].remove({"_id": {"$in": response}})


def update_collection_and_drop_old(final_collection_name, new_collection_name, drop_old=True):
    heroku_db = get_heroku_db()

    old_collection = heroku_db[final_collection_name]
    old_collection.rename('old_' + final_collection_name)

    new_collection = heroku_db[new_collection_name]
    new_collection.rename(final_collection_name)

    if drop_old:
        heroku_db.drop_collection('old_' + final_collection_name)


def active_id_db_cleanup(target_collection, active_id_list):
    heroku_db = get_heroku_db()

    cursor = heroku_db[target_collection].find({'ad_id': {'$nin': active_id_list}})
    ids_to_remove = [x['_id'] for x in list(cursor)]

    heroku_db[target_collection].remove({"_id": {"$in": ids_to_remove}})


def repair_db():
    heroku_db = get_heroku_db()
    heroku_db.command('repairDatabase')
