import os
def youtubeSearchListStatistics(q=None, maxResults=10):
    '''Get video search results for a query. Returns advanced statistics such as counts forlikes, dislikes, views and comments. Return a json file.'''

    query_result = youtubeSearchList(q=q, maxResults=maxResults)

    # Create a list of video ids
    video_id_list = [x['id']['videoId'] for x in query_result['items']]

    snippets = video_snippets(youtube, video_id_list, maxResults=10, part="statistics")
    assert len(query_result['items']) == len(snippets), 'Query result length does not match statistics length.'

    counter = 0
    for i in query_result['items']:
        i['statistics'] = snippets[counter]['statistics']
        counter += 1

    return query_result

def get_database():
    from pymongo import MongoClient
    import pymongo
    client = MongoClient('localhost', 27017)
    db = client.youtubedb.youtubedb

    print(db.count_documents({}))
    return db
    
# This is added so that many files can reuse the function get_database()
if __name__ == "__main__":    
    
    # Get the database
    dbname = get_database()