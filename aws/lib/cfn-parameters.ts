import { CfnParameter } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export class CfnParameters {
    readonly ecrRepositoryName: CfnParameter;
    readonly transcoderInstanceType: CfnParameter;
    readonly imageTag: CfnParameter;

    constructor(scope: Construct) {
        this.ecrRepositoryName = new CfnParameter(scope, 'ECRRepositoryName', {
            type: 'String',
            default: 'wet-toast-talk-radio',
            description: 'The ecr repository name for the docker images',
        });
        this.ecrRepositoryName.overrideLogicalId('ECRRepositoryName');

        this.imageTag = new CfnParameter(scope, 'ImageTag', {
            type: 'String',
            default: 'latest',
            description: 'image tag for the docker images',
        });
        this.imageTag.overrideLogicalId('ImageTag');

        this.transcoderInstanceType = new CfnParameter(scope, 'TranscoderInstanceType', {
            type: 'String',
            default: 'm5.large',
            description: 'The instance type for the trancoder task',
        });
        this.transcoderInstanceType.overrideLogicalId('TranscoderInstanceType');
    }
}
