import os
from dotenv import load_dotenv
from preprocess.preprocess import get_text_from, process_text
from preprocess.annotate import text_annotation
import tagme
import json
import nltk

# Initialise dependencies
tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer()

# Load env file
load_dotenv()
tagme.GCUBE_TOKEN = os.environ.get("GCUBE_TOKEN")

# Load blank schema for reference
with open("schema/schema.json", "r") as jsonFile:
    json_schema = json.load(jsonFile)

# html link for legislation
html_link = "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32019R0947&from=EN"
legal_text = get_text_from(html_link)

# Provides processed text (splits into introduction, recitals, articles,
# appendix etc)
processed_legal_text = process_text(legal_text)

# Add more structure to the blank schema
json_schema["document_data"] = {}
json_schema["document_data"]["uri"] = html_link
json_schema["document_data"]["sections"] = {}

# Keep track of articles. Temp setup until article number, name are extracted
# in helper functions.
article_count = 0
articles = []

# For entity extraction and linking.
# TODO: 1. Implement EuroVoc library for better extraction of concepts
#       2. Triple classification (subject, verb, object)
#       3. Rule classification
#       4. Ontology reference
#       5. Knowledge graph creation and shacl validation

for elem in processed_legal_text["order"]:
    if elem not in json_schema["document_data"]["sections"]:
        if elem == "articles":
            json_schema["document_data"]["sections"][elem] = []
        else:
            json_schema["document_data"]["sections"][elem] = {}
    for text in processed_legal_text[elem]:
        if elem == "articles":
            article_collection = {}
            article_count += 1
            article_collection["id"] = article_count
            article_collection["text"] = text
            article_collection["uri"] = ""
        sent_collection = []
        for sent in tokenizer.tokenize(text):
            temp_sent_data = {}
            temp_sent_data["text"] = sent
            temp_sent_data["sentence_rule"] = ""
            temp_concepts = text_annotation(sent, 0.2)
            temp_sent_data["concepts"] = temp_concepts
            sent_collection.append(temp_sent_data)
        if elem == "articles":
            article_collection["sentences"] = sent_collection
            articles.append(article_collection)
        if elem != "articles":
            json_schema["document_data"]["sections"][elem]["full_text"] = text
            json_schema["document_data"]["sections"][elem]["sentences"] = sent_collection
    if elem == "articles":
        json_schema["document_data"]["sections"][elem] = articles

# Save the file
with open("output/processed_data.json", "w", encoding="utf-8") as jsonFile:
    json.dump(json_schema, jsonFile, ensure_ascii=False, indent=4)
