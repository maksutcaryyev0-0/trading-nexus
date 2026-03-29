#!/bin/sh
# NEXUS nightly backup
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="/backups/nexus_${DATE}.sql.gz"

pg_dump -h postgres -U "$POSTGRES_USER" "$POSTGRES_DB" | gzip > "$BACKUP_FILE"
echo "Backup created: $BACKUP_FILE"

# Keep only last 7 days
find /backups -name "nexus_*.sql.gz" -mtime +7 -delete
echo "Old backups cleaned"

# Upload to S3 if configured
if [ -n "$BACKUP_S3_BUCKET" ] && [ -n "$AWS_ACCESS_KEY" ]; then
    aws s3 cp "$BACKUP_FILE" "s3://$BACKUP_S3_BUCKET/$(basename $BACKUP_FILE)"
    echo "Uploaded to S3"
fi
