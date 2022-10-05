import json
import networkx as nx
import matplotlib.pyplot as plt
import io
import pydotplus
from IPython.display import display, Image
from rdflib.tools.rdf2dot import rdf2dot
from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import XSD, OWL, RDF, RDFS, FOAF
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
from urllib.parse import quote
from jsonpath_ng import jsonpath, parse

def visualize(g):
    stream = io.StringIO()
    rdf2dot(g, stream, opts={display})
    dg = pydotplus.graph_from_dot_data(stream.getvalue())
    dg.write_png('document_graph.png')
    # png = dg.create_png()
    # display(Image(png))

with open('./json_work_in_progress.json','r') as f:
    json_data = json.load(f)

# Things to do:
# 1. Identify subject, predicate, object with their URIs to create a graph.
# 2. Validate the data being inserted into the graph using SHACL.
# 3. Create a hierarchy where we take article first, with it's URI and then
# link that to the SPO detected.
document_expression = parse('document')
g = Graph()
schema = Namespace('http://schema.org/')
n = Namespace('http://example.com/test#')
wiki = Namespace('https://en.wikipedia.org/wiki/')
schema_name = schema + 'name'
# Document is an object.
# Properties - name (hasName), language (isInLanguage), domain (forDomain),
# published (publishedOn), region (applicableForRegion), revised (isRevised),
# amended (isAmended), title (subclassOf) 
for match in document_expression.find(json_data):
    document_uri = URIRef(match.value['uri'])
    g.add((document_uri, RDF.type, URIRef(n + 'Document')))
    g.add((document_uri, URIRef(schema_name), Literal(match.value['name'],\
            datatype=XSD.string)))
    g.add((document_uri, URIRef(schema + 'language'),
           Literal(match.value['language'], datatype=XSD.string)))
    g.add((document_uri, URIRef(schema + 'domain'),
           Literal(match.value['domain'], datatype=XSD.string)))
    g.add((document_uri, URIRef(schema + 'publishedDate'),
           Literal(match.value['published_date'], datatype=XSD.date)))
    g.add((document_uri, URIRef(schema + 'region'),
           Literal(match.value['region'], datatype=XSD.string)))
    g.add((document_uri, URIRef(schema + 'revised'),
           Literal(match.value['revised'], datatype=XSD.boolean)))
    g.add((document_uri, URIRef(schema + 'amended'),
           Literal(match.value['amended'], datatype=XSD.boolean)))

# Adding triples for titles, sections, articles, concepts
for match in parse('title').find(json_data):
    title_uri = URIRef(match.value['uri'])
    g.add((title_uri, RDFS.subClassOf, document_uri))
    g.add((title_uri, RDF.type, URIRef(n + 'Document_Title')))
    g.add((title_uri, URIRef(schema_name), Literal(match.value['name'],
                                                        datatype=XSD.string)))
    for section in match.value['sections']:
        section_uri = URIRef(section['uri'])
        g.add((section_uri, RDFS.subClassOf, title_uri))
        g.add((section_uri, RDF.type, URIRef(n + 'Document_Section')))
        g.add((section_uri, URIRef(schema_name), Literal(section['name'],
                                                             datatype=XSD.string)))
        g.add((section_uri, URIRef(schema + 'description'), Literal(section['text'],
                                                                    datatype=XSD.string)))
        for article in section['articles']:
            article_uri = URIRef(article['uri'])
            g.add((article_uri, RDFS.subClassOf, section_uri))
            g.add((article_uri, URIRef(schema_name),
                   Literal(article['name'], datatype=XSD.string)))
            g.add((article_uri, URIRef(schema + 'description'),
                   Literal(article['text'], datatype=XSD.string)))
            for sentence in article['sentences']:
                sentence_uri = URIRef(n + 'sentence')
                g.add((sentence_uri, RDFS.subClassOf, article_uri))
                g.add((sentence_uri, RDF.type, URIRef(wiki +
                                                      'Sentence_(linguistics)')))
                g.add((sentence_uri, URIRef(schema + 'text'),
                       Literal(sentence['text'], datatype=XSD.string)))
                g.add((sentence_uri, URIRef(schema + 'sentenceRule'),
                       Literal(sentence['sentence_rule'], datatype=XSD.string)))
                for concept in sentence['concepts']:
                    concept_uri = URIRef(concept['uri'])
                    g.add((concept_uri, RDFS.subClassOf, sentence_uri))
                    g.add((concept_uri, URIRef(schema + 'category'),
                          Literal(concept['type'], datatype=XSD.string)))
                    g.add((concept_uri, URIRef(schema + 'concept'),
                          Literal(concept['concept'], datatype=XSD.string)))
                    if concept['triple_classification'].lower() == 'subject':
                        g.add((concept_uri, RDF.type, RDF.subject))
                    elif concept['triple_classification'].lower() == 'verb':
                        g.add((concept_uri, RDF.type, RDF.predicate))
                    else:
                        g.add((concept_uri, RDF.type, RDF.object))
final_ttl = g.serialize(format='turtle')
print(final_ttl)
visualize(g)
# Visualise the graph
# G = rdflib_to_networkx_multidigraph(final_ttl)
# pos = nx.spring_layout(G, scale=2)
# edge_labels = nx.get_edge_attributes(G, 'r')
# nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
# nx.draw(G, with_labels=True)
# 
# plt.show()


