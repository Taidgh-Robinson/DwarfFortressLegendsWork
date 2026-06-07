from collections import defaultdict

from sqlmodel import SQLModel

from db import engine, create_tables, get_session
from test import stream_legends_xml

import models.region
import models.underground_region
import models.dance_form
import models.musical_form
import models.site
import models.artifact
import models.historical_figure
import models.historical_event
import models.historical_event_collection
import models.historical_era
import models.written_content
import models.poetic_form
import models.entity
import models.entity_population


BATCH_SIZE = 1000


def main():
    print('Dropping existing tables...')
    SQLModel.metadata.drop_all(engine)

    print('Creating tables...')
    create_tables()

    print('Parsing XML...')
    results = stream_legends_xml('a.xml')
    print(f'Parsed {len(results)} objects')

    by_type = defaultdict(list)
    for r in results:
        by_type[type(r).__name__].append(r)

    with get_session() as session:
        for type_name, objects in by_type.items():
            print(f'Inserting {len(objects)} {type_name}...')
            for i in range(0, len(objects), BATCH_SIZE):
                batch = objects[i:i + BATCH_SIZE]
                session.add_all(batch)
                session.commit()

    print('Done')


if __name__ == '__main__':
    main()
