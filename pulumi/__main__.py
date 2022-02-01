from pulumi import export
from pulumi_aws import s3, cloudfront, iam

website_bucket = s3.Bucket(
    's3-hurtov-test-alpacked',
    acl="private",
)

bucket_name = website_bucket.id

cf_origin_access_identity = cloudfront.OriginAccessIdentity("origin-access-identity", comment="Identity")

def s3_policy(bucket_name):
    return iam.get_policy_document(statements=[iam.GetPolicyDocumentStatementArgs(
        actions=["s3:GetObject"],
        resources=[f"arn:aws:s3:::{bucket_name}/*"],
        principals=[iam.GetPolicyDocumentStatementPrincipalArgs(
            type="AWS",
            identifiers=[cf_origin_access_identity.iam_arn],
        )],
    )]).json


bucket_policy = s3.BucketPolicy("bucket-policy",
                                bucket=bucket_name,
                                policy=bucket_name.apply(s3_policy))

s3_origin_id = "myS3Origin"
website_cloudfront = cloudfront.Distribution("website_cloudfront",
                                         origins=[cloudfront.DistributionOriginArgs(
                                             domain_name=website_bucket.bucket_regional_domain_name,
                                             origin_id=s3_origin_id,
                                             s3_origin_config=cloudfront.DistributionOriginS3OriginConfigArgs(
                                                 origin_access_identity=cf_origin_access_identity.cloudfront_access_identity_path
                                             )
                                         )],
                                         enabled=True,
                                         comment="Cloudfront_Alpacked",
                                         default_root_object="index.html",
                                         default_cache_behavior=cloudfront.DistributionDefaultCacheBehaviorArgs(
                                             allowed_methods=[
                                                 "DELETE",
                                                 "GET",
                                                 "HEAD",
                                                 "OPTIONS",
                                                 "PATCH",
                                                 "POST",
                                                 "PUT",
                                             ],
                                             cached_methods=[
                                                 "GET",
                                                 "HEAD",
                                             ],
                                             target_origin_id=s3_origin_id,
                                             forwarded_values=cloudfront.DistributionDefaultCacheBehaviorForwardedValuesArgs(
                                                 query_string=False,
                                                 cookies=cloudfront.DistributionDefaultCacheBehaviorForwardedValuesCookiesArgs(
                                                     forward="none",
                                                 ),
                                             ),
                                             viewer_protocol_policy="allow-all",
                                             min_ttl=0,
                                             default_ttl=3600,
                                             max_ttl=86400,
                                         ),
                                         ordered_cache_behaviors=[
                                             cloudfront.DistributionOrderedCacheBehaviorArgs(
                                                 path_pattern="/content/immutable/*",
                                                 allowed_methods=[
                                                     "GET",
                                                     "HEAD",
                                                     "OPTIONS",
                                                 ],
                                                 cached_methods=[
                                                     "GET",
                                                     "HEAD",
                                                     "OPTIONS",
                                                 ],
                                                 target_origin_id=s3_origin_id,
                                                 forwarded_values=cloudfront.DistributionOrderedCacheBehaviorForwardedValuesArgs(
                                                     query_string=False,
                                                     headers=["Origin"],
                                                     cookies=cloudfront.DistributionOrderedCacheBehaviorForwardedValuesCookiesArgs(
                                                         forward="none",
                                                     ),
                                                 ),
                                                 min_ttl=0,
                                                 default_ttl=86400,
                                                 max_ttl=31536000,
                                                 compress=True,
                                                 viewer_protocol_policy="redirect-to-https",
                                             ),
                                             cloudfront.DistributionOrderedCacheBehaviorArgs(
                                                 path_pattern="/content/*",
                                                 allowed_methods=[
                                                     "GET",
                                                     "HEAD",
                                                     "OPTIONS",
                                                 ],
                                                 cached_methods=[
                                                     "GET",
                                                     "HEAD",
                                                 ],
                                                 target_origin_id=s3_origin_id,
                                                 forwarded_values=cloudfront.DistributionOrderedCacheBehaviorForwardedValuesArgs(
                                                     query_string=False,
                                                     cookies=cloudfront.DistributionOrderedCacheBehaviorForwardedValuesCookiesArgs(
                                                         forward="none",
                                                     ),
                                                 ),
                                                 min_ttl=0,
                                                 default_ttl=3600,
                                                 max_ttl=86400,
                                                 compress=True,
                                                 viewer_protocol_policy="redirect-to-https",
                                             ),
                                         ],
                                         price_class="PriceClass_200",
                                         restrictions=cloudfront.DistributionRestrictionsArgs(
                                             geo_restriction=cloudfront.DistributionRestrictionsGeoRestrictionArgs(
                                                 restriction_type="none",
                                             ),
                                         ),
                                         tags={
                                             "Environment": "production",
                                         },
                                         viewer_certificate=cloudfront.DistributionViewerCertificateArgs(
                                             cloudfront_default_certificate=True,
                                         ))

export('bucket', website_bucket.id)
export('site_url', website_cloudfront.domain_name)
