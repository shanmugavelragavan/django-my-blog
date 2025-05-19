from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction

def create_groups_permissions(sender, **kwargs):
    try:
        with transaction.atomic():
            # create groups
            readers_group, _ = Group.objects.get_or_create(name="Readers")
            authors_group, _ = Group.objects.get_or_create(name="Authors")
            editors_group, _ = Group.objects.get_or_create(name="Editors")

            # get post content type
            post_content_type = ContentType.objects.get(app_label='blog', model='post')

            # create permissions
            readers_permissions = [
                Permission.objects.get(codename="view_post", content_type=post_content_type)
            ]

            authors_permissions = [
                Permission.objects.get(codename="view_post", content_type=post_content_type),
                Permission.objects.get(codename="add_post", content_type=post_content_type),
                Permission.objects.get(codename="change_post", content_type=post_content_type),
                Permission.objects.get(codename="delete_post", content_type=post_content_type),
            ]

            can_publish, _ = Permission.objects.get_or_create(
                codename="can_publish",
                content_type=post_content_type,
                name="Can Publish Post"
            )

            editors_permissions = [
                Permission.objects.get(codename="view_post", content_type=post_content_type),
                can_publish,
                Permission.objects.get(codename="add_post", content_type=post_content_type),
                Permission.objects.get(codename="change_post", content_type=post_content_type),
                Permission.objects.get(codename="delete_post", content_type=post_content_type),
            ]

            # assigning the permissions to groups
            readers_group.permissions.set(readers_permissions)
            authors_group.permissions.set(authors_permissions)
            editors_group.permissions.set(editors_permissions)
            print("Groups and Permissions created successfully")
    except Exception as e:
        print(f"An error occurred: {e}")
