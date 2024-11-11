from django.core.exceptions import ValidationError



class UniqueFieldMixin:
    def clean_unique_field(self,field_name,model_class):
        data = self.cleaned_data.get(field_name)

         
        existing_objects = model_class.objects.exclude(id=self.instance.id)
        
        if existing_objects.filter(**{f"{field_name}__iexact": data}).exists():
            raise ValidationError(f'{field_name.replace("_", " ").capitalize()} already exists!')
        
        return data
    

class CompanyUniqueFieldMixin:
    def clean_unique_field(self,field_name,model_class):
        data = self.cleaned_data.get(field_name)
        
        
        existing_objects = model_class.objects.exclude(id=self.instance.id)
        
        if existing_objects.filter(**{f"{field_name}__iexact": data},company = self.instance.company).exists():
            raise ValidationError(f'{field_name.replace("_", " ").capitalize()} already exists!')
        
        return data


    """
        existing_objects.filter(**{f"{field_name}__iexact": data}) translates to

        existing_objects.filter(**{"packing_material__iexact": "Cardboard Box"}) translates to 

        existing_objects.filter(packing_material__iexact="Cardboard Box")

        in python we cannot use formatted string as keyword arguemnt  Instead,
        you need to use the ** unpacking operator with a dictionary to dynamically 
        create the keyword argument.

        The syntax f"{field_name}__iexact" = data tries to create a keyword argument where 
        the key is a dynamically generated string. Python does not allow dynamically created 
        strings to be used directly as keyword argument names in function calls(existing_objects.filter). Instead,
        Python expects keyword arguments to be known at the time of function definition.

        Correct Approach: Using ** for Dictionary Unpacking
        To dynamically create keyword arguments, you should use a dictionary and the ** 
          operator. This allows you to construct the dictionary keys dynamically.
        
    """

