import secrets
import zipfile
from flask import Flask, render_template, request, redirect, url_for, session
from app.helpers import parse_raw_data
from analysis import DataAnalyzer
from formatter_ import formatlist

app = Flask(__name__)

app.secret_key = secrets.token_hex(16)


@app.route('/')
def index():
    return render_template("index.html")

# upload's from index


@app.route('/', methods=['POST'])
def data_upload():
    file = request.files['file']
    # TODO: SETUP FILE EXCEPTIONS AND ERRORS

    zipfile_ = zipfile.ZipFile(file, "r")
    parsed_data = parse_raw_data(zipfile_)

    analyzer = DataAnalyzer(parsed_data)
    print(analyzer.content.no_of_pfp_changes())

    data = analyzer.export()
    session['analyzed_data'] = data # store the analyzer object in the session to access it in the dashboard
    return redirect(url_for('analysis'))


@app.route('/analysis')
def analysis():
    if 'Referer' not in request.headers or url_for('index') not in request.headers['Referer']:
       return redirect(url_for('index'))

    analyzed_data = session.get('analyzed_data', None) # retrieve the analyzer object from the session

    formatted_data = {
        ## ads, topics, and viewership
       'ad_view_freq': analyzed_data['ad_view_freq'],
       'account_based_in': analyzed_data['account_based_in'],
       'possible_phone_numbers': formatlist(analyzed_data['possible_phone_numbers']),
    }

    return render_template(
       template_name_or_list = "dashboard.html",
       **formatted_data
    )


# run app
app.run(
    debug=True
)
