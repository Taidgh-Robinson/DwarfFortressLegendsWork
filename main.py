from lxml import etree

from models.region import Region
from models.underground_region import UndergroundRegion

def cast_basic_items_to_models(items, model_type):
    models = []

    for region in list(items):
        temp_dict = {}
        
        for child in region:
            if child.text is not None:
                cleaned_text = child.text.strip()
                if cleaned_text: 
                    temp_dict[child.tag] = cleaned_text
            else:
                continue 

        try:
            temp_model = model_type.model_validate(temp_dict)
            models.append(temp_model)
        except Exception as e:
            print(f"Skipping an invalid region element. Error: {e}")
            print(f"Offending data dictionary: {temp_dict}")
    
    return models



def print_all_of_type(element_collection):
    for item in element_collection:
        print('--------')
        _print_recursive(item, indent_level=0)

def _print_recursive(element, indent_level):
    indent = "  " * indent_level
    
    for child in element:
        if len(child) > 0:
            print(f"{indent}{child.tag}:")
            _print_recursive(child, indent_level + 1)
        else:
            text = child.text.strip() if child.text else ""
            print(f"{indent}{child.tag} - {text}")

def main():
    parser = etree.XMLParser(recover=True)
    with open('a.xml', 'rb') as f:
        content = f.read().replace(b'encoding="UTF-8"', b'encoding="latin-1"')
        root = etree.fromstring(content, parser)

    tags = []
    for child in root:
        tags.append(child.tag)
        print(child.tag, len(child))

    print(tags)
    for tag in tags:
        print(tag)
        tmp = root.find(tag)
        print_all_of_type(tmp)

    regions = root.find('regions')

    region_models = cast_basic_items_to_models(regions, Region)
    print(region_models[0])
    ungerground_regions = root.find('underground_regions')

    underground_region_models = cast_basic_items_to_models(ungerground_regions, UndergroundRegion)
    print(underground_region_models[0])

    """
    sites = root.find('historical_eras')
    print_all_of_type(sites)
    """

if __name__ == "__main__":
    main()


