from flask import Flask
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
@app.route('/api/news', methods=['GET'])
def get_news():
    data = pd.read_csv('./data/log.csv')
    data = data.sort_values(by=['time'],ascending=False).head(16)
    return data.to_json(orient='records', force_ascii=False)


if __name__ == '__main__':
    app.run(port=5000)