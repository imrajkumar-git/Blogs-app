import blog.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="post",
            name="cover_image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=blog.models.blog_cover_path,
                validators=[blog.models.validate_cover_image],
            ),
        ),
    ]
