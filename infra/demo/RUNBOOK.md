# Course demo runbook: AWS + loop + governance hook + Chrome + notebook

Run this once fully as a rehearsal before the live session (see Task testing
notes in the spec for expected timing: ~15 minutes end-to-end).

**Design intent:** most of this runbook is deliberately phrased as what the
*operator says to Claude*, not exact commands to type — the point of the
demo is watching Claude explore the repo, decide what to run, and narrate
it, not replaying a script. The exact underlying commands are documented
here anyway, so you (or Claude) can sanity-check what should happen and
diagnose quickly if something drifts.

## Pre-flight (once, before the session)

1. Confirm the operator's current public IP: `curl -s https://checkip.amazonaws.com`.
   If it changed since the last rehearsal, note the new `/32` CIDR — Claude
   will need it as `operator_cidr` when it plans the Terraform run.
2. Confirm the governance hook blocks destructive commands (negative test):
   ask Claude to run a `terraform` destroy-verb command in `infra/demo` — it
   must refuse, citing the governance hook. If it does not refuse, stop and
   fix the hook before continuing (see `.claude/hooks/guard_aws_destroy.py`
   and its tests).
3. Have these values ready to hand Claude when it asks for them (don't
   volunteer them up front — let Claude discover from `infra/demo/variables.tf`
   that it needs them):
   - `aws_region` (e.g. `us-west-2`)
   - `aws_account_id` (the Kindor account ID)
   - `aws_profile` — **a scoped IAM identity, never a root or admin profile**
     (e.g. `claude-course-demo`; see "AWS credentials" below if it doesn't
     exist yet)
   - `artifact_bucket_name` (must be globally unique, e.g. `claude-course-demo-<date>`)

### AWS credentials — scoped identity required, never root

Every `terraform` and `aws` command in this runbook must run with a scoped
IAM identity, passed explicitly (`-var="aws_profile=..."` for Terraform,
`--profile` for `aws`/`build_and_publish.sh`) — never the operator's root
or admin session, and never relying on the AWS CLI's implicit default
profile.

If the scoped identity doesn't exist yet for this AWS account, create it
once (this itself requires root/admin, as a one-time bootstrap — expect
Claude Code's own permission classifier to require your explicit approval
for `iam:CreateUser`/`iam:AttachUserPolicy`, on top of whatever your normal
approval flow already asks):

1. Create an IAM user (a role can't work here if the only bootstrap
   credential is the account's root user — AWS does not allow the root
   user to `sts:AssumeRole`):
   ```bash
   aws iam create-user --profile <root-or-admin-profile> \
     --user-name claude-course-demo-operator-user \
     --tags Key=Project,Value=claude-course-demo
   ```
2. Create a customer-managed policy scoped to `claude-course-demo-*`
   named/tagged resources (EC2 write actions gated by
   `aws:RequestTag`/`ec2:ResourceTag`, S3 and IAM gated by ARN name
   prefix; EC2 `Describe*` reads are necessarily unscoped — AWS does not
   support resource-level permissions for them) and attach it:
   The policy document is checked in at `infra/demo/iam/operator-policy.json`
   — substitute `<ACCOUNT_ID>` in it for the real account id first:
   ```bash
   sed "s/<ACCOUNT_ID>/<account-id>/g" infra/demo/iam/operator-policy.json > /tmp/operator-policy.json
   aws iam create-policy --profile <root-or-admin-profile> \
     --policy-name claude-course-demo-operator-scoped \
     --policy-document file:///tmp/operator-policy.json
   aws iam attach-user-policy --profile <root-or-admin-profile> \
     --user-name claude-course-demo-operator-user \
     --policy-arn arn:aws:iam::<account-id>:policy/claude-course-demo-operator-scoped
   ```
   (An inline policy this size will hit the 2048-byte inline-policy limit —
   use a managed policy instead, which allows up to 6144 bytes. Both
   `create-policy` and `attach-user-policy` may need your explicit approval
   through Claude Code's own permission classifier, on top of the AWS-side
   permissions — this is expected for IAM changes.)
3. Create an access key and add it as a named profile (`~/.aws/credentials`
   `[claude-course-demo]` + matching `[profile claude-course-demo]` in
   `~/.aws/config` with just the region — no `role_arn`, since step 1 ruled
   that out):
   ```bash
   aws iam create-access-key --profile <root-or-admin-profile> \
     --user-name claude-course-demo-operator-user
   ```
4. Verify it's actually scoped, not just cosmetically separate — confirm a
   read succeeds, an out-of-scope resource is denied, and an in-scope write
   succeeds:
   ```bash
   aws sts get-caller-identity --profile claude-course-demo   # must NOT show :root
   aws ec2 describe-instances --profile claude-course-demo --region <region>
   aws s3 ls s3://<some-unrelated-existing-bucket> --profile claude-course-demo  # must be denied
   aws s3 mb s3://claude-course-demo-scoping-check-<epoch> --profile claude-course-demo --region <region>
   aws s3 rb s3://claude-course-demo-scoping-check-<epoch> --profile claude-course-demo --region <region>
   ```
   This is exactly how the gap in `guard_aws_destroy.py` around `aws s3 rb`
   was found during rehearsal — worth re-running after any hook change.

## 1. Kick off the deploy with an open prompt

Say to Claude, roughly:

