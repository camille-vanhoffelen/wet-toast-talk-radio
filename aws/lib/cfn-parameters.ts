import { CfnParameter } from 'aws-cdk-lib';
import { Construct } from 'constructs';

export class CfnParameters {
    readonly ecrRepositoryName: CfnParameter;
    readonly ecrGpuRepositoryName: CfnParameter;
    readonly imageTag: CfnParameter;

    readonly transcoderInstanceType: CfnParameter;
    readonly playlistInstanceType: CfnParameter;
    readonly shoutClientInstanceType: CfnParameter;

    readonly scriptWriterInstanceType: CfnParameter;
    readonly audioGeneratorInstanceType: CfnParameter;

    constructor(scope: Construct) {
        this.ecrRepositoryName = new CfnParameter(scope, 'ECRRepositoryName', {
            type: 'String',
            default: 'wet-toast-talk-radio',
            description: 'The ecr repository name for the docker images',
        });
        this.ecrRepositoryName.overrideLogicalId('ECRRepositoryName');

        this.ecrGpuRepositoryName = new CfnParameter(scope, 'ECRGpuRepositoryName', {
            type: 'String',
            default: 'wet-toast-talk-radio-gpu',
            description: 'The ecr repository name for the gpu docker images',
        });
        this.ecrGpuRepositoryName.overrideLogicalId('ECRGpuRepositoryName');

        this.imageTag = new CfnParameter(scope, 'ImageTag', {
            type: 'String',
            default: 'latest',
            description: 'image tag for the docker images',
        });
        this.imageTag.overrideLogicalId('ImageTag');

        this.transcoderInstanceType = new CfnParameter(scope, 'TranscoderInstanceType', {
            type: 'String',
            default: 't3.medium',
            description: 'The instance type for the trancoder task',
        });
        this.transcoderInstanceType.overrideLogicalId('TranscoderInstanceType');

        this.playlistInstanceType = new CfnParameter(scope, 'PlaylistInstanceType', {
            type: 'String',
            default: 't2.micro',
            description: 'The instance type for the playlist task',
        });
        this.playlistInstanceType.overrideLogicalId('PlaylistInstanceType');

        this.shoutClientInstanceType = new CfnParameter(scope, 'ShoutClientInstanceType', {
            type: 'String',
            default: 't3.small',
            description: 'The instance type for the shout-client task',
        });
        this.shoutClientInstanceType.overrideLogicalId('ShoutClientInstanceType');

        this.scriptWriterInstanceType = new CfnParameter(scope, 'ScriptWriterInstance', {
            type: 'String',
            default: 't2.micro',
            description: 'The instance type for the scriptwriter task',
        });
        this.scriptWriterInstanceType.overrideLogicalId('ScriptWriterInstance');

        this.audioGeneratorInstanceType = new CfnParameter(scope, 'AudioGeneratorInstance', {
            type: 'String',
            // TODO: Change to correct type
            default: 't2.micro',
            description: 'The instance type for the audio generator task',
        });
    }
}