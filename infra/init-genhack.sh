#!/bin/bash

# ============================================
# GenHack Climate - Infrastructure Init
# ============================================
# Idempotent script - safe to run multiple times
# Based on Phase 0 setup (genhack-duplication/)

set -e

PROJECT_ID="genhack-heat-dev"
REGION="europe-west1"
REGISTRY_LOCATION="europe"
REGISTRY_NAME="heat"

echo "🔧 GenHack Infrastructure Initialization"
echo "========================================"
echo ""

# Verify current project
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
  echo "⚠️  Current project: $CURRENT_PROJECT"
  echo "   Switching to: $PROJECT_ID"
  gcloud config set project "$PROJECT_ID"
fi

echo "✅ Project: $PROJECT_ID"
echo ""

# Check if already initialized
if gsutil ls -p "$PROJECT_ID" "gs://gh-exports-$PROJECT_ID" &>/dev/null; then
  echo "✅ Infrastructure already initialized"
  echo "   (Buckets exist, skipping creation)"
  echo ""
  echo "To verify setup, run:"
  echo "   gsutil ls -p $PROJECT_ID"
  echo "   gcloud artifacts repositories list --location=$REGISTRY_LOCATION"
  exit 0
fi

echo "🔨 Creating resources..."
echo ""

# Enable APIs (idempotent)
echo "Enabling APIs..."
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  storage.googleapis.com \
  cloudkms.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  cloudbuild.googleapis.com \
  eventarc.googleapis.com \
  cloudscheduler.googleapis.com \
  compute.googleapis.com \
  --project="$PROJECT_ID" \
  2>/dev/null || echo "   APIs already enabled"

echo "✅ APIs enabled"
echo ""

# Check KMS (created in Phase 0)
echo "Checking KMS..."
if gcloud kms keyrings describe gh-ring \
    --location="$REGION" \
    --project="$PROJECT_ID" &>/dev/null; then
  echo "✅ KMS keyring 'gh-ring' exists"
else
  echo "❌ KMS keyring 'gh-ring' not found"
  echo "   Run Phase 0 setup first:"
  echo "   cd ../genhack-duplication && ./scripts/phase0_setup_infrastructure.sh"
  exit 1
fi
echo ""

# Check Artifact Registry (created in Phase 0)
echo "Checking Artifact Registry..."
if gcloud artifacts repositories describe "$REGISTRY_NAME" \
    --location="$REGISTRY_LOCATION" \
    --project="$PROJECT_ID" &>/dev/null; then
  echo "✅ Artifact Registry '$REGISTRY_NAME' exists"
else
  echo "❌ Artifact Registry not found"
  echo "   Run Phase 0 setup first"
  exit 1
fi
echo ""

# Check Service Account (created in Phase 0)
echo "Checking Service Account..."
SA_EMAIL="gh-pipeline-sa@$PROJECT_ID.iam.gserviceaccount.com"
if gcloud iam service-accounts describe "$SA_EMAIL" \
    --project="$PROJECT_ID" &>/dev/null; then
  echo "✅ Service account: $SA_EMAIL"
else
  echo "❌ Service account not found"
  echo "   Run Phase 0 setup first"
  exit 1
fi
echo ""

# Check buckets (created in Phase 0)
echo "Checking GCS buckets..."
BUCKET_COUNT=$(gsutil ls -p "$PROJECT_ID" | grep "gh-" | wc -l | tr -d ' ')
if [ "$BUCKET_COUNT" -ge 11 ]; then
  echo "✅ Found $BUCKET_COUNT buckets with 'gh-' prefix"
else
  echo "❌ Expected 11 buckets, found $BUCKET_COUNT"
  echo "   Run Phase 0 setup first"
  exit 1
fi
echo ""

echo "============================================"
echo "✅ Infrastructure Check Complete"
echo "============================================"
echo ""
echo "Ready for Phase 1 deployment!"
echo ""
echo "Next steps:"
echo "  1. Build Docker image:   make build"
echo "  2. Deploy Cloud Run Job: make deploy"
echo "  3. Run pipeline:         make run"