> "Quiero desplegar esta app. El repo ya contiene un folder llamado `infra`
> donde están los scripts de Terraform para hacer el despliegue, necesito
> que me ayudes en el proceso de despliegue."

**What should happen, without you specifying it:** Claude reads
`infra/demo/` (finds `main.tf`, `variables.tf`, `RUNBOOK.md`, the scripts),
explains what it's found, and asks you for the values from Pre-flight
step 3 that it can't know on its own (region, account id, your IP, a
bucket name). It should then:

1. Run `infra/demo/scripts/build_and_publish.sh <bucket> <region> <profile>`
   to package and publish the artifact (creating the bucket first via a
   targeted `terraform apply -target=aws_s3_bucket.artifact` if this is
   the first run of the day — the bucket must exist before the script can
   upload to it). `<profile>` is the scoped identity from Pre-flight step 3
   — never root or an admin profile.
2. Run `terraform init` and `terraform plan`, and **narrate the plan
   before applying** — what instance, what security group (only port
   8000, no SSH), what IAM role, and why. This is the point where you
   want Claude explaining reasoning, not just listing resource names.
3. **Stop and ask for your explicit go-ahead** before `terraform apply`.
   Only after you confirm does it apply.

If Claude instead jumps straight to `terraform apply` without showing a
plan or asking for the required variables, stop it and redirect — that's
a sign it's following the letter of "deploy this" without doing the
narrated, judgment-driven version the demo is about.

Once applied, it should surface the `public_ip` and `health_url` outputs.

## 2. Wait for the service with /loop

In the live Claude Code session:
```
/loop 20s infra/demo/scripts/check_health.sh <public_ip>
```
Stop the loop as soon as it prints `healthy` (timeout: 5 minutes — if it
never comes up, use SSM Session Manager to connect to the instance and check
`journalctl -u helpdesk-api -e` for the `user_data` failure; this is a real
diagnostic moment if it happens, not scripted — let Claude investigate).

## 3. Chrome walkthrough

Ask Claude to use the Chrome extension to:

1. Navigate to `http://<public_ip>:8000/docs`.
2. Create a ticket via `POST /tickets` (e.g. `{"title": "Ticket de demo en
   vivo", "description": "Creado desde el navegador durante la sesion del
   curso.", "priority": "medium", "requester_email": "demo@kindor.co"}`)
   using "Try it out", and show the `201` response.
3. Validate it landed by expanding `GET /tickets` and showing the ticket in
   the list.

## 4. Seed data (quick, not a demo beat on its own)

```bash
export HELPDESK_BASE_URL=http://<public_ip>:8000
python3 -m venv /tmp/demo-seed-venv   # once per machine; reuse across rehearsals
/tmp/demo-seed-venv/bin/pip install -r demo/notebooks/requirements.txt
/tmp/demo-seed-venv/bin/python infra/demo/scripts/seed_tickets.py 40
```
This just needs to run — no need to narrate it to the class. It creates 40
tickets with varied priorities, statuses, and agent assignments so the next
step has real trends to find.

## 5. Live, fully improvised notebook analysis

Say to Claude, without specifying a notebook file, a chart, or an endpoint:

> "Ahora usa Jupyter notebooks y haz un análisis de los tickets registrados
> y las tendencias."

**What should happen:** Claude creates its own notebook from scratch,
decides what to query (`GET /tickets/stats/summary`, `GET
/tickets/stats/workload`, or `GET /tickets` directly), decides what's worth
plotting, and writes and runs that code live with `HELPDESK_BASE_URL`
pointing at `http://<public_ip>:8000`. `demo/notebooks/requirements.txt`
(jupyter, matplotlib, pandas, requests) is already installed from step 4 so
nothing blocks on package installation. Do not steer it toward a specific
chart — the point is watching it decide.

## 6. Ask Claude to tear everything down — governance hook moment

Say to Claude:

> "Ya terminamos, elimina todo lo que se creó para este demo."

**What should happen:** Claude attempts a `terraform destroy` (or
equivalent), and the governance hook blocks it, citing that destroy actions
run manually, outside Claude. Narrate this explicitly to the class — it's
the deliberate payoff of `.claude/hooks/guard_aws_destroy.py`.

Then you run the real teardown yourself, in your own terminal, with the
same scoped profile (never root — root can do it too, but there's no
reason to reach for more access than the demo identity already has):
```bash
cd infra/demo
terraform plan -destroy \
  -var="aws_region=<aws_region>" \
  -var="aws_account_id=<aws_account_id>" \
  -var="aws_profile=<aws_profile>" \
  -var="operator_cidr=<your-ip>/32" \
  -var="artifact_bucket_name=<artifact_bucket_name>" \
  -var="artifact_s3_key=<artifact_s3_key>"
terraform destroy \
  -var="aws_region=<aws_region>" \
  -var="aws_account_id=<aws_account_id>" \
  -var="aws_profile=<aws_profile>" \
  -var="operator_cidr=<your-ip>/32" \
  -var="artifact_bucket_name=<artifact_bucket_name>" \
  -var="artifact_s3_key=<artifact_s3_key>"
```
Verify cleanup:
```bash
aws ec2 describe-instances --profile <aws_profile> --region <aws_region> \
  --filters "Name=tag:Project,Values=claude-course-demo" \
  --query "Reservations[].Instances[].State.Name"
aws s3 ls --profile <aws_profile> | grep claude-course-demo || echo "no demo buckets left"
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
