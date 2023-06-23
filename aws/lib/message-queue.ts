import { Construct } from 'constructs';
import { Duration, aws_sqs as sqs } from 'aws-cdk-lib';

export class MessageQueue extends Construct {
    readonly streamQueue: sqs.Queue;
    readonly scriptQueue: sqs.Queue;

    constructor(scope: Construct, id: string) {
        super(scope, id);

        this.streamQueue = new sqs.Queue(this, 'StreamQueue', {
            queueName: 'stream-shows.fifo',
            fifo: true,
            contentBasedDeduplication: true,
            receiveMessageWaitTime: Duration.seconds(5),
            visibilityTimeout: Duration.seconds(60 * 10),
        });

        this.scriptQueue = new sqs.Queue(this, 'ScriptQueue', {
            queueName: 'script-shows.fifo',
            fifo: true,
            contentBasedDeduplication: true,
            receiveMessageWaitTime: Duration.seconds(5),
            visibilityTimeout: Duration.seconds(60 * 10),
        });
    }
}
