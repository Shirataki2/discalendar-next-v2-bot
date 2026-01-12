# Lightsail instance for Discord Bot
resource "aws_lightsail_instance" "bot" {
  name              = var.instance_name
  availability_zone = "${var.aws_region}a"
  blueprint_id      = var.blueprint_id
  bundle_id         = var.bundle_id

  user_data = file("${path.module}/user_data.sh")

  tags = merge(
    var.tags,
    {
      Name = var.instance_name
    }
  )
}

# Static IP for Lightsail instance
resource "aws_lightsail_static_ip" "bot" {
  name = "${var.instance_name}-static-ip"
}

resource "aws_lightsail_static_ip_attachment" "bot" {
  static_ip_name = aws_lightsail_static_ip.bot.id
  instance_name  = aws_lightsail_instance.bot.id
}
