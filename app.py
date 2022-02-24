import re
from flask import Flask, render_template, request
import youtubedb as ydt
#from src import viz
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame
matplotlib.use('Agg')

# Plot configurations
FIG_W = 10 # Width of plots
FIG_H = 5 # Height of plots
ROT = 0 # Rotation of x-axis labels
TS = 15 # Title size

def get_database():
    from pymongo import MongoClient
    import pymongo
    client = MongoClient('localhost', 27017)
    db = client.youtubedb.youtubedb

    print(db.count_documents({}))
    return db

dbname = get_database()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('layout.html')

@app.route('/select_video')
def select_video():
    '''This page returns search results, when a user hits the 'Search Video' button'''
    result_dictionary = request.args
    query = result_dictionary['query']
    rate = result_dictionary['rate']
    query_result = dbname.find({'category': query, 'rate': rate})

    return render_template(
        'select_video.html',
        query_result=query_result,
        query=query,
        rate = rate
    )

@app.route('/select_channels')
def select_channels():
    video = request.args['videoid']
    query_video = dbname.find_one({'videoID':video})

    related_videos = list(query_video.values())[-20:]
    image_names = [compare(video, related_videos, 'views'), compare(video, related_videos, 'rate')]
    df = tableCategory(video, related_videos)
    return render_template(
        'channels.html',
        image_names= image_names,
        table = df.to_html(index=False, classes='table-striped')
    )

def tableCategory(video, related_videos):
    item_details = dbname.find()
    items_df = DataFrame(item_details)
    values = [items_df.loc[items_df['videoID'] == video]['category'].iloc[0]]
    related_in_db = [video]
    for v in related_videos:
        if v in items_df['videoID'].tolist():
            related_in_db.append(v)
            value = items_df.loc[items_df['videoID'] == v]['category'].iloc[0]
            values.append(value)
    return pd.DataFrame({'related_videos':related_in_db, 'category':values})

def compare(video, related_videos, column_name):
    item_details = dbname.find()
    items_df = DataFrame(item_details)

    values_of_column_name = [items_df.loc[items_df['videoID'] == video][column_name].iloc[0]]
    related_in_db = [video]
    for v in related_videos:
        if v in items_df['videoID'].tolist():
            related_in_db.append(v)
            value = items_df.loc[items_df['videoID'] == v][column_name].iloc[0]
            values_of_column_name.append(value)

    image_name = f'static/images/{video}_barplot_video_{column_name}_comparation.png'
    video_df = pd.DataFrame({'related_videos':related_in_db, column_name: values_of_column_name})
    video_df[column_name] = video_df[column_name].astype(float)

    plt.figure(figsize=(FIG_W, FIG_H))
    video_df.plot.bar(x='related_videos', y=column_name)
    plt.xticks(rotation=ROT)
    plt.xlabel("Video Names")
    plt.ylabel("Video {column_name}")
    plt.title('{column_name} per Related Videos', fontdict = {'fontsize' : TS})
    plt.savefig(image_name, dpi=100)
    plt.close()
    return image_name
            

if __name__ == '__main__':
    app.debug = True
    app.run(port=3000, debug=True)
