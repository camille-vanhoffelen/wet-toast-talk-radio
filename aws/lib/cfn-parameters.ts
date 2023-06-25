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

    readonly emergencyAlertSystemUrl: CfnParameter;
    readonly radioOperatorUrl: CfnParameter;

    readonly voscastPassword: CfnParameter;
    readonly voscastHostname: CfnParameter;
    readonly voscastPort: CfnParameter;
    readonly voscastAutoDjKey: CfnParameter;

    readonly openApiKey: CfnParameter;

    constructor(scope: Construct) {
        this.ecrRepositoryName = new CfnParameter(scope, 'ECRRepositoryName', {
            type: 'String',
            default: 'wet-toast-talk-radio',
            description: 'The ecr repository name for the docker images',
        });
        this.ecrRepositoryName.overrideLogicalId('EcrRepositoryName');

        this.ecrGpuRepositoryName = new CfnParameter(scope, 'ECRGpuRepositoryName', {
            type: 'String',
            default: 'wet-toast-talk-radio-gpu',
            description: 'The ecr repository name for the gpu docker images',
        });
        this.ecrGpuRepositoryName.overrideLogicalId('EcrGpuRepositoryName');

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
            default: 'g4dn.xlarge',
            description: 'The instance type for the audio generator task',
        });

        this.emergencyAlertSystemUrl = new CfnParameter(scope, 'EmergencyAlertSystemUrl', {
            type: 'String',
            default: 'sm:/wet-toast-talk-show/emergency-alert-system/slack-web-hook-url',
            description: 'The slack url for the emergency alert system',
        });

        this.radioOperatorUrl = new CfnParameter(scope, 'RadioOperatorUrl', {
            type: 'String',
            default: 'sm:/wet-toast-talk-show/radio-operator/slack-web-hook-url',
            description: 'The slack url for the radio operator',
        });

        this.voscastPassword = new CfnParameter(scope, 'VoscastPassword', {
            type: 'String',
            default: 'sm:/wet-toast-talk-radio/voscast-password',
            description: 'The password for the voscast server',
        });

        this.voscastHostname = new CfnParameter(scope, 'VoscastHostname', {
            type: 'String',
            default: 's3.voscast.com',
            description: 'The hostname for the voscast server',
        });

        this.voscastPort = new CfnParameter(scope, 'VoscastPort', {
            type: 'String',
            default: '11053',
            description: 'The port for the voscast server',
        });

        this.voscastAutoDjKey = new CfnParameter(scope, 'VoscastAutoDjKey', {
            type: 'String',
            default: 'sm:/wet-toast-talk-radio/voscast-autodj-key',
            description: 'The auto dj key for the voscast server',
        });

        this.openApiKey = new CfnParameter(scope, 'OpenApiKey', {
            type: 'String',
            default: 'sm:/wet-toast-talk-radio/scriptwriter/openai-api-key',
            description: 'The open api key for the script writer',
        });
    }
}
