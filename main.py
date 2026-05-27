from lxml import etree

from models.region import Region

def cast_regions_to_models(regions):
    region_models = []

    for region in list(regions):
        temp_dict = {}
        
        for child in region:
            if child.text is not None:
                cleaned_text = child.text.strip()
                if cleaned_text: 
                    temp_dict[child.tag] = cleaned_text
            else:
                continue 

        try:
            temp_region = Region.model_validate(temp_dict)
            region_models.append(temp_region)
        except Exception as e:
            print(f"Skipping an invalid region element. Error: {e}")
            print(f"Offending data dictionary: {temp_dict}")
    
    return region_models

def print_all_of_type(type):
    for t in type:
        print('--------')
        for child in t:
            print(f'{child.tag} - {child.text}')


def main():
    parser = etree.XMLParser(recover=True)
    with open('a.xml', 'rb') as f:
        content = f.read().replace(b'encoding="UTF-8"', b'encoding="latin-1"')
        root = etree.fromstring(content, parser)

    for child in root:
        print(child.tag, len(child))

    regions = root.find('regions')

    region_models = cast_regions_to_models(regions)
    print(region_models[0])

    sites = root.find('historical_figures')
    #print_all_of_type(sites)

if __name__ == "__main__":
    main()


