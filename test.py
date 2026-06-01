from lxml import etree
from models.underground_region import UndergroundRegion
from models.region import Region
from models.dance_form import DanceForm
from models.musical_form import MusicalForm
"""
# Step 3: Insert straight into Postgres
with Session(engine) as session:
    session.add(region_model)
    session.commit()
"""

def stream_legends_xml(file_path):
    target_tags = ('site', 'historical_event', 'underground_region', 'region', 'dance_form', 'musical_form')
    
    # 'end' means it triggers when the parser hits the closing tag (e.g., </site>)
    context = etree.iterparse(file_path, events=('end',), tag=target_tags, recover=True)
    bleh = []
    for event, elem in context:
        tag_type = elem.tag 
        
        process_single_element(tag_type, elem, bleh)
        elem.clear()
        
        while elem.getprevious() is not None:
            del elem.getparent()[0]
            
    del context
    return bleh


def process_underground_region(elem):
    data_dict = {}
    for child in elem:
        if child.text is not None:
            cleaned_text = child.text.strip()
            if cleaned_text:
                data_dict[child.tag] = cleaned_text
    try:
        region_model = UndergroundRegion.model_validate(data_dict)
        return region_model
    except Exception as e:
        print(f"Skipping invalid region ID {data_dict.get('id')}. Error: {e}")
        return None

def process_region(elem):
    data_dict = {}
    for child in elem:
        if child.text is not None:
            cleaned_text = child.text.strip()
            if cleaned_text:
                data_dict[child.tag] = cleaned_text
    try:
        region_model = Region.model_validate(data_dict)
        return region_model
    except Exception as e:
        print(f"Skipping invalid region ID {data_dict.get('id')}. Error: {e}")
        return None


def process_dance_form(elem):
    data_dict = {}
    for child in elem:
        if child.text is not None:
            cleaned_text = child.text.strip()
            if cleaned_text:
                data_dict[child.tag] = cleaned_text
    try:
        dance_form_model = DanceForm.model_validate(data_dict)
        return dance_form_model
    except Exception as e:
        print(f"Skipping invalid region ID {data_dict.get('id')}. Error: {e}")
        return None

def process_musical_form(elem):
    data_dict = {}
    for child in elem:
        if child.text is not None:
            cleaned_text = child.text.strip()
            if cleaned_text:
                data_dict[child.tag] = cleaned_text
    try:
        dance_form_model = MusicalForm.model_validate(data_dict)
        return dance_form_model
    except Exception as e:
        print(f"Skipping invalid region ID {data_dict.get('id')}. Error: {e}")
        return None


def process_single_element(tag_type, elem, bleh):
    """Process a single entity at a time and push it straight to Postgres."""
    if tag_type == 'site':
        # Parse site, validate with Pydantic, save to DB
        pass
    elif tag_type == 'historical_event':
        # Parse chaotic event data, validate, save to DB
        pass
    elif tag_type == 'underground_region':
        region = process_underground_region(elem)
        if region is not None: 
            bleh.append(region)
    elif tag_type =='region':
        region = process_region(elem)
        if region is not None: 
            bleh.append(region)
    elif tag_type =='dance_form':
        region = process_dance_form(elem)
        if region is not None: 
            bleh.append(region)
    elif tag_type =='musical_form':
        region = process_musical_form(elem)
        if region is not None: 
            bleh.append(region)

bleh = stream_legends_xml('a.xml')
for b in bleh:
    print(type(b))