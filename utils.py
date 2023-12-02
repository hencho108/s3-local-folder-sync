class DotDict(dict):
    """
    A dictionary subclass that allows access to its elements
    using dot notation. Provides a way to access both top-level and
    nested dictionary values as if they were attributes.

    Example:
    ```
    my_dict = DotDict({'person': {'name': 'John', 'age': 30}})
    print(my_dict.person.name)  # Output: 'John'
    print(my_dict.person.age)   # Output: 30
    ```

    Note:
    DotDict is designed for dictionaries and nested dictionaries and may not
    handle other data types or edge cases.
    """

    def __getattr__(self, attr):
        if attr in self:
            value = self[attr]
            if isinstance(value, dict):
                return DotDict(value)
            return value
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{attr}'"
        )
