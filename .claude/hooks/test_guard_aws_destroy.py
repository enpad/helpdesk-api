import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).parent / "guard_aws_destroy.py"


def run_hook(command: str) -> subprocess.CompletedProcess:
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload,
        capture_output=True,
        text=True,
    )


def test_blocks_terraform_destroy():
    result = run_hook("terraform destroy -auto-approve")
    assert result.returncode == 2
    assert "governance hook" in result.stderr


def test_blocks_terraform_apply_with_destroy_flag():
    result = run_hook("terraform apply -destroy -auto-approve")
    assert result.returncode == 2


def test_blocks_aws_terminate_instances():
    result = run_hook("aws ec2 terminate-instances --instance-ids i-0123456789abcdef0")
    assert result.returncode == 2


def test_blocks_aws_delete_bucket():
    result = run_hook("aws s3api delete-bucket --bucket claude-course-demo-artifacts")
    assert result.returncode == 2


def test_blocks_aws_s3_rb_shorthand():
    result = run_hook("aws s3 rb s3://claude-course-demo-artifacts")
    assert result.returncode == 2


def test_allows_terraform_plan():
    result = run_hook("terraform plan -out=demo.tfplan")
    assert result.returncode == 0


def test_allows_terraform_apply():
    result = run_hook("terraform apply demo.tfplan")
    assert result.returncode == 0


def test_allows_aws_s3_cp():
    result = run_hook("aws s3 cp build/release.tar.gz s3://claude-course-demo-artifacts/releases/x.tar.gz")
    assert result.returncode == 0


def test_allows_aws_describe_instances():
    result = run_hook("aws ec2 describe-instances")
    assert result.returncode == 0


def test_allows_unrelated_commands():
    result = run_hook("ls -la infra/demo")
    assert result.returncode == 0


def test_allows_commit_message_mentioning_destroy():
    result = run_hook(
        'git commit -m "Add governance hook blocking terraform destroy and destructive aws verbs"'
    )
    assert result.returncode == 0
