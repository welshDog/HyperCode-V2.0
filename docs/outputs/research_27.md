# 🧠 HyperCode Output: RESEARCH

# 1. Executive Summary
**'Test MinIO Upload 2'** refers to testing and implementing file upload workflows to MinIO, an S3-compatible object storage system. Recent developments (2024-2026) emphasize cURL-based pre-signed URL uploads, MinIO Client (mc) commands, and SDK integrations for reliable testing. Best practices include authentication via pre-signed URLs, multipart handling for large files (>5GB), and automation scripts. Actionable insight: Use pre-signed URLs for secure, temporary upload testing without exposing credentials[1][2].

# 2. Key Concepts & Definitions
- **MinIO**: High-performance, open-source object storage fully compatible with AWS S3 API; supports encryption, replication, and cloud-native deployments[1][5].
- **Pre-signed URLs**: Temporary, secure links for direct uploads/downloads to MinIO buckets without SDKs; generated via mc or SDKs, expire after set time (e.g., 2h)[1].
- **MinIO Client (mc)**: CLI tool for bucket/object management; aliases simplify endpoint/access config (e.g., `mc alias set myminio http://localhost:9000 ACCESS SECRET`)[1][2].
- **Multipart Uploads**: Required for files >5GB; splits uploads into parts for resumability and efficiency[1].
- **Bucket Policies**: JSON-defined permissions (e.g., allow PutObject/GetObject on `arn:aws:s3:::my-bucket/*`)[2].
- **Recent Context (2026)**: Original MinIO repo entered "no longer maintained" status; community forks emerged, but core S3 compatibility persists[6][7].

# 3. Code Examples or Architectural Patterns
## Basic mc Upload Test (Single File/Directory)
```
# Configure alias
mc alias set myminio http://localhost:9000 YOUR-ACCESS YOUR-SECRET

# Create bucket
mc mb myminio/my-bucket

# Test upload single file
mc cp ./test-file.txt myminio/my-bucket/

# Test recursive directory upload
mc cp --recursive ./test-dir/ myminio/my-bucket/
```
Verify: `mc ls myminio/my-bucket`[1][2].

## cURL Pre-signed URL Upload (Automation Pattern)
1. Generate URL: `mc share upload myminio/my-bucket/test.txt --expire 2h --json | jq -r .url`
2. Upload: `curl -X PUT --upload-file ./test.txt --fail "${URL}"`
Full Bash script for repeatable testing[1]:
```
#!/bin/bash
set -euo pipefail
MINIO_ALIAS="myminio"; BUCKET="mybucket"; EXPIRY="2h"; FILE="test.txt"
mc alias set $MINIO_ALIAS http://localhost:9000 ACCESS SECRET
URL=$(mc share upload $MINIO_ALIAS/$BUCKET/$FILE --expire $EXPIRY --json | jq -r .url)
curl -X PUT --upload-file $FILE --progress-bar "$URL" && echo "Upload test passed"
```

## Node.js SDK Test Pattern (2024 Compatible)
```
const Minio = require('minio');
const client = new Minio.Client({ endPoint: 'localhost', port: 9000, useSSL: false, accessKey: 'ACCESS', secretKey: 'SECRET' });
const url = await client.presignedPutObject('mybucket', 'test.txt', 7200); // 2h expiry
// Use cURL or fetch to PUT test.txt to $url
```
For large files: Use `client.fPutObject` with multipart options[1][2].

**Pattern**: Alias setup → Bucket create → Pre-sign → cURL PUT → Verify list.

# 4. Pros & Cons
| Aspect | Pros | Cons |
|--------|------|------|
| **cURL/mc Testing** | Simple CLI; no code deps; progress tracking; works offline[1][2][4] | Manual expiry management; less error-handling than SDKs |
| **Pre-signed URLs** | Secure (no creds exposed); temporary access; S3-standard[1] | URL expiry limits long tests; regeneration overhead |
| **MinIO Overall** | S3-compatible; high perf; multi-platform[1][5] | 2026 maintenance issues (forks needed); file count limits in some FS[7][9] |
| **Large Files** | Multipart resumable; `mc mirror` syncs dirs[1] | >5GB requires special handling; network timeouts possible |

# 5. References or Further Reading
- [1] Transloadit cURL Guide (2024): Full automation scripts, versions (MinIO RELEASE.2024-02-09T21-25-16Z).
- [2] OneUptime Setup Guide (2026): mc commands, SDKs (Node.js/Python/Go), policies.
- [5] MinIO GitHub: Official docs for builds/deployments.
- [6][7] Community forks post-2026 repo changes.
- Explore: MinIO docs for latest forks; test with `mc` on localhost:9000.

---
**Archived in MinIO**: `agent-reports/research_27.md`
