import hashlib

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

def generate_document_id(doc):
    combined = f"{doc['course']}-{doc['question']}-{doc['text'][:10]}"
    hash_object = hashlib.md5(combined.encode())
    hash_hex = hash_object.hexdigest()
    document_id = hash_hex[:8]
    return document_id

@transformer
def transform(data, *args, **kwargs):
    print("type data", type(data))
    documents = []
    for doc in data['documents']:  # Accédez directement à la liste 'documents'
        doc['course'] = data['course']  # Accédez au nom du cours depuis data
        doc['document_id'] = generate_document_id(doc)
        documents.append(doc)
    
    print(f"Number of documents: {len(documents)}")
    print("doc 0 =>", documents[0])
    return documents

@test
def test_output(output, *args) -> None:
    """
    Test the output of the transform block.
    """
    assert output is not None, 'The output is undefined'
    assert isinstance(output, list), 'The output should be a list'
    assert len(output) > 0, 'The output list should not be empty'

    for doc in output:
        assert 'course' in doc, 'Each document should have a "course" key'
        assert 'document_id' in doc, 'Each document should have a "document_id" key'
        assert 'text' in doc, 'Each document should have a "text" key'
        assert 'section' in doc, 'Each document should have a "section" key'
        assert 'question' in doc, 'Each document should have a "question" key'