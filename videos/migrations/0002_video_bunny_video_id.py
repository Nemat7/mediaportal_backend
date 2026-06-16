from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='bunny_video_id',
            field=models.CharField(blank=True, max_length=100, verbose_name='Bunny Stream Video ID'),
        ),
    ]
