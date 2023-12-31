from sqlalchemy import Column, Float, MetaData, String, Table, create_engine


def write_deviation_results_to_sqlite(result):
    """
    Can write results of a classification computation towards a sqllite db
    It takes into consideration the requirements given in the assignment
    :param result: a list with a dict describing the result of a classification test
    """
    # In this function we use a native SQLAlchemy approach
    # Rather than using SQL syntax, I decided to use MetaData to describe the table and the columns
    # This data structure is used by SQLAlchemy to create the table
    engine = create_engine('sqlite:///{}.db'.format("output/mapping"), echo=False)
    metadata = MetaData()

    mapping = Table('mapping', metadata,
                    Column('X (test func)', Float, primary_key=False),
                    Column('Y (test func)', Float),
                    Column('Delta Y (test func)', Float),
                    Column('No. of ideal func', String(50))
                    )

    metadata.create_all(engine)

    # Rather than injecting the values line by line (which is slow)
    # I decided to use SQLAlchemy's .execute using a dict contain all the values
    # The creation of this dict is a simple mapping between the my internal data structures and
    # the structure which is required for the assignment

    execute_map = []
    for item in result:
        point = item["point"]
        classification = item["classification"]
        delta_y = item["delta_y"]

        # We need to test if there is a classification for a point at all and if so rename the function name to comply
        classification_name = None
        if classification is not None:
            classification_name = classification.name.replace("y", "N")
        else:
            # If there is no classification, there is also no distance. In that case I write a dash
            classification_name = "-"
            delta_y = -1

        execute_map.append(
            {"X (test func)": point["x"], "Y (test func)": point["y"], "Delta Y (test func)": delta_y,
             "No. of ideal func": classification_name})

    # using the Table object, the dict is used to insert the data
    i = mapping.insert().values(execute_map)
    with engine.connect() as connection:
        connection.execute(i.compile(connection))
        connection.commit()

    #i.execute(execute_map)