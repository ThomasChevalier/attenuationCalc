def header_indexes(header, fields):
    if header is None:
        raise RuntimeError("The CSV file is empty.")

    indexes = []
    for field in fields:
        if field in header:
            indexes.append(header.index(field))
        else:
            raise RuntimeError("Missing {} header.".format(field))
    return indexes
