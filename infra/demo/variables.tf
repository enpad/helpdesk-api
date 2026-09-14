variable "aws_region" {
  description = "AWS region for the demo resources. Must match the account/region approved for the live session."
  type        = string
}

variable "aws_account_id" {
  description = "AWS account ID the demo must run in (Kindor demo/sandbox account). Terraform refuses to apply against any other account."
  type        = string
}

variable "aws_profile" {
  description = "Named AWS CLI profile to use — must be a scoped identity (e.g. claude-course-demo), never a root or admin profile. Terraform never falls back to an implicit default profile."
  type        = string
}

variable "operator_cidr" {
  description = "Operator's current public IP as a /32 CIDR, e.g. 203.0.113.10/32. The security group only allows this CIDR on port 8000."
  type        = string
}

variable "artifact_bucket_name" {
  description = "Globally-unique S3 bucket name created exclusively for this demo's build artifacts. Never an existing Kindor bucket."
  type        = string
}

variable "artifact_s3_key" {
  description = "Exact S3 key of the tarball to deploy, e.g. releases/helpdesk-api-abc1234.tar.gz. Produced by scripts/build_and_publish.sh."
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type."
  type        = string
  default     = "t3.micro"
}

variable "project_tag" {
  description = "Value applied to the Project tag on every resource, used for identification and cleanup."
  type        = string
  default     = "claude-course-demo"
}
