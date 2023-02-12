import aiml
import time
# import nltk
import random
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
import string
import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("homepage.html")

@app.route('/animelist')
def anilist():
    # return (tables=[data.to_html()], titles=[''])
    return render_template('animelist.html')

@app.route('/anibot')
def anibot():
    return render_template("chatbot.html")

def lowercase(x):
    return x.lower()

data = pd.read_csv("Anirec Indo.csv")

def filtertoken(x):
    stop_words = set(stopwords.words("indonesian"))
    word_tokens = word_tokenize(x)
    filtered_text = {word for word in word_tokens if word not in stop_words}
    return filtered_text

def jaccard(x, y):
    intersec = x.intersection(y)
    uni = x.union(y)
    similarity = len(intersec)/len(uni)
    return similarity

factory = StemmerFactory()
stemmer = factory.create_stemmer()

time.clock = time.time
kernel = aiml.Kernel()
kernel.learn("chat.aiml")

@app.route("/get")
def resp():
    userText = request.args.get('msg')
    userText = str(userText)
    input_teks = userText
    # start = time.time()
    #case folding
    input_teks = lowercase(input_teks)
    if 'anime mirip' in input_teks or 'anime yang mirip' in input_teks or 'anime seperti' in input_teks:
        respon = kernel.respond(input_teks)
        # stemming
        input_teks = stemmer.stem(input_teks)
        # print('stem')
        print(input_teks)
        # filtering dan tokenizing
        input_teks = filtertoken(input_teks)
        # print('filtering')
        print(input_teks)
        i = 0
        max_similarity = 0
        for row in data.iterrows():
            # print('masuk sini deh ehe')
            title = data.iloc[i]['Anime']
            title = lowercase(title)
            title = filtertoken(title)
            title_similarity = jaccard(input_teks, title)
            if max_similarity < title_similarity:
                max_similarity = title_similarity
                index = i
            i = i + 1
        print(index)
        inputdesc = data.iloc[index]['Description']
        inputdesc = lowercase(inputdesc)
        inputdesc = filtertoken(inputdesc)
        j=0
        resultrecommendation = ''
        print('jalan')
        # print(inputdesc)
        recom = []
        for row in data.iterrows():
            desc = data.iloc[j]['Description']
            desc = lowercase(desc)
            desc = filtertoken(desc)
            desc_similarity = jaccard(inputdesc, desc)
            # print(desc_similarity)
            if desc_similarity > 0.15:
                # print('kasjdbask')
                index1 = j
                if data.iloc[index1]['Anime'] == data.iloc[index]['Anime']:
                    j = j + 1
                    continue
                else:
                    recom.append(data.iloc[index1]['Anime'])
            j = j + 1
        # print(resultrecommendation)
        if recom != []:
            recommendation_respond = random.choices(recom, k=3)
            stringrespon = ''
            temp = ''
            for x in recommendation_respond:
                if stringrespon == '':
                    temp = x 
                    stringrespon = x
                if temp != x:
                    temp = x
                    stringrespon = stringrespon + ', ' + x
            # end = time.time()
            return str(respon +' '+ stringrespon)
        else:
            return str("Anime tidak ditemukan")
            # print(end-start)

    elif 'musim' in input_teks or 'genre' in input_teks or 'bergenre' in input_teks:
        print('masuk sisen ehe')
        respon = kernel.respond(input_teks)
        # stemming
        input_teks = stemmer.stem(input_teks)
        # filtering dan tokenizing
        input_teks = filtertoken(input_teks)
        i=0
        result = ''
        # print(input_teks)
        recom=[]
        for row in data.iterrows():
            # print('masuk sini boi')
            season = data.iloc[i]['Season']
            if pd.notna(season):
                season = lowercase(season)
                season = filtertoken(season)
                season_similarity = jaccard(input_teks, season)
                # print(season_similarity)
                if season_similarity >= 0.6:
                    genre = data.iloc[i]['Genres']
                    genre = lowercase(genre)
                    genre = word_tokenize(genre)
                    genre_similarity = jaccard(input_teks, genre)
                    print(genre_similarity)
                    if genre_similarity >= 0.1:
                        recom.append(data.iloc[i]['Anime'])
                i=i+1
            else :
                i=i+1
                continue
        recommendation_respond = []
        if recom != []:
            recommendation_respond = random.choices(recom, k=3)
            stringrespon = ''
            temp = ''
            for x in recommendation_respond:
                if stringrespon == '':
                    temp = x
                    stringrespon = x
                if temp != x:
                    temp = x
                    stringrespon = stringrespon + ', ' + x
            # end = time.time()
            return str(respon + ' ' +stringrespon)  
            # print(end-start) 
        else:
            # end = time.time()
            return str("Anime Tidak ditemukan")
            # print(end-start)

    elif 'judul' in input_teks or 'dari anime' in input_teks:
        respon = kernel.respond(input_teks)
        input_teks = lowercase(input_teks)
        input_teks = stemmer.stem(input_teks)
        input_teks = filtertoken(input_teks)
        # print(input_teks)
        i = 0
        result = ''
        max_similarity = 0
        index = -1
        for row in data.iterrows():
            chara = data.iloc[i]['Characters']
            if pd.notna(chara):
                chara = chara.translate(str.maketrans('', '', string.punctuation))
                chara = lowercase(chara)
                chara = filtertoken(chara)
                # print(chara)
                chara_similarity = jaccard(input_teks, chara)
                # print(chara_similarity)
                if max_similarity < chara_similarity:
                    max_similarity = chara_similarity
                    index = i
                i=i+1
            else:
                i=i+1
                continue
        if index != -1:
            anime = data.iloc[index]['Anime']
            # end = time.time()
            return str(respon + ' ' +anime)
            # print(end-start)
        else:
            # end = time.time()
            return str("Anime tidak ditemukan")
            # print(end-start)
    else:
        # end = time.time()
        return str('Saya tidak mengerti pertanyaan anda')
        # (end-start)

if __name__ == "__main__":
    app.run(debug=True)