from flask import Flask, render_template, request
import facebook as fb

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        page_id = request.form['page_id']
        token = request.form['token']
        
        graph = fb.GraphAPI(access_token=token, version="3.1")
        
        try:
            response = graph.request(f'{page_id}?fields=posts{{id,message,created_time,comments{{id,message,created_time,from}}}}')
            
            posts_data = response.get('posts', {}).get('data', [])
            
            return render_template('results.html', posts=posts_data)
        except fb.GraphAPIError as e:
            error = f"Ocurrió un error: {e}"
            return render_template('index.html', error=error)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)