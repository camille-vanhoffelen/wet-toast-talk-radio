import { Construct } from 'constructs';
import { aws_s3 as s3, Duration } from 'aws-cdk-lib';

export class WetToastBucket extends Construct {
    readonly bucket: s3.Bucket;
    constructor(scope: Construct, id: string) {
        super(scope, id);

        let intelligentTieringConfigurations = [];
        for (const prefix of ['raw', 'transcoded', 'script']) {
            intelligentTieringConfigurations.push({
                name: prefix,
                prefix: `${prefix}/`,
                archiveAccessTierTime: Duration.days(30),
                deepArchiveAccessTierTime: Duration.days(60),
            });
        }
        this.bucket = new s3.Bucket(this, 'Bucket', {
            intelligentTieringConfigurations,
        });
    }
}
