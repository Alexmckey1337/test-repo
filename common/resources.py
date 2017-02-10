from import_export import resources


class CustomFieldsModelResource(resources.ModelResource):
    def get_export_order(self):
        if hasattr(self, 'custom_export_fields') and self.custom_export_fields:
            return [f for f in self.custom_export_fields if f in self.fields.keys()]
        return super(CustomFieldsModelResource, self).get_export_order()

    def export(self, queryset=None, *args, **kwargs):
        self.custom_export_fields = kwargs.get('custom_export_fields')
        return super(CustomFieldsModelResource, self).export(queryset=queryset, *args, **kwargs)
