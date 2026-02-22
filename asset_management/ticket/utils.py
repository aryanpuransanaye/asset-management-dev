from .models import Question

def get_question_config():

    filter_fields = []

    all_db_fields = [f.name for f in Question._meta.get_fields() if not f.many_to_many]
    sorting_fields = all_db_fields + [f'-{field}' for field in all_db_fields]

    search_fields = ['text']

    return {
        'filters': filter_fields,
        'sorting': sorting_fields,
        'search': search_fields
    }