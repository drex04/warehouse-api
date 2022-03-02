from flask import render_template
import config

app = config.conn_app
app.add_api('openapi-spec.yml')

@app.route('/')
def homepage():
    return render_template('homepage.html')
 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
