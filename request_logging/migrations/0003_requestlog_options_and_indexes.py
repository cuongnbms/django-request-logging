from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("request_logging", "0002_remove_requestlog_user_agent_requestlog_headers"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="requestlog",
            options={"ordering": ["-request_at"]},
        ),
        migrations.AddIndex(
            model_name="requestlog",
            index=models.Index(fields=["request_at"], name="request_log_request_at_idx"),
        ),
        migrations.AddIndex(
            model_name="requestlog",
            index=models.Index(fields=["client_ip"], name="request_log_client_ip_idx"),
        ),
        migrations.AddIndex(
            model_name="requestlog",
            index=models.Index(fields=["response_code"], name="request_log_resp_code_idx"),
        ),
    ]
