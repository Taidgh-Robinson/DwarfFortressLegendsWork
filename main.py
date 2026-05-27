from lxml import etree

def main():
    parser = etree.XMLParser(recover=True)
    with open('a.xml', 'rb') as f:
        content = f.read().replace(b'encoding="UTF-8"', b'encoding="latin-1"')
        root = etree.fromstring(content, parser)

    for child in root:
        print(child.tag, len(child))

    events = root.find('historical_events')

    for event in list(events)[:5]:
        print('---')
        for child in event:
            print(f'  {child.tag}: {child.text}')



if __name__ == "__main__":
    main()
