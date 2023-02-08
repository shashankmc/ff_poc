# TODO: Need to implement a proper class.
import tagme

def text_annotation(text, threshold):
    legal_annotations = tagme.annotate(text)
    concept_collection = []
    # Needs a minimum rho-score value which basically captures 
    # the confidence of entity linking, the higher the value, lesser the
    # results
    for ann in legal_annotations.get_annotations(threshold):
        temp_concept_dict = {}
        temp_concept_dict["concept"] = ann.entity_title
        temp_concept_dict["trigger"] = ann.mention
        temp_concept_dict["type"] = ""
        temp_concept_dict["start"] = ann.begin
        temp_concept_dict["end"] = ann.end
        temp_concept_dict["triple_classification"] = ""
        temp_concept_dict["uri"] = ann.uri()
        concept_collection.append(temp_concept_dict)
    return concept_collection 
