resource "aws_iam_role_policy" "lambda_rds_backup_role" {
    name = "lambda_rds_backup"
    role = "${aws_iam_role.lambda_rds_backup.id}"
    policy = "${file("${path.module}/role_policy.json")}"
}

resource "aws_iam_role" "lambda_rds_backup" {
    name = "lambda_rds_backup"
    assume_role_policy = "${file("${path.module}/role.json")}"
}
