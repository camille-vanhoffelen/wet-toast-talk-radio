import { Construct } from 'constructs';
import { aws_s3 as s3, Duration, Aws } from 'aws-cdk-lib';
import { resourceName } from './resource-name';

export class MediaStore extends Construct {
    readonly bucket: s3.Bucket;
    constructor(scope: Construct, id: string, dev = false) {
        super(scope, id);

        const intelligentTieringConfigurations = [];
        for (const prefix of ['raw', 'transcoded', 'script']) {
            intelligentTieringConfigurations.push({
                name: prefix,
                prefix: `${prefix}/`,
                archiveAccessTierTime: Duration.days(90),
                deepArchiveAccessTierTime: Duration.days(180),
            });
        }

        const bucketName = resourceName('media-store-' + Aws.ACCOUNT_ID, dev);
        this.bucket = new s3.Bucket(this, 'Bucket', {
            bucketName,
            intelligentTieringConfigurations,
        });
    }
}
