def priority_filter(queryset, params):
    query = params.get('priority')
    if query:
        return queryset.filter(priority__iexact=query)
    return queryset

def search_filter_project(queryset, params):
    query = params.get('search')
    if query:
        if queryset.model.__name__ == 'Project':
            return queryset.filter(title__icontains=query)
    return queryset

def search_filter_task(queryset, params):
    query = params.get('search')
    if query:
        return queryset.filter(title__icontains=query)
    return queryset