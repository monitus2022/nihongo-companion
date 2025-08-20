def file_name_to_id(filename: str) -> int:
    """Extract the model ID from the filename."""
    return int(filename.split('.')[0])
