def is_generator_empty(generator):
    generator = iter(generator)
    try:
        next(generator)
        return False  # Generator has at least one element
    except StopIteration:
        return True  # Generator is empty