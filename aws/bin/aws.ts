#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { WetToastTalkShowStack } from '../lib/wet-toast-talk-show-stack';

const app = new cdk.App();
new WetToastTalkShowStack(app, 'WetToastTalkShowStack', {
    stackName: app.node.tryGetContext('stack-name'),
    env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
});
