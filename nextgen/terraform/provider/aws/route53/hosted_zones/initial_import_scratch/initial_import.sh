#!/usr/bin/env bash

# 20210511
# import existing zones, withme.com, withme.de, and *.withme.com

direnv exec ~/ops/aws/407733091588/build_user tf15 import module.route53_hosted_zone[0].aws_route53_zone.zone  Z043867237VNOZ9QMLR2S
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.route53_hosted_zone[1].aws_route53_zone.zone  Z07753632PXZ3H94T9GY2
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[0].aws_route53_zone.zone  Z05320852TOXZL7KZ16KA
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[1].aws_route53_zone.zone  ZHSJ9YRM74LE9
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[2].aws_route53_zone.zone  Z2XI6I7Q87C94M
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[3].aws_route53_zone.zone  Z3BJK3DL5VAC69
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[4].aws_route53_zone.zone  ZZB61V0USA0BM
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[5].aws_route53_zone.zone  ZT9WYNS51Q8MJ
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[6].aws_route53_zone.zone  Z02900261M7ASN3HEVOQF
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[7].aws_route53_zone.zone  Z1BBGSUNFZHR1K
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[8].aws_route53_zone.zone  Z02109601NE7C0NBZ36AW
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[9].aws_route53_zone.zone  Z07217317DHPGBT1T752
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[10].aws_route53_zone.zone  Z2ZYPZ30HZGU6Q
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[11].aws_route53_zone.zone  Z06175761WIU5PL91ZXDX
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[12].aws_route53_zone.zone  Z02382641X5R2BON4RUNP
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[13].aws_route53_zone.zone  Z31DNN3JEALTTG
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[14].aws_route53_zone.zone  Z08876992YQF7VY8ZVCW4
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[15].aws_route53_zone.zone  Z3O5C67TLOK0QO
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[16].aws_route53_zone.zone  Z051516028XHRJ00A70SX
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[17].aws_route53_zone.zone  Z1YHUK37GL4828
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[18].aws_route53_zone.zone  Z221QR6AQN5Z95
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[19].aws_route53_zone.zone  ZEF0KYZ48N886
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[20].aws_route53_zone.zone  ZV4UM9HDYQ39E
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[21].aws_route53_zone.zone  Z1CSVLH6EMC2Z
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[22].aws_route53_zone.zone  Z0180272779JJQT56DPA
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[23].aws_route53_zone.zone  Z053291817NQISMLKXZVC
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[24].aws_route53_zone.zone  ZZEXR47J934F5
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[25].aws_route53_zone.zone  ZSI9UY1GAXD85
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[26].aws_route53_zone.zone  Z2823XQDYLSMSH
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[27].aws_route53_zone.zone  Z28QGGI714Q2I
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[28].aws_route53_zone.zone  ZNCVYHIJBFV1L
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[29].aws_route53_zone.zone  Z1GCV57Y579JAP
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[30].aws_route53_zone.zone  Z33P78VUI29JTU
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[31].aws_route53_zone.zone  Z021063613N2F5GEF7IA2
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[32].aws_route53_zone.zone  Z00887593NMD9RYDH0FI2
direnv exec ~/ops/aws/407733091588/build_user tf15 import module.subdomains[0].module.route53_hosted_zone[33].aws_route53_zone.zone  Z2KW3GK7R41VCI
 
