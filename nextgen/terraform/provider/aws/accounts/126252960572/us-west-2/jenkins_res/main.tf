resource "aws_launch_configuration" "windows_builder_config" {
  image_id = var.windows_ami_id
  instance_type = var.windows_instance_type
  name = format("%s-win_build_config", local.regional_prefix)
}

resource "aws_autoscaling_group" "windows_builders" {
  name = format("%s-win_build_asg", local.regional_prefix)
  max_size = 12
  min_size = 0
  desired_capacity = 0
  launch_configuration = aws_launch_configuration.windows_builder_config.name
  vpc_zone_identifier = data.terraform_remote_state.vpc.outputs.private_subnet_ids["vpc0"]["windows_asg"]
  depends_on = [aws_launch_configuration.windows_builder_config]
}