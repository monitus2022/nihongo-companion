def remove_seperators_from_text(text: str) -> str:
    """
    Remove separators from the text.
    
    Args:
        text (str): The input text from which to remove separators.
    
    Returns:
        str: The text with separators removed.
    """
    return text.replace("\n", "").replace("\t", "")