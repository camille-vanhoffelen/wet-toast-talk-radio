import { Construct } from 'constructs';
import { aws_s3 as s3, Duration, Aws } from 'aws-cdk-lib';

export class MediaStore extends Construct {
    readonly bucket: s3.Bucket;
    constructor(scope: Construct, id: string) {
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
        this.bucket = new s3.Bucket(this, 'Bucket', {
            bucketName: 'media-store-' + Aws.ACCOUNT_ID,
            intelligentTieringConfigurations,
        });
    }
}
