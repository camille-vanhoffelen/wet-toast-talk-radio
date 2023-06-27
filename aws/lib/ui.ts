import { Construct } from 'constructs';
import {
    aws_s3 as s3,
    Aws,
    aws_s3_deployment as s3Deployment,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
} from 'aws-cdk-lib';

export class Ui extends Construct {
    readonly bucket: s3.Bucket;
    constructor(scope: Construct, id: string) {
        super(scope, id);

        const bucket = new s3.Bucket(this, 'Bucket', {
            bucketName: 'wet-toast-ui-' + Aws.ACCOUNT_ID,
            accessControl: s3.BucketAccessControl.PRIVATE,
        });

        new s3Deployment.BucketDeployment(this, 'BucketDeployment', {
            sources: [s3Deployment.Source.asset('../ui')],
            destinationBucket: bucket,
        });

        const originAccessIdentity = new cloudfront.OriginAccessIdentity(this, 'OriginAccessIdentity');
        bucket.grantRead(originAccessIdentity);

        new cloudfront.Distribution(this, 'Distribution', {
            defaultRootObject: 'index.html',
            defaultBehavior: {
                origin: new origins.S3Origin(bucket, { originAccessIdentity }),
            },
            errorResponses: [
                {
                    httpStatus: 404,
                    responseHttpStatus: 200,
                    responsePagePath: '/index.html',
                },
            ],
        });
    }
}
