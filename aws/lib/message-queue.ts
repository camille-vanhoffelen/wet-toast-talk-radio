import { Construct } from 'constructs';
import { Duration, aws_sqs as sqs, aws_iam as iam } from 'aws-cdk-lib';
import { resourceName } from './resource-name';

export class MessageQueue extends Construct {
    readonly streamQueue: sqs.Queue;
    readonly scriptQueue: sqs.Queue;

    constructor(scope: Construct, id: string, dev = false) {
        super(scope, id);

        const streamQueueName = resourceName('stream-shows', dev) + '.fifo';
        const scriptQueueName = resourceName('script-shows', dev) + '.fifo';

        this.streamQueue = new sqs.Queue(this, 'StreamQueue', {
            queueName: streamQueueName,
            fifo: true,
            contentBasedDeduplication: true,
            receiveMessageWaitTime: Duration.seconds(5),
            visibilityTimeout: Duration.seconds(60 * 10),
        });

        this.scriptQueue = new sqs.Queue(this, 'ScriptQueue', {
            queueName: scriptQueueName,
            fifo: true,
            contentBasedDeduplication: true,
            receiveMessageWaitTime: Duration.seconds(5),
            visibilityTimeout: Duration.seconds(60 * 10),
            retentionPeriod: Duration.seconds(60 * 60 * 24 * 10),
        });
    }

    grantConsumeMessages(grantee: iam.IGrantable) {
        this.streamQueue.grantConsumeMessages(grantee);
        this.scriptQueue.grantConsumeMessages(grantee);
    }

    grantSendMessages(grantee: iam.IGrantable) {
        this.streamQueue.grantSendMessages(grantee);
        this.scriptQueue.grantSendMessages(grantee);
    }

    grantPurge(grantee: iam.IGrantable) {
        this.streamQueue.grantPurge(grantee);
        this.scriptQueue.grantPurge(grantee);
    }

    envVars(): { [key: string]: string } {
        return {
            WT_MESSAGE_QUEUE__SQS__SCRIPT_QUEUE_NAME: this.scriptQueue.queueName,
            WT_MESSAGE_QUEUE__SQS__STREAM_QUEUE_NAME: this.streamQueue.queueName,
        };
    }
}
