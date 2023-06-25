import { Construct } from 'constructs';
import { CfnParameter, aws_s3 as s3 } from 'aws-cdk-lib';

interface ModelCacheProps {
    bucketName: CfnParameter;
}

export class ModelCache extends Construct {
    readonly bucket: s3.IBucket;
    constructor(scope: Construct, id: string, props: ModelCacheProps) {
        super(scope, id);
        this.bucket = s3.Bucket.fromBucketName(this, 'Bucket', props.bucketName.valueAsString);
    }
}
