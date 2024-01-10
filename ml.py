import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import sys

#Reading the dataframe
df = pd.read_csv("reddit_data.csv")
df.drop(['utc'], inplace=True, axis=1)
username = sys.argv[0]
Nor = sys.argv[1]

users = df.username.unique().tolist()
subs = df.subreddit.unique().tolist()

dftot = df.groupby(['username','subreddit']).size().reset_index(name="tot_comments")
dfmax = dftot.groupby(['username'])['tot_comments'].max().reset_index(name="max_comments")
dfnew = pd.merge(dftot, dfmax, on='username', how='left')
dfnew['rating'] = dfnew['tot_comments']/dfnew['max_comments']*10

dfusers = df.drop_duplicates(subset='username')
dfusers.drop(['subreddit'], inplace=True, axis=1)
dfusers = dfusers.sort_values(['username'], ascending=True)
dfusers.reset_index(drop=True, inplace=True)
dfusers['user_id'] = dfusers.index+1
dfsubs = df.drop_duplicates(subset='subreddit')
dfsubs.drop(['username'], inplace=True, axis=1)
dfsubs = dfsubs.sort_values(['subreddit'], ascending=True)
dfsubs.reset_index(drop=True, inplace=True)
dfsubs['sub_id'] = dfsubs.index+1
dfnew = pd.merge(dfnew, dfusers, on='username', how='left')
move_pos = dfnew.pop('user_id')
dfnew.insert(1, 'user_id', move_pos)
dfnew = pd.merge(dfnew, dfsubs, on='subreddit', how='left')
move_pos = dfnew.pop('sub_id')
dfnew.insert(3, 'sub_id', move_pos)

dfnum = dfnew
dfnew.drop(['username','subreddit','tot_comments','max_comments'], inplace=True, axis=1)
dfrat = dfnum.pivot(index='sub_id', columns='user_id', values='rating')
dfrat.fillna(0,inplace=True)

num_users = dfnum.groupby('sub_id')['rating'].agg('count')
num_subs = dfnum.groupby('user_id')['rating'].agg('count')

dflast = dfrat.loc[num_users[num_users > 100].index,:]
dflast = dflast.loc[:,num_subs[num_subs > 10].index]
csr_data = csr_matrix(dflast.values)
dflast.reset_index(inplace=True)

knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=20, n_jobs=-1)
knn.fit(csr_data)

def subreddit_recommender(username, Nor):
    sub_list = dfsubs[dfsubs['subreddit'].str.contains(username)]
    if len(sub_list):
        sub_idx = sub_list.iloc[0]['sub_id']
        sub_idx = dflast[dflast['sub_id'] == sub_idx].index[0]
        distances, indices = knn.kneighbors(csr_data[sub_idx], n_neighbors=Nor+1)
        rec_sub_indices = sorted(list(zip(indices.squeeze().tolist(), distances.squeeze().tolist())), key=lambda x: x[1])[:0:-1]
        recommend_frame = []
        for val in rec_sub_indices:
            sub_idx = dflast.iloc[val[0]]['sub_id']
            subreddit = dfsubs[dfsubs['sub_id'] == sub_idx]['subreddit'].tolist()[0]
            recommend_frame.append(subreddit)
        return recommend_frame
    else:
        return "No subreddits found. Please check the subreddit name and try again."

result = subreddit_recommender(username, Nor)
print(result)