import django.dispatch

obj_edit = django.dispatch.Signal(
    providing_args=["new_obj", "old_obj_dict", "new_obj_dict", "editor"])

obj_add = django.dispatch.Signal(
    providing_args=["obj", "obj_dict", "editor"])

obj_delete = django.dispatch.Signal(
    providing_args=["obj", "obj_dict", "editor"])
