terraform {
  required_version = ">= 1.7.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region              = var.aws_region
  profile             = var.aws_profile
  allowed_account_ids = [var.aws_account_id]
}

data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["137112412989"] # Amazon

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

resource "aws_s3_bucket" "artifact" {
  bucket        = var.artifact_bucket_name
  force_destroy = true

  tags = {
    Project = var.project_tag
  }
}

resource "aws_s3_bucket_public_access_block" "artifact" {
  bucket                  = aws_s3_bucket.artifact.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_iam_role" "ec2" {
  name = "${var.project_tag}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })

  tags = {
    Project = var.project_tag
  }
}

resource "aws_iam_role_policy" "s3_read_artifact" {
  name = "${var.project_tag}-s3-read-artifact"
  role = aws_iam_role.ec2.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["s3:GetObject"]
      Resource = "${aws_s3_bucket.artifact.arn}/releases/*"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.ec2.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "ec2" {
  name = "${var.project_tag}-ec2-profile"
  role = aws_iam_role.ec2.name
}

resource "aws_security_group" "demo" {
  name        = "${var.project_tag}-sg"
  description = "Course demo: only the operator's IP can reach port 8000. No SSH."

  ingress {
    description = "Helpdesk API, operator only"
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = [var.operator_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Project = var.project_tag
  }
}

resource "aws_instance" "demo" {
  ami                    = data.aws_ami.al2023.id
  instance_type          = var.instance_type
  iam_instance_profile   = aws_iam_instance_profile.ec2.name
  vpc_security_group_ids = [aws_security_group.demo.id]

  metadata_options {
    http_tokens   = "required"
    http_endpoint = "enabled"
  }

  # Without this, the root EBS volume gets no tags in the RunInstances
  # call itself — Terraform tags it via a separate CreateTags call after
  # creation instead, same as it does for the security group. Tagging it
  # here keeps the "every resource carries Project=claude-course-demo"
  # guarantee true from the moment of creation, not after the fact.
  root_block_device {
    tags = {
      Project = var.project_tag
    }
  }

  user_data = templatefile("${path.module}/user_data.sh.tpl", {
    bucket = var.artifact_bucket_name
    key    = var.artifact_s3_key
    region = var.aws_region
  })

  tags = {
    Name    = "${var.project_tag}-instance"
    Project = var.project_tag
  }
}
