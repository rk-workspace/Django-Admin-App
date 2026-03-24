# define_ec2_instance

data "aws_ami" "ubuntuOS"{
    most_recent = true

    filter {
      name = "name"
      values = [ "ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*" ]
    }

    filter {
      name = "virtualization-type"
      values = [ "hvm" ]
    }

    owners = ["099720109477"]
}

resource "aws_instance" "my_ec2_instance" {
  ami = data.aws_ami.ubuntuOS.id
  instance_type = "t3.micro"
  key_name = aws_key_pair.django_key_pairs.key_name

  tags = {
    Name = "Django-App-Instance"
  }

  user_data = <<-EOF
                #!/bin/bash
                apt update -y
                apt install ca-certificates curl gnupg -y
                install -m 0755 -d /etc/apt/keyrings
                curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
                chmod a+r /etc/apt/keyrings/docker.gpg
                echo \
                    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
                    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
                    tee /etc/apt/sources.list.d/docker.list > /dev/null
    
                apt update -y
                apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

                usermod -aG docker ubuntu
              EOF
}

resource "aws_key_pair" "django_key_pairs" {
  key_name = "admin-app_key_pairs"
  public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQC2NUt8PhmPUukIBsnVeKg6IzpN+38z42AeazkXI6mKHYtTPhHY3GI+65l0pVcAu9FzZWXUUrVYKMqneg9HJ6im1dmxGbansfX/0I2vhyhM3yw0IdDDhuU+JP18cuME1djTvhsh2IRlAtsZZ/a7wPn5jsE4QxttUQgUgeeYmoUN2+Bs5OFH/OTsbwlfbp1VuWbHqSzoRUWvE8mZjpvA0b1IsBInG9EArHbnRULL5vP3qmIYQdxvZYxf+IsreIGNEEtYe+MiVdoKfMvHECnosjyMkCOsIxy3axEhRjmK+4dQhUyYp3Hbnhc11tmAhN55fhv4nXyzjjVetbTztmNw2JCB9xz1UlZPMWaqQvDGap95d7Drr1D83ks/BwvkTJZs0l/9U4FwqwtIr/faMpACmsuqnT5rwYy+p2Fc+nOfpQcJ4IQqEKjhraYM+i21VAaJGFsTNCs9TFyb2zaTDuH1ujR4MTKKoj0lPTDKE3aZuKJ1T/yV7sYlnpFyzt6VA/3gSpJXCDn/jidT4BF3pOkmF0arko7aJGD+slSVDUu6jVPOmnAZ9+X0PUFoFweMUNYUm/rBOjIgVgHhRBwgRoQI26ExdsNE1MT+SZB+0S43BVa3YR4Gkz641c/Ira1RlpwNjzZJaa3UQw+enjzCZKiY2nSbBOlGahJmfcqioAIkywV3tw== rashu.cloud11@gmail.com"
}

# configure networking rules