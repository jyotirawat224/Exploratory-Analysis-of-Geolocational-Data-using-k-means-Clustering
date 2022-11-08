from flask import Flask, render_template, url_for, request,redirect
import main

appy = Flask(__name__)



@appy.route('/', methods=['GET', 'POST'])
def home():
    if request.method=='POST':
        return redirect(url_for('predict'))
    else:
        return render_template('home.html')


@appy.route('/predict', methods=['POST'])
def predict():
    score = 0

    if request.method == 'POST':
        app_packages =[]
        data = {'latitude': "", 'longitude': '','city':''}
        lat = request.form['lat']
        long = request.form['long']
        city = request.form['city']
        #new = pd.DataFrame([data])
        #new_model = load_model('lr-model')
       # new = pd.DataFrame.from_records(new)
        #result = new_model.predict(new)
        map = main.classify(city,lat,long)

        # result=new_model.predict_classes(data)
        # print(len(result))
        return render_template('map.html',map = map)
    else:
        return render_template('map.html')

if __name__ == '__main__':
    appy.debug = True
    appy.run()