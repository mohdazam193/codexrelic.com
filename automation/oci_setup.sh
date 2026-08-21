#!/bin/bash
set -e

echo "Starting OCI S3 Setup Automation..."

# Get the current user OCID from the OCI config
USER_OCID=$(grep -E "^user=" ~/.oci/config | cut -d'=' -f2 | tr -d ' ')
echo "User OCID: $USER_OCID"

# Get the namespace
NAMESPACE=$(oci os ns get | grep '"data"' | cut -d'"' -f4)
echo "Namespace: $NAMESPACE"

# Create the bucket (ignore error if it already exists)
echo "Creating bucket codexrelic-storage..."
oci os bucket create --name codexrelic-storage --namespace $NAMESPACE --compartment-id $USER_OCID || echo "Bucket already exists or creation failed, proceeding..."

# Generate a new Customer Secret Key for S3 compatibility
echo "Generating Customer Secret Key..."
KEY_NAME="codexrelic-api-key-$(date +%s)"
KEY_OUTPUT=$(oci iam customer-secret-key create --user-id $USER_OCID --display-name $KEY_NAME)

ACCESS_KEY=$(echo "$KEY_OUTPUT" | grep '"id"' | head -1 | cut -d'"' -f4)
SECRET_KEY=$(echo "$KEY_OUTPUT" | grep '"key"' | cut -d'"' -f4)

echo "Access Key: $ACCESS_KEY"
echo "Secret Key: $SECRET_KEY"

# Determine the region from config
REGION=$(grep -E "^region=" ~/.oci/config | cut -d'=' -f2 | tr -d ' ')
echo "Region: $REGION"

S3_ENDPOINT="https://${NAMESPACE}.compat.objectstorage.${REGION}.oraclecloud.com"

# Write everything to a .env.s3 file in the workspace
cat > /Users/azam.mohd/Desktop/codexrelic.com/.env.s3 <<EOF
# OCI Object Storage Credentials for S3 Compatibility
AWS_ACCESS_KEY_ID=$ACCESS_KEY
AWS_SECRET_ACCESS_KEY=$SECRET_KEY
AWS_ENDPOINT_URL_S3=$S3_ENDPOINT
AWS_DEFAULT_REGION=$REGION
AWS_S3_BUCKET=codexrelic-storage
EOF

echo "Setup complete! Credentials written to .env.s3"
