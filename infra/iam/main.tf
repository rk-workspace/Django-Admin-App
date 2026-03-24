# iam_group_define
resource "aws_iam_group" "accessors" {
    name = "developers"
    path = "/developers/"
}

# iam_group_policy_define
resource "aws_iam_group_policy" "users_access_policy" {
  name = "users_access_policy"
  group = aws_iam_group.accessors.name

  policy = data.aws_iam_policy_document.access_policy_define.json
}

data "aws_iam_policy_document" "access_policy_define" {
  statement {
    sid = "developers-group-policy"

    actions = [
        "will add later",
    ]

    resources = [ 
        "arn:aws:ec2:thecreatedec2istance",
    ]

  }
}

# iam_users_define_1
resource "aws_iam_user" "userDev" {
  name = "userDev"
  path = "/developers/"
}

# iam_users_define_2
resource "aws_iam_user" "userOps" {
  name = "userOps"
  path = "/developers/"
}

resource "aws_iam_user_group_membership" "group_add_1" {
  user = aws_iam_user.userDev.name

  groups = [ 
        aws_iam_group.accessors.name,
   ]
}

resource "aws_iam_user_group_membership" "group_add_2" {
  user = aws_iam_user.userOps.name

  groups = [ 
        aws_iam_group.accessors.name,
   ]
}

