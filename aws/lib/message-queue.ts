import { Construct } from 'constructs';
import { Duration, aws_sqs as sqs } from 'aws-cdk-lib';

export class MessageQueue extends Construct {
    readonly streamQueue: sqs.Queue;
    readonly audiogenQueue: sqs.Queue;

    constructor(scope: Construct, id: string) {
        super(scope, id);

        this.streamQueue = new sqs.Queue(this, 'StreamQueue', {
            queueName: 'stream-shows.fifo',
            fifo: true,
            receiveMessageWaitTime: Duration.seconds(5),
            visibilityTimeout: Duration.seconds(60 * 10),
        });

        this.audiogenQueue = new sqs.Queue(this, 'AudioGenQueue', {
            queueName: 'audio-gen.fifo',
            fifo: true,
            receiveMessageWaitTime: Duration.seconds(5),
            visibilityTimeout: Duration.seconds(60 * 10),
        });
    }
}
