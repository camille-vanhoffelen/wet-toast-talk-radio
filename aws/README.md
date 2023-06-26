# Wet Toast Talk Radio Infrastructure

This directory contains all the infrastructure as code to deploy wet toast talk radio to a aws account.

## Prerequisites

- [nvm](https://github.com/nvm-sh/nvm)

## Getting Started

Make sure you are in the `aws` directory.

Setup node: 

```bash
nvm use
```

Install cdk:

```bash
npm install -g aws-cdk 
```

## Deploying 

Make sure your terminal has assumed the right aws credentials/profile

You can deploy the infrastructure to any account with the following command:

```bash
cdk deploy --all --parameters ImageTag=<SOME_TAG> 
```

You can update any CfnParameter defined at [./lib/cfn-parameters.ts](./lib/cfn-parameters.ts) by adding a `--parameters MyParam=value` to the command above.

You can also go the cloud formation aws console to edit any CfnParameters directly.

### Only dev stack

```
cdk deploy WetToastTalkShowDevStack --parameters ImageTag=<SOME_TAG> 
```

## Useful commands

* `cdk deploy`      deploy this stack to your default AWS account/region
* `cdk diff`        compare deployed stack with current state
* `cdk synth`       emits the synthesized CloudFormation template

## Linting

```bash
npm run lint
```