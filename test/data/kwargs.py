result = function(
    foo,
    bar,
    **kwargs
)

result = function(
    foo,
    bar,
    **not_called_kwargs
)

result = function(
    foo,
    bar,
    **some.function_call_kwargs()
)

result = function(
    foo,
    bar,
    **[
        a_list,
        of,
        items,
    ]
)

result = function(
    foo,
    bar,
    **{
        'a_dict': {'with': 'a_dict'},
    }
)
