

output "cp_sg_id" {
  value = "${module.sg.cp_sg_id}"
}

output "cp_sg_arn" {
  value = "${module.sg.cp_sg_arn}"
}

output "cluster_name" {
  value = "${aws_eks_cluster.cluster.name}"
}