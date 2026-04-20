# AWS S3 And IAM Setup

This project uses S3 as the raw landing zone and Redshift `COPY` as the
warehouse load mechanism.

## S3 Bucket

Create one bucket for the project, for example:

```text
<your-prefix>-olist-modern-data-stack
```

Recommended raw layout:

```text
s3://<bucket>/olist/raw/<entity>/batch_date=<YYYY-MM-DD>/run_id=<run_id>/<entity>.csv.gz
```

Example:

```text
s3://<bucket>/olist/raw/orders/batch_date=2018-09-01/run_id=manual_2018_09_01/orders.csv.gz
```

## Redshift COPY Role

Create an IAM role that Redshift can assume and grant it read access to the
project bucket.

Minimum policy shape:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::<bucket>",
        "arn:aws:s3:::<bucket>/olist/*"
      ]
    }
  ]
}
```

Trust relationship service principal:

```text
redshift.amazonaws.com
```

For Redshift Serverless, attach the role to the workgroup. For provisioned
Redshift, associate the role with the cluster.

## Local AWS Credentials

Use an AWS profile or environment variables. Do not commit credentials.

Common local setup:

```powershell
aws configure --profile olist-modern-data-stack
```

Then set:

```text
AWS_PROFILE=olist-modern-data-stack
AWS_REGION=<region>
OLIST_S3_BUCKET=<bucket>
OLIST_S3_PREFIX=olist
REDSHIFT_COPY_IAM_ROLE_ARN=<role-arn>
```

## Cost Controls

- Keep only one learning bucket.
- Avoid storing unnecessary copies of prepared files.
- Pause or delete Redshift compute when not in use.
- Prefer small Redshift Serverless capacity while developing.
