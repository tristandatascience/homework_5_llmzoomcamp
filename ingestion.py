if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

import io
import requests
import docx

def clean_line(line):
    line = line.strip()
    line = line.strip('\uFEFF')
    return line

def read_faq(file_id):
    url = f'https://docs.google.com/document/d/{file_id}/export?format=docx'
    
    response = requests.get(url)
    response.raise_for_status()
    
    with io.BytesIO(response.content) as f_in:
        doc = docx.Document(f_in)

    questions = []

    question_heading_style = 'heading 2'
    section_heading_style = 'heading 1'
    
    heading_id = ''
    section_title = ''
    question_title = ''
    answer_text_so_far = ''
     
    for p in doc.paragraphs:
        style = p.style.name.lower()
        p_text = clean_line(p.text)
    
        if len(p_text) == 0:
            continue
    
        if style == section_heading_style:
            section_title = p_text
            continue
    
        if style == question_heading_style:
            answer_text_so_far = answer_text_so_far.strip()
            if answer_text_so_far != '' and section_title != '' and question_title != '':
                questions.append({
                    'text': answer_text_so_far,
                    'section': section_title,
                    'question': question_title,
                })
                answer_text_so_far = ''
    
            question_title = p_text
            continue
        
        answer_text_so_far += '\n' + p_text
    
    answer_text_so_far = answer_text_so_far.strip()
    if answer_text_so_far != '' and section_title != '' and question_title != '':
        questions.append({
            'text': answer_text_so_far,
            'section': section_title,
            'question': question_title,
        })

    return questions

@data_loader
def load_data(*args, **kwargs):
    """
    Load FAQ data from Google Docs.

    Returns:
        List of dictionaries containing course and documents data.
    """
    faq_documents = {
        'llm-faq-v1': '1qZjwHkvP0lXHiE4zdbWyUXSVfmVGzougDD6N37bat3E',
    }
    documents = []

    for course, file_id in faq_documents.items():
        print(f"Loading data for course: {course}")
        course_documents = read_faq(file_id)
        documents.append({'course': course, 'documents': course_documents})

    print(f"Number of FAQ documents processed: {len(faq_documents)}")

    return documents


@test
def test_output(output, *args) -> None:
    """
    Test the output of the data loader.
    """
    assert output is not None, 'The output is undefined'
    assert isinstance(output, list), 'The output should be a list'
    assert len(output) > 0, 'The output list should not be empty'
    
    for item in output:
        assert 'course' in item, 'Each item should have a "course" key'
        assert 'documents' in item, 'Each item should have a "documents" key'
        assert isinstance(item['documents'], list), 'The "documents" value should be a list'
        
        for doc in item['documents']:
            assert 'text' in doc, 'Each document should have a "text" key'
            assert 'section' in doc, 'Each document should have a "section" key'
            assert 'question' in doc, 'Each document should have a "question" key'