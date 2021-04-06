provider "local" {
}

resource "local_file" "in_temp_dir" {
  count = var.generate == true ? 1 : 0
  content  = var.content
  filename = "${var.path_prefix}.${var.uniq}/${var.filename}"
}
