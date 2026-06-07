from typing import get_origin, get_args, Union

from lxml import etree

from models.underground_region import UndergroundRegion
from models.region import Region
from models.dance_form import DanceForm
from models.musical_form import MusicalForm
from models.site import Site
from models.artifact import Artifact
from models.historical_figure import HistoricalFigure
from models.historical_event import HistoricalEvent
from models.historical_event_collection import HistoricalEventCollection
from models.historical_era import HistoricalEra
from models.written_content import WrittenContent
from models.poetic_form import PoeticForm
from models.entity import Entity
from models.entity_population import EntityPopulation

TAG_TO_MODEL = {
    'region': Region,
    'underground_region': UndergroundRegion,
    'dance_form': DanceForm,
    'musical_form': MusicalForm,
    'site': Site,
    'artifact': Artifact,
    'historical_figure': HistoricalFigure,
    'historical_event': HistoricalEvent,
    'historical_event_collection': HistoricalEventCollection,
    'historical_era': HistoricalEra,
    'written_content': WrittenContent,
    'poetic_form': PoeticForm,
    'entity': Entity,
    'entity_population': EntityPopulation,
}

TAG_REMAP = {
    'return': 'return_',
    'honor': 'honors',
    'hf_link': 'hf_links',
    'entity_link': 'entity_links',
    'copied_artifact_id': 'copied_artifact_ids',
}


def coerce_text(text):
    if text is None:
        return None
    stripped = text.strip()
    return stripped if stripped else None


def process_element(model_class, elem):
    fields = model_class.model_fields
    children_by_tag = {}
    for child in elem:
        tag = child.tag
        if tag not in children_by_tag:
            children_by_tag[tag] = []
        children_by_tag[tag].append(child)

    data = {}
    for tag, children in children_by_tag.items():
        field_name = TAG_REMAP.get(tag, tag)
        if field_name not in fields:
            continue

        field_info = fields[field_name]
        origin = get_origin(field_info.annotation)
        args = get_args(field_info.annotation) if origin else None
        is_list = origin is list
        is_multiple = len(children) > 1

        if is_list:
            inner_type = args[0] if args else str
            if hasattr(inner_type, 'model_fields'):
                items = []
                if len(children) == 1 and len(children[0]) > 0:
                    for c in children[0]:
                        item = process_element(inner_type, c)
                        if item is not None:
                            items.append(item)
                else:
                    for c in children:
                        item = process_element(inner_type, c)
                        if item is not None:
                            items.append(item)
                data[field_name] = items
            else:
                items = []
                for c in children:
                    if len(c) > 0:
                        for sub in c:
                            text = coerce_text(sub.text)
                            if text is not None:
                                items.append(text)
                    else:
                        text = coerce_text(c.text)
                        if text is not None:
                            items.append(text)
                data[field_name] = items
            continue

        if hasattr(field_info.annotation, 'model_fields'):
            data[field_name] = process_element(field_info.annotation, children[0])
            continue

        if is_multiple:
            child = children[-1]
        else:
            child = children[0]

        text = coerce_text(child.text)
        if text is None:
            if origin is Union and type(None) in args:
                non_none_types = [a for a in args if a is not type(None)]
                if non_none_types and non_none_types[0] is bool:
                    data[field_name] = True
                else:
                    data.setdefault(field_name, None)
            continue

        if origin is Union and type(None) in args:
            non_none_types = [a for a in args if a is not type(None)]
            if non_none_types and non_none_types[0] is int and text == '-1':
                if field_name != 'id':
                    data[field_name] = None
                    continue

        data[field_name] = text

    if not data:
        return None

    try:
        return model_class.model_validate(data)
    except Exception as e:
        print(f"Skipping invalid {model_class.__name__} ID {data.get('id')}. Error: {e}")
        return None


def stream_legends_xml(file_path):
    target_tags = tuple(TAG_TO_MODEL.keys())

    context = etree.iterparse(file_path, events=('end',), tag=target_tags, recover=True)
    results = []
    for event, elem in context:
        tag_type = elem.tag

        model_class = TAG_TO_MODEL.get(tag_type)
        if model_class is None:
            elem.clear()
            while elem.getprevious() is not None:
                del elem.getparent()[0]
            continue

        model_instance = process_element(model_class, elem)
        if model_instance is not None:
            results.append(model_instance)

        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]

    del context
    return results


if __name__ == '__main__':
    results = stream_legends_xml('a.xml')
    counts = {}
    for r in results:
        cls = type(r).__name__
        counts[cls] = counts.get(cls, 0) + 1

    print(f'\nParsed {len(results)} total elements:')
    for cls, count in sorted(counts.items()):
        print(f'  {cls}: {count}')

    for r in results:
        print(r)