#!/usr/bin/env python3


def update_model(instance, form):
    """
    Updates a Django model instance with data from a Pydantic model,
    considering only the fields that were explicitly set by the user.
    
    :param instance: The Django model instance to be updated.
    :param form: The validated Pydantic model with update data.
    :return: The updated Django model instance.
    """
    # Exclude fields that were not explicitly set (i.e., only update the fields that were passed)
    data = form.dict(exclude_unset=True)

    for field, value in data.items():
        setattr(instance, field, value)
    return instance


def check_form(Model, data):
    from pydantic import ValidationError # noqa
    try:
        form = Model(**data)
        return form, None
    except ValidationError as e:
        errors = e.errors()
        return None, errors
