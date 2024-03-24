provider "aws" {
  region = var.region
}


resource "aws_db_instance" "MysqlForLambda" {
  allocated_storage         = 20
  storage_type              = "gp2"
  engine               =     "mysql"
  engine_version       =     "5.7"
  instance_class       =     "db.t3.micro"
  db_name                   = "DBLAMBDAMETRICS"
  username                  = var.db_username
  password                  = var.db_password
  # final_snapshot_identifier = "someid"
  skip_final_snapshot       = true
    publicly_accessible = true
}

data "archive_file" "lambda" {
  type        = "zip"
  source_dir  = "lambda"
  output_path = "app.zip"
}


# Create IAM role for Lambda function
resource "aws_iam_role" "lambda_role" {
  name = "lambda-execution-role"
  assume_role_policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Principal" : {
          "Service" : "lambda.amazonaws.com"
        },
        "Action" : "sts:AssumeRole"
      }
    ]
  })
}

# Attach policy to IAM role granting necessary permissions
resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# IAM policy granting full access to Amazon RDS for Lambda function
resource "aws_iam_role_policy" "lambda_rds_full_access_policy" {
  name   = "lambda-rds-full-access-policy"
  role   = aws_iam_role.lambda_role.id

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "rds:*",
        "Resource": "*"
      }
    ]
  })
}



resource "aws_lambda_function" "test_lambda" {
  filename         = "app.zip"
  function_name    = "AWSLambdaExecutionCounter"
  role             =  aws_iam_role.lambda_role.arn
  handler          = "app.handler"
  runtime          = "python3.8"
  source_code_hash = filebase64sha256(data.archive_file.lambda.output_path)
  
  environment {
    variables = {
      rds_endpoint = aws_db_instance.MysqlForLambda.endpoint
      db_username  = var.db_username
      db_password  = var.db_password
    }
  }
}

