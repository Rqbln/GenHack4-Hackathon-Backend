#!/bin/bash

# ============================================
# GenHack Climate - Deploy Cloud Run Job
# ============================================

set -e

PROJECT_ID="${PROJECT_ID:-genhack-heat-dev}"
REGION="${REGION:-europe-west1}"
JOB_NAME="heat-downscaling-pipeline"
IMAGE_TAG="${IMAGE_TAG:-latest}"
IMAGE_URL="europe-docker.pkg.dev/$PROJECT_ID/heat/gh-pipeline:$IMAGE_TAG"
SA_EMAIL="gh-pipeline-sa@$PROJECT_ID.iam.gserviceaccount.com"

echo "🚀 Deploying Cloud Run Job"
echo "=========================="
echo "Project: $PROJECT_ID"
echo "Region:  $REGION"
echo "Image:   $IMAGE_URL"
echo ""

# Verify current project
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
  echo "❌ Wrong project: $CURRENT_PROJECT (expected $PROJECT_ID)"
  echo "   Run: gcloud config set project $PROJECT_ID"
  exit 1
fi

# Check if job exists
if gcloud run jobs describe "$JOB_NAME" \
    --region="$REGION" \
    --project="$PROJECT_ID" &>/dev/null; then
  
  echo "📝 Job exists - updating..."
  gcloud run jobs update "$JOB_NAME" \
    --image="$IMAGE_URL" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --service-account="$SA_EMAIL" \
    --set-env-vars="PROJECT_ID=$PROJECT_ID,BUCKET_EXPORTS=gh-exports-$PROJECT_ID,BUCKET_CONFIGS=gh-configs-$PROJECT_ID" \
    --task-timeout=3600 \
    --max-retries=1 \
    --memory=4Gi \
    --cpu=2
  
  echo "✅ Job updated: $JOB_NAME"
  
else
  
  echo "🆕 Creating new job..."
  gcloud run jobs create "$JOB_NAME" \
    --image="$IMAGE_URL" \
    --region="$REGION" \
    --project="$PROJECT_ID" \
    --service-account="$SA_EMAIL" \
    --set-env-vars="PROJECT_ID=$PROJECT_ID,BUCKET_EXPORTS=gh-exports-$PROJECT_ID,BUCKET_CONFIGS=gh-configs-$PROJECT_ID" \
    --task-timeout=3600 \
    --max-retries=1 \
    --memory=4Gi \
    --cpu=2 \
    --args="--config,configs/paris_2022_mock.yml"
  
  echo "✅ Job created: $JOB_NAME"
fi

echo ""
echo "To execute the job:"
echo "  gcloud run jobs execute $JOB_NAME --region=$REGION"
echo ""
echo "To view logs:"
echo "  gcloud logging read \"resource.type=cloud_run_job AND resource.labels.job_name=$JOB_NAME\" --limit=50 --format=json"
