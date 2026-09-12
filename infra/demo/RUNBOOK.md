# Course demo runbook: AWS + loop + governance hook + Chrome + notebook

Run this once fully as a rehearsal before the live session (see Task testing
notes in the spec for expected timing: ~15 minutes end-to-end).

## Pre-flight (once, before the session)

1. Confirm the operator's current public IP: `curl -s https://checkip.amazonaws.com`.
   If it changed since the last rehearsal, note the new `/32` CIDR — you'll pass
   it as `operator_cidr` below.
2. Confirm the governance hook blocks destructive commands (negative test):
   ask Claude to run a `terraform` destroy-verb command in `infra/demo` — it
   must refuse, citing the governance hook. If it does not refuse, stop and
   fix the hook before continuing (see `.claude/hooks/guard_aws_destroy.py`
   and its tests).
3. Choose (or reuse from the last rehearsal) values for:
   - `aws_region` (e.g. `us-east-1`)
   - `aws_account_id` (the Kindor demo/sandbox account ID)
   - `artifact_bucket_name` (must be globally unique, e.g. `claude-course-demo-<date>`)

## 1. Build & publish the artifact

```bash
infra/demo/scripts/build_and_publish.sh <artifact_bucket_name> <aws_region>
```
Copy the printed S3 key (e.g. `releases/helpdesk-api-abc1234.tar.gz`) — this is
`artifact_s3_key` below. Note: the bucket must already exist before this
succeeds; on the very first run of the day, apply Terraform once to create
the bucket (Terraform will fail to place the EC2 instance without a valid
`artifact_s3_key`, so do a two-step apply: first `terraform apply
-target=aws_s3_bucket.artifact`, then run this script, then the full apply
below).

## 2. Provision the infrastructure

```bash
cd infra/demo
terraform init
terraform plan \
  -var="aws_region=<aws_region>" \
  -var="aws_account_id=<aws_account_id>" \
  -var="operator_cidr=<your-ip>/32" \
  -var="artifact_bucket_name=<artifact_bucket_name>" \
  -var="artifact_s3_key=<artifact_s3_key>" \
  -out=demo.tfplan
```
**Stop here and show the plan to the operator.** Only after explicit
confirmation:
```bash
terraform apply demo.tfplan
```
Note the `public_ip` and `health_url` outputs.

## 3. Wait for the service with /loop

In the live Claude Code session:
```
/loop 20s infra/demo/scripts/check_health.sh <public_ip>
```
Stop the loop as soon as it prints `healthy` (timeout: 5 minutes — if it
never comes up, use SSM Session Manager to connect to the instance and check
`journalctl -u helpdesk-api -e` for the `user_data` failure).

## 4. Chrome walkthrough

1. Navigate to `http://<public_ip>:8000/docs`.
2. Expand `POST /tickets`, click "Try it out", submit a sample ticket
   payload (e.g. `{"title": "Ticket de demo en vivo", "description":
   "Creado desde el navegador durante la sesion del curso.", "priority":
   "medium", "requester_email": "demo@kindor.co"}`), execute, and show the
   `201` response.
3. Expand `GET /tickets` and show the created ticket in the list.

## 5. Notebook — seed data, then live analysis

```bash
export HELPDESK_BASE_URL=http://<public_ip>:8000
jupyter notebook demo/notebooks/seed_tickets.ipynb
```
Run the seed cells (setup, create tickets, update statuses) — this part is
prepared and reliable. Then, **live, with Claude**, add new cells that query
`GET /tickets/stats/summary` and/or `GET /tickets/stats/workload` and plot
the result with matplotlib — this is the analysis step, and it is
deliberately not pre-written: the value being demonstrated is Claude
deciding what to look at and writing that analysis against real data it
just created, not replaying a canned cell.

## 6. Teardown (manual, outside Claude)

In your own terminal — **not** delegated to Claude, the governance hook
blocks it there anyway:
```bash
cd infra/demo
terraform plan -destroy \
  -var="aws_region=<aws_region>" \
  -var="aws_account_id=<aws_account_id>" \
  -var="operator_cidr=<your-ip>/32" \
  -var="artifact_bucket_name=<artifact_bucket_name>" \
  -var="artifact_s3_key=<artifact_s3_key>"
terraform destroy \
  -var="aws_region=<aws_region>" \
  -var="aws_account_id=<aws_account_id>" \
  -var="operator_cidr=<your-ip>/32" \
  -var="artifact_bucket_name=<artifact_bucket_name>" \
  -var="artifact_s3_key=<artifact_s3_key>"
```
Verify cleanup:
```bash
aws ec2 describe-instances --filters "Name=tag:Project,Values=claude-course-demo" \
  --query "Reservations[].Instances[].State.Name"
aws s3 ls | grep claude-course-demo || echo "no demo buckets left"
```
Both should show nothing running / no leftover bucket.

## Fallback plan

If AWS misbehaves live (instance stuck, `user_data` failure, network
issues), fall back to running the app locally (`python run.py` on the
presenter's machine) and continue the Chrome/notebook steps against
`http://localhost:8000` — narrate that this is the fallback, skip the
`/loop` step (nothing to wait for), and still cover the intended
teaching points about the AWS flow using the already-applied Terraform
plan output as the visual aid.
