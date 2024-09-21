from core.models import Company


def company_list(request):
    # Return a context dictionary with all companies
    return {'companies': Company.objects.all()}




"""
to add companies in base 

#custom context processor (in settings file)

'product.context_processors.company_list',

"""