from pyairtable import Api, Base, Table
from time import sleep
import requests
import json

airtable_api_key = ''
base_id = ""
table_name = ""



def check_text_for_grammar_mistakes(text, api_url, api_key=None, username=None, language="en-US"):
    payload = {
        "text": text,
        "language": language,
        "apiKey": api_key,
        "username": username
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(api_url, data=payload, headers=headers)

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        raise ValueError(f"API call failed with status code {response.status_code}: {response.text}")

# languagetool vars
api_url = "https://api.languagetoolplus.com/v2/check"
api_key = ""
username = ""



table = Table(airtable_api_key, base_id, table_name)

formula = "AND({LanguageToolFeedback} = '')"

filtered_table = table.all(formula=formula)


for records in table.iterate(page_size=1, max_records=90, formula=formula):
    feedback_dict_list = []
    checked_text = check_text_for_grammar_mistakes(records[0]['fields']['Main Content'], api_url, api_key, username)
    matches = checked_text['matches']
    for match in matches:
        feedback_dict = {}
        message = match['message']
        shortMessage = match['shortMessage']
        sentence = match['sentence']
        prompt_message = f"Message: {message}\nShort Message: {shortMessage}\nSentence: {sentence}\n"
        feedback_dict['feedback'] = prompt_message
        feedback_dict_list.append(feedback_dict)
    table.update(records[0]['id'], {"LanguageToolFeedback": str(feedback_dict_list)})

