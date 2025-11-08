# 🔗 GenHack4 - Quick Links

## GitHub
- **Repository**: https://github.com/Rqbln/GenHack4-Hackathon-Vertex
- **Actions/CI**: https://github.com/Rqbln/GenHack4-Hackathon-Vertex/actions
- **Issues**: https://github.com/Rqbln/GenHack4-Hackathon-Vertex/issues

## Google Cloud Platform

### Project: genhack-heat-dev
- **Console**: https://console.cloud.google.com/?project=genhack-heat-dev
- **Cloud Run Jobs**: https://console.cloud.google.com/run/jobs?project=genhack-heat-dev
- **Artifact Registry**: https://console.cloud.google.com/artifacts/docker/genhack-heat-dev/europe/heat
- **Cloud Storage**: https://console.cloud.google.com/storage/browser?project=genhack-heat-dev
- **Logs Explorer**: https://console.cloud.google.com/logs/query?project=genhack-heat-dev
- **Cloud KMS**: https://console.cloud.google.com/security/kms?project=genhack-heat-dev
- **IAM**: https://console.cloud.google.com/iam-admin/iam?project=genhack-heat-dev

### Deployed Resources
- **Job**: `heat-downscaling-pipeline`
- **Image**: `europe-docker.pkg.dev/genhack-heat-dev/heat/gh-pipeline:latest`
- **Service Account**: `gh-pipeline-sa@genhack-heat-dev.iam.gserviceaccount.com`
- **KMS Key**: `projects/genhack-heat-dev/locations/europe-west1/keyRings/gh-ring/cryptoKeys/gh-key`

## Quick Commands

### Execute Pipeline
```bash
gcloud run jobs execute heat-downscaling-pipeline --region=europe-west1 --wait
```

### View Recent Logs
```bash
gcloud logging read "resource.type=cloud_run_job AND resource.labels.job_name=heat-downscaling-pipeline" --limit=50 --format=json
```

### List All Buckets
```bash
gsutil ls | grep gh-
```

### Check Docker Image
```bash
gcloud artifacts docker images list europe-docker.pkg.dev/genhack-heat-dev/heat
```

### Update Job
```bash
gcloud run jobs update heat-downscaling-pipeline --image=europe-docker.pkg.dev/genhack-heat-dev/heat/gh-pipeline:latest --region=europe-west1
```

## Local Development

### Clone Repository
```bash
git clone git@github.com:Rqbln/GenHack4-Hackathon-Vertex.git
cd GenHack4-Hackathon-Vertex
```

### Setup
```bash
make init
```

### Build & Test
```bash
make build
make test
make dryrun
```

### Deploy
```bash
make deploy
make run
make logs
```

## Documentation

- [README.md](README.md) - Main documentation
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment summary
- [docs/ARCHITECTURE_CLIMATE.md](docs/ARCHITECTURE_CLIMATE.md) - System architecture
- [docs/SCHEMAS.md](docs/SCHEMAS.md) - Data contracts
- [docs/REPRODUCE.md](docs/REPRODUCE.md) - Step-by-step guide
- [docs/setup/PHASE0_COMPLETE.md](docs/setup/PHASE0_COMPLETE.md) - Infrastructure setup

## Support

For issues or questions:
1. Check [DEPLOYMENT.md](DEPLOYMENT.md) for troubleshooting
2. Review logs in GCP Console
3. Open an issue on GitHub
4. Check [docs/REPRODUCE.md](docs/REPRODUCE.md) for detailed steps

---

**Last Updated**: November 8, 2025  
**Version**: 1.0.0 (Phase 1)
